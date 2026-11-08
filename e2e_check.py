# -*- coding: utf-8 -*-
"""e2e_check.py —— 端到端检查（需要先启动 server.py）

1) HTTP：/api/data 里 27 道 OJ 都带 reference / best
2) HTTP：POST /api/judge 用参考答案 → AC；用错误答案 → WA（抽 4 道题）
3) 浏览器：OJ 页 27 条、点第 27 题出现「第 27 块」、编辑器就位
跑完记得 python e2e_check.py --clean 清理测试留下的 problem_*.c 和进度
"""
import json
import os
import sys
import urllib.request

APP = os.path.dirname(os.path.abspath(__file__))
OJ_DIR = os.path.join(APP, "oj")
BASE = "http://127.0.0.1:8765"
WRONG = '#include <stdio.h>\nint main(void){printf("999999\\n");return 0;}\n'


def api(path, payload=None):
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data,
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def clean():
    removed = []
    if os.path.isdir(OJ_DIR):
        for name in os.listdir(OJ_DIR):
            if name.startswith("problem_") and name.endswith(".c"):
                os.remove(os.path.join(OJ_DIR, name))
                removed.append(name)
    pf = os.path.join(APP, "progress.json")
    if os.path.exists(pf):
        p = json.load(open(pf, encoding="utf-8"))
        p["oj"] = {}
        p["submissions"] = []
        json.dump(p, open(pf, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("清理 %d 个测试文件：%s" % (len(removed), removed))


def http_checks():
    d = api("/api/data")
    oj = d["oj"]
    print("OJ 题数:", len(oj))
    assert len(oj) == 36, "题数不是 36"
    missing = [p["id"] for p in oj if not p["reference"] or not p["best"]]
    assert not missing, "缺参考答案：%s" % missing

    for pid in (1, 13, 26, 27, 33, 36):
        ans = next(p for p in oj if p["id"] == pid)
        r = api("/api/judge", {"id": pid, "code": ans["reference"]})
        print("第 %2d 题 reference → %s" % (pid, r["verdict"]))
        assert r["verdict"] == "AC", "第 %d 题参考答案没 AC" % pid

        r = api("/api/judge", {"id": pid, "code": ans["best"]})
        print("第 %2d 题 best      → %s" % (pid, r["verdict"]))
        assert r["verdict"] == "AC"

        r = api("/api/judge", {"id": pid, "code": WRONG})
        print("第 %2d 题 错误答案   → %s" % (pid, r["verdict"]))
        assert r["verdict"] == "WA"


def ui_checks():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge", headless=True)
        page = b.new_page(viewport={"width": 1300, "height": 950})
        page.goto(BASE, wait_until="networkidle")
        page.click("text=OJ 刷题")
        page.wait_for_selector(".oj-item")
        items = page.query_selector_all(".oj-item")
        print("OJ 列表条数:", len(items))
        assert len(items) == 36

        items[-1].click()
        page.wait_for_timeout(600)
        text = page.inner_text("#ojdetail")
        assert "第 36 块" in text, "详情没显示知识块"
        assert "标准库综合" in text
        has_editor = page.query_selector(".CodeMirror") is not None
        print("编辑器就位:", has_editor)
        page.screenshot(path=os.path.join(APP, "_verify", "ui_oj27.png"))
        b.close()


if "--clean" in sys.argv:
    clean()
    sys.exit(0)

http_checks()
ui_checks()
print("端到端检查通过")
