# -*- coding: utf-8 -*-
"""ojmenu_check.py —— 验证 OJ 选题菜单：分组、固定不滚动、换题回到顶部"""
import os
import subprocess
import sys
import time
import json
import urllib.request

from playwright.sync_api import sync_playwright

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8792


def wait_api():
    for _ in range(30):
        time.sleep(1)
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d/api/data" % PORT, timeout=3) as r:
                return json.loads(r.read().decode())
        except Exception:
            pass
    return None


ok = True


def check(name, cond, extra=""):
    global ok
    print(("  %-34s %s %s" % (name, "OK" if cond else "!! 失败", extra)).rstrip())
    ok = ok and cond


env = dict(os.environ, CSTUDY_PORT=str(PORT))
p = subprocess.Popen([sys.executable, "server.py"], cwd=APP, env=env,
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
d = wait_api()
if not d:
    print("服务没起来")
    sys.exit(1)

try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(channel="msedge", headless=True)
        page = b.new_page(viewport={"width": 1300, "height": 620})
        page.goto("http://127.0.0.1:%d/" % PORT, wait_until="networkidle")
        page.click("text=OJ 刷题")
        page.wait_for_selector(".oj-menu")

        groups = page.query_selector_all(".oj-group")
        names = [g.query_selector(".g-name").inner_text() for g in groups]
        print("分组:", names)
        check("按难度分成三组", names == ["入门", "基础", "进阶"])
        total = len(page.query_selector_all("[data-pid]"))
        check("题目总数 36", total == 36, "实际 %d" % total)

        # 打开一道长题（第 33 题，描述+样例较长），把右侧滚到底
        page.click("[data-pid='33']")
        page.wait_for_timeout(400)
        box_before = page.query_selector(".oj-menu").bounding_box()
        page.eval_on_selector("#content", "el => el.scrollTop = el.scrollHeight")
        page.wait_for_timeout(400)
        box_after = page.query_selector(".oj-menu").bounding_box()
        scrolled = page.eval_on_selector("#content", "el => el.scrollTop")
        pos = page.eval_on_selector(".oj-menu", "el => getComputedStyle(el).position")
        print("滚动距离:", scrolled, "| 菜单 y:", round(box_before["y"]), "->", round(box_after["y"]), "| position:", pos)
        check("内容确实滚动了", scrolled > 200)
        check("菜单是 sticky", pos == "sticky")
        # 静态元素会被滚出视野（y 变成负数）；sticky 会停在顶部附近
        check("滚动后菜单仍贴在顶部", 0 <= box_after["y"] <= 40, "y=%d" % round(box_after["y"]))
        visible = page.eval_on_selector(".oj-menu", """el => {
            const r = el.getBoundingClientRect();
            return r.top >= -1 && r.bottom <= window.innerHeight + 1;
        }""")
        check("菜单仍在可视区", visible)

        # 关键：菜单自己必须能滚，而且能滚到最后一道题
        m = page.evaluate("""() => {
            const el = document.querySelector(".oj-menu");
            return {scrollH: el.scrollHeight, clientH: el.clientHeight};
        }""")
        print("菜单 scrollHeight=%d clientHeight=%d" % (m["scrollH"], m["clientH"]))
        check("菜单内部可滚动", m["scrollH"] > m["clientH"] + 20)
        page.eval_on_selector(".oj-menu", "el => el.scrollTop = el.scrollHeight")
        page.wait_for_timeout(300)
        last = page.evaluate("""() => {
            const el = document.querySelector("[data-pid='36']");
            const r = el.getBoundingClientRect();
            const m = document.querySelector(".oj-menu").getBoundingClientRect();
            return {top: Math.round(r.top), bottom: Math.round(r.bottom),
                    menuBottom: Math.round(m.bottom), vh: window.innerHeight};
        }""")
        print("滚到底后第 36 题位置:", last)
        check("能滚到最后一道题", last["bottom"] <= last["menuBottom"] + 1 and last["bottom"] <= last["vh"])

        # 分组不能被 flex 压扁
        gh = page.evaluate("""() => [...document.querySelectorAll(".oj-group")].map(g => ({
            h: Math.round(g.getBoundingClientRect().height),
            n: g.querySelectorAll(".oj-item").length
        }))""")
        print("分组高度:", gh)
        check("每组高度容得下所有题目", all(g["h"] >= g["n"] * 30 + 40 for g in gh))
        page.eval_on_selector(".oj-menu", "el => el.scrollTop = 0")

        # 换题：应回到题目顶部
        page.click("[data-pid='4']")
        page.wait_for_timeout(400)
        top = page.eval_on_selector("#content", "el => el.scrollTop")
        title = page.inner_text("#ojdetail h2")
        check("换题后回到顶部", top == 0, "scrollTop=%d" % top)
        check("题目切换正确", title.startswith("4."), title[:24])

        # 分组可折叠
        page.click(".oj-group >> nth=0 >> summary")
        page.wait_for_timeout(250)
        collapsed = page.eval_on_selector(".oj-group", "el => !el.open")
        check("分组能折叠", bool(collapsed))

        page.screenshot(path=os.path.join(APP, "_verify", "ui_ojmenu.png"))
        b.close()
finally:
    subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)

print("菜单检查:", "通过" if ok else "有问题")
sys.exit(0 if ok else 1)
