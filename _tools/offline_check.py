# -*- coding: utf-8 -*-
"""offline_check.py —— 验证两件事：
1) 用户那段第 4 题代码能正常判出 WA（不会卡）
2) 本地服务被杀掉后，点提交会立刻给出中文提示，而不是永远停在「正在判题……」

用法：python _tools/offline_check.py
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_CODE = """#include <stdio.h>

int main(void) {
    int n,m;
    char c;
    scanf("%d %c",&n,&c);

    for(m=0;m<=n;m++)
    {
        printf("%c",c);
    }

    return 0;
}
"""


def start():
    env = dict(os.environ, CSTUDY_PORT="8788")
    return subprocess.Popen([sys.executable, "server.py"], cwd=APP, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def wait_api(port=8788, timeout=30):
    for _ in range(timeout):
        time.sleep(1)
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d/api/data" % port, timeout=3) as r:
                return json.loads(r.read().decode())
        except Exception:
            pass
    return None


ok = True


def check(name, cond, extra=""):
    global ok
    print(("  %-38s %s %s" % (name, "OK" if cond else "!! 失败", extra)).rstrip())
    ok = ok and cond


p = start()
d = wait_api()
if not d:
    print("服务没起来")
    sys.exit(1)
print("服务已启动，OJ 题数", len(d["oj"]))

try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(channel="msedge", headless=True)
        page = b.new_page(viewport={"width": 1300, "height": 950})
        page.goto("http://127.0.0.1:8788/", wait_until="networkidle")
        page.click("text=OJ 刷题")
        page.wait_for_selector(".oj-item")
        page.click(".oj-item >> nth=3")          # 第 4 题
        page.wait_for_timeout(300)
        page.evaluate("(c) => editor.setValue(c)", USER_CODE)
        t0 = time.time()
        page.click("#submit")
        page.wait_for_selector("#result .sub-verdict, #result div", timeout=60000)
        page.wait_for_timeout(800)
        txt = page.inner_text("#result")
        print("判题结果文字:", txt[:120].replace("\n", " "))
        check("用户这段代码正常判出 WA", "WA" in txt, "耗时 %.1fs" % (time.time() - t0))
        check("给出了样例差异", "实际" in page.content() or "期望" in page.content())

        # ---- 杀掉服务，再点一次 ----
        subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
        time.sleep(1)
        t1 = time.time()
        page.click("#submit")
        page.wait_for_timeout(2500)
        txt2 = page.inner_text("#result")
        print("断线提示:", txt2[:120].replace("\n", " "))
        check("服务没了会提示而不是卡死", "判题没有响应" in txt2, "耗时 %.1fs" % (time.time() - t1))
        page.screenshot(path=os.path.join(APP, "_verify", "ui_offline.png"))
        b.close()
finally:
    subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)

print("检查:", "通过" if ok else "有问题")
sys.exit(0 if ok else 1)
