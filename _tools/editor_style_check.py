# -*- coding: utf-8 -*-
"""editor_style_check.py —— 检查 OJ 代码输入框的实际配色"""
import os

from playwright.sync_api import sync_playwright

APP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(APP, "_verify")

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    page = b.new_page(viewport={"width": 1300, "height": 950})
    page.goto("http://127.0.0.1:8765/", wait_until="networkidle")
    page.click("text=OJ 刷题")
    page.wait_for_selector(".oj-item")
    page.click(".oj-item >> nth=3")
    page.wait_for_timeout(600)
    page.evaluate("""() => editor.setValue(
      '#include <stdio.h>\\n\\nint main(void) {\\n    int n;\\n    // 测试高亮\\n    scanf(\\"%d\\", &n);\\n    printf(\\"%d\\\\n\\", n * 2);\\n    return 0;\\n}\\n')""")
    page.wait_for_timeout(400)
    res = page.evaluate(
        """() => {
            const q = (sel) => {
                const el = document.querySelector(sel);
                if (!el) return "缺少 " + sel;
                const cs = getComputedStyle(el);
                return cs.backgroundColor + " / 文字 " + cs.color;
            };
            return {
              wrapper: q("#editor"),
              cm: q(".CodeMirror"),
              scroll: q(".CodeMirror-scroll"),
              gutters: q(".CodeMirror-gutters"),
              code: q(".CodeMirror-code"),
              lines: q(".CodeMirror-line"),
              textarea: q(".CodeMirror textarea"),
              keyword: q(".CodeMirror .cm-keyword"),
              string: q(".CodeMirror .cm-string"),
              comment: q(".CodeMirror .cm-comment"),
              sampleCard: q(".lesson-detail .code-body"),
            };
        }"""
    )
    for k, v in res.items():
        print("%-11s %s" % (k, v))
    page.screenshot(path=os.path.join(OUT, "editor_now.png"))
    page.screenshot(path=os.path.join(OUT, "editor_dark.png"), clip={"x": 280, "y": 60, "width": 1000, "height": 700})
    b.close()
