# -*- coding: utf-8 -*-
"""about_log_check.py —— 日志功能的 UI 验收（headless Edge）

跑法：python _tools/about_log_check.py
验证：关于页有「运行日志」卡片 → 点「查看最近日志」能读出内容 →
      页面里的 JS 报错会通过 /api/log 写进同一个日志文件。
截图：_verify/ui_about_log.png
"""
import json
import os
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["CSTUDY_PORT"] = "8799"

import server          # noqa: E402
import applog          # noqa: E402
from playwright.sync_api import sync_playwright   # noqa: E402

server.webbrowser.open = lambda *a, **k: None

PORT = 8799
srv = server.AppServer(("127.0.0.1", PORT), server.Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
time.sleep(0.4)

OUT = os.path.join(ROOT, "_verify")
os.makedirs(OUT, exist_ok=True)
fails = []


def check(name, ok, extra=""):
    print(("  [OK] " if ok else "  [FAIL] ") + name + (("  " + extra) if extra else ""))
    if not ok:
        fails.append(name)


with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    page = b.new_page(viewport={"width": 1320, "height": 1150})
    page.goto("http://127.0.0.1:%d/" % PORT, wait_until="networkidle")
    page.wait_for_selector(".lesson-item")

    print("1) 打开「关于」页")
    page.click(".nav-item >> text=关于")
    page.wait_for_selector("#showlog")
    check("有「查看最近日志」按钮", page.is_visible("#showlog"))
    check("有「打开日志文件夹」按钮", page.is_visible("#openlog"))
    check("显示了日志目录", "logs" in (page.text_content("#loghint") or ""))

    print("2) 点开日志")
    page.click("#showlog")
    page.wait_for_function("""() => {
        const b = document.querySelector('#logbox');
        return b && b.style.display !== 'none' && !b.textContent.includes('读取中');
    }""", timeout=10000)
    text = page.text_content("#logbox") or ""
    check("日志内容非空", len(text) > 50, "%d 字符" % len(text))
    check("含启动记录", "启动 C 语言学习器" in text)
    check("含请求记录", "GET /api/data" in text)
    page.screenshot(path=os.path.join(OUT, "ui_about_log.png"), full_page=True)

    print("3) 页面 JS 报错会写进日志")
    before = len(applog.tail(500))
    page.evaluate("() => { setTimeout(() => { throw new Error('自检：故意抛的错'); }, 0); }")
    page.wait_for_timeout(800)
    lines = applog.tail(500)
    joined = "\n".join(lines[before:] if len(lines) > before else lines)
    check("JS 未捕获异常被后端记下", "[前端:web]" in joined, )
    check("异常内容正确", "故意抛的错" in joined)

    print("4) 未处理的 Promise 拒绝也会记")
    page.evaluate("() => { Promise.reject(new Error('自检：rejected')); }")
    page.wait_for_timeout(800)
    check("unhandledrejection 被记下", "自检：rejected" in "\n".join(applog.tail(500)))

    b.close()

srv.shutdown()
print("\n截图：%s" % os.path.join(OUT, "ui_about_log.png"))
print("自检结果：", "全部通过" if not fails else "失败 %d 项 → %s" % (len(fails), fails))
sys.exit(0 if not fails else 1)
