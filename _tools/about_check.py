# -*- coding: utf-8 -*-
"""about_check.py —— 验证 favicon / 关于页 / 版本号

1) /icon.ico 能取到且是 ico
2) 页面 <link rel=icon> 指向 icon.ico，浏览器标题带版本号
3) 「关于」页有作者信息、vibe coding 说明、版本 1.0.1
4) 开发/便携版不显示卸载按钮，安装版显示（用 /api/about 判断）
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP)
import appinfo          # noqa: E402
VER = appinfo.VERSION
PORT = 8795
ok = True


def check(name, cond, extra=""):
    global ok
    print(("  %-32s %s %s" % (name, "OK" if cond else "!! 失败", extra)).rstrip())
    ok = ok and cond


env = dict(os.environ, CSTUDY_PORT=str(PORT))
p = subprocess.Popen([sys.executable, "server.py"], cwd=APP, env=env,
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
for _ in range(30):
    time.sleep(1)
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/api/data" % PORT, timeout=3) as r:
            data = json.loads(r.read().decode())
        break
    except Exception:
        data = None

try:
    check("服务启动", data is not None)
    app = (data or {}).get("app", {})
    print("app 元信息:", {k: app.get(k) for k in ("name", "version", "build", "frozen")})
    check("版本号是 %s" % VER, app.get("version") == VER, app.get("version", ""))
    check("开发版没有卸载器", app.get("uninstaller") == "")

    req = urllib.request.Request("http://127.0.0.1:%d/icon.ico" % PORT)
    with urllib.request.urlopen(req, timeout=10) as r:
        ico = r.read()
        ctype = r.headers.get("Content-Type")
    check("/icon.ico 可取", len(ico) > 5000, "%d 字节, %s" % (len(ico), ctype))
    check("返回 ico 类型", "icon" in (ctype or "").lower())

    check("favicon 可取（/favicon.ico）",
          urllib.request.urlopen("http://127.0.0.1:%d/favicon.ico" % PORT, timeout=10).status == 200)

    with sync_playwright() as pw:
        b = pw.chromium.launch(channel="msedge", headless=True)
        page = b.new_page(viewport={"width": 1300, "height": 950})
        page.goto("http://127.0.0.1:%d/" % PORT, wait_until="networkidle")
        page.wait_for_timeout(600)
        title = page.title()
        print("页面标题:", title)
        check("标题带版本号", VER in title)
        href = page.eval_on_selector("link[rel='icon']", "el => el.getAttribute('href')")
        check("link[rel=icon] 指向 icon.ico", href == "icon.ico", href)
        fav = page.evaluate("""async () => {
            const r = await fetch("/icon.ico"); return r.status;
        }""")
        check("页面能拿到 favicon", fav == 200)

        page.click("text=关于")
        page.wait_for_timeout(500)
        txt = page.inner_text("#content")
        for kw in ("Naireip", "1302212726", "vibe coding", "v" + VER, "MinGW"):
            check("关于页含「%s」" % kw, kw in txt)
        for bad in ("滕州", "准大一", "2432775691", "无需安装", "学校"):
            check("关于页不含「%s」" % bad, bad not in txt)
        check("开发版不显示卸载按钮", page.query_selector("#uninstall") is None)
        page.screenshot(path=os.path.join(APP, "_verify", "ui_about.png"))
        b.close()
finally:
    subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)

print("关于页检查:", "通过" if ok else "有问题")
sys.exit(0 if ok else 1)
