# -*- coding: utf-8 -*-
"""log_check.py —— 日志功能自检

跑法：python _tools/log_check.py
它会：起一个临时端口的服务 → 发真实请求（正常/编译错误/404/前端上报）→
      检查日志文件里有没有对应记录 → 打印最后几十行。
不会碰 8765 上正在跑的那个服务。
"""
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["CSTUDY_PORT"] = "8799"

import server          # noqa: E402
import applog          # noqa: E402

server.webbrowser.open = lambda *a, **k: None      # 自检时别弹浏览器

PORT = 8799
srv = server.AppServer(("127.0.0.1", PORT), server.Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
time.sleep(0.3)

BASE = "http://127.0.0.1:%d" % PORT
fails = []


def check(name, ok, extra=""):
    print(("  [OK] " if ok else "  [FAIL] ") + name + (("  " + extra) if extra else ""))
    if not ok:
        fails.append(name)


def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=20) as r:
            return r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def post(path, obj=None, raw=None):
    data = raw if raw is not None else json.dumps(obj or {}).encode()
    req = urllib.request.Request(BASE + path, data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


print("1) 正常请求")
code, body = get("/api/data")
data = json.loads(body) if code == 200 else {}
check("GET /api/data 返回 200", code == 200)
check("数据里有 OJ 题", len(data.get("oj", [])) > 0, "%d 题" % len(data.get("oj", [])))

print("2) 判题：正确代码 → AC")
prob = next(x for x in data["oj"] if x["id"] == 1)
code, body = post("/api/judge", {"id": 1, "code": prob["reference"]})
r = json.loads(body)
check("判题返回 AC", r.get("verdict") == "AC", r.get("verdict", ""))

print("3) 判题：坏代码 → CE（并应写 WARNING）")
code, body = post("/api/judge", {"id": 1, "code": "int main(void){ return 0 }"})
r = json.loads(body)
check("判题返回 CE", r.get("verdict") == "CE", r.get("verdict", ""))

print("4) 前端错误上报")
code, body = post("/api/log", {"level": "ERROR", "source": "selfcheck",
                               "message": "自检上报：页面点了判题没反应",
                               "stack": "TypeError: x is undefined\n    at submitJudge (app.js:1:1)",
                               "where": "app.js:480"})
check("POST /api/log 成功", code == 200 and json.loads(body).get("ok") is True)

print("5) 404 也应留痕")
code, body = get("/nope")
check("GET /nope 返回 404", code == 404)

print("6) 读日志接口")
code, body = get("/api/logs?n=50")
r = json.loads(body)
check("GET /api/logs 返回 200", code == 200)
check("返回了日志行", len(r.get("lines", [])) > 0, "%d 行" % len(r.get("lines", [])))
check("日志路径指向 logs 目录", "logs" in (r.get("path") or ""), r.get("path", ""))

print("7) 日志内容检查")
text = "\n".join(applog.tail(400))
check("记录了启动信息", "启动 C 语言学习器" in text)
check("记录了 gcc 路径", "编译器=" in text)
check("记录了请求与耗时", "GET /api/data -> 200" in text)
check("记录了判题 AC", "→ AC" in text)
check("记录了编译失败", "判定 CE" in text)
check("记录了前端上报", "[前端:selfcheck]" in text)
check("记录了 404", "/nope -> 404" in text)

print("8) 坏进度文件不会让程序崩")
server.PROGRESS_FILE = os.path.join(os.environ["TEMP"], "cstudy_bad_progress.json")
with open(server.PROGRESS_FILE, "w", encoding="utf-8") as f:
    f.write("{ this is not json ")
server.load_progress()
check("坏文件被备份", any(n.startswith("cstudy_bad_progress.json.broken-")
                        for n in os.listdir(os.environ["TEMP"])))
check("坏文件后仍能启动", isinstance(server.progress, dict))

print("\n===== 日志文件最后 40 行：%s =====" % applog.LOG_FILE)
for line in applog.tail(40):
    print(line)

srv.shutdown()
print("\n自检结果：", "全部通过" if not fails else "失败 %d 项 → %s" % (len(fails), fails))
sys.exit(0 if not fails else 1)
