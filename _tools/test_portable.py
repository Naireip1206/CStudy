# -*- coding: utf-8 -*-
"""test_portable.py —— 便携版验收：精简版无编译器、双开端口顺延、页面渲染

用法：python _tools/test_portable.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = os.path.join(APP, "release", "C语言学习器-完整版")
EXE = os.path.join(REL, "C语言学习器.exe")
LITE_DIR = os.path.join(tempfile.gettempdir(), "cstudy_lite")
LITE_EXE = os.path.join(LITE_DIR, "C语言学习器.exe")
# 数据目录隔离到临时目录：这个脚本会判题、写 AC 留档，
# 绝不能落在用户真实的 %LOCALAPPDATA%\CStudy 里（更不能 rmtree 它）。
TEST_DATA = os.path.join(tempfile.gettempdir(), "cstudy_portable_test", "_userdata")


def wait_api(port, timeout=40):
    for _ in range(timeout):
        time.sleep(1)
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d/api/data" % port, timeout=3) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            pass
    return None


def judge(port, pid, code):
    body = json.dumps({"id": pid, "code": code}).encode()
    req = urllib.request.Request("http://127.0.0.1:%d/api/judge" % port, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def run(exe, workdir, port, extra_env=None):
    env = dict(os.environ)
    env["CSTUDY_PORT"] = str(port)
    env["CSTUDY_DATA"] = TEST_DATA
    if extra_env:
        env.update(extra_env)
    return subprocess.Popen([exe], cwd=workdir, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def stop(p):
    # 只杀这一棵进程树（单文件 exe 会派生子进程），别误伤同名的另一个实例
    subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
    time.sleep(0.5)


ok = True


def check(name, cond, extra=""):
    global ok
    print(("  %-30s %s %s" % (name, "OK" if cond else "!! 失败", extra)).rstrip())
    ok = ok and cond


# ---------------- 1) 精简版（没有 compiler 文件夹） ----------------
print("[1] 精简版：无编译器")
shutil.rmtree(LITE_DIR, ignore_errors=True)
os.makedirs(LITE_DIR, exist_ok=True)
lite_src = os.path.join(APP, "release", "C语言学习器-精简版.exe")
shutil.copy2(lite_src, LITE_EXE)

# 用 CSTUDY_GCC_DISABLE 假装这台机器没装 gcc（否则会用到 D:\w64devkit）
p = run(LITE_EXE, LITE_DIR, 8795, {"CSTUDY_GCC_DISABLE": "1"})
d = wait_api(8795)
check("有 compiler 文件夹时是否误判", d is not None, "(API 起来了)")
if d:
    ref = next(x for x in d["oj"] if x["id"] == 1)["reference"]
    r = judge(8795, 1, ref)
    msg = r.get("message", "")
    check("无编译器时判题为 CE", r["verdict"] == "CE", "| " + msg.splitlines()[0][:40])
    check("提示是中文且友好", "找不到 C 编译器" in msg)
stop(p)

# ---------------- 2) 完整版 + 双开端口顺延 ----------------
print("[2] 完整版：自带编译器 + 双开")
p1 = run(EXE, REL, 8796)
d1 = wait_api(8796)
check("第一个实例 API", d1 is not None)
ref = next(x for x in d1["oj"] if x["id"] == 33)["reference"]
r = judge(8796, 33, ref)
check("自带编译器判第 33 题（大数加法）", r["verdict"] == "AC", "| " + r["verdict"])

p2 = run(EXE, REL, 8796)          # 故意抢同一个端口
d2 = wait_api(8797, timeout=25)   # 应当自动顺延到 8797
check("第二个实例自动换端口", d2 is not None, "(8797 起来了)")
stop(p2)

# ---------------- 3) 页面渲染（Playwright 打真实 exe） ----------------
print("[3] 页面渲染")
try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        b = pw.chromium.launch(channel="msedge", headless=True)
        page = b.new_page(viewport={"width": 1300, "height": 1000})
        page.goto("http://127.0.0.1:8796/", wait_until="networkidle")
        page.wait_for_selector(".lesson-item")
        items = page.query_selector_all(".lesson-item")
        check("课程列表 36 条", len(items) == 36, "实际 %d" % len(items))
        items[10].click()
        page.wait_for_timeout(500)
        detail = page.query_selector(".lesson-detail[data-detail='10']")
        check("代码块有高亮", len(detail.query_selector_all(".code-body .tk-kw")) >= 1)
        check("正文有行内高亮", len(detail.query_selector_all(".points .tok")) >= 3)

        page.click("text=OJ 刷题")
        page.wait_for_selector(".oj-item")
        page.click(".oj-item >> nth=32")   # 第 33 题
        page.wait_for_timeout(300)
        bg = page.evaluate("() => getComputedStyle(document.querySelector('.CodeMirror')).backgroundColor")
        check("代码输入框是深色", bg == "rgb(20, 20, 19)", bg)
        ref33 = page.evaluate("() => DATA.oj.find(p => p.id === 33).reference")
        page.evaluate("(c) => editor.setValue(c)", ref33)
        page.click("#submit")
        page.wait_for_selector("#answers .code-body", timeout=60000)
        check("网页里提交也能 AC 并显示答案", True)

        # AC 留档：文件 + 页面
        ac_file = os.path.join(TEST_DATA, "ac", "problem_33.c")
        check("AC 代码已留档到 ac 目录", os.path.exists(ac_file), ac_file)
        page.click("text=通过代码")
        page.wait_for_timeout(500)
        check("「通过代码」页能看到这道题", "33." in page.inner_text("#content"))
        page.screenshot(path=os.path.join(APP, "_verify", "portable_ui.png"))
        b.close()
except Exception as e:
    check("页面渲染", False, str(e)[:120])

stop(p1)

# ---------------- 4) 清理测试存档（只删临时目录，用户真实数据一律不碰） ----------------
shutil.rmtree(os.path.dirname(TEST_DATA), ignore_errors=True)
shutil.rmtree(LITE_DIR, ignore_errors=True)

print("整体：", "通过" if ok else "有问题")
sys.exit(0 if ok else 1)
