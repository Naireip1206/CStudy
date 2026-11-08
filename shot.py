# -*- coding: utf-8 -*-
"""shot.py —— 给高亮效果拍图：课程详情（含代码块 + 正文）/ 测验题"""
import os

from playwright.sync_api import sync_playwright

APP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(APP, "_verify")

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    page = b.new_page(viewport={"width": 1320, "height": 1250})
    page.goto("http://127.0.0.1:8765/", wait_until="networkidle")
    page.wait_for_selector(".lesson-item")

    items = page.query_selector_all(".lesson-item")
    items[27].click()          # 第 28 块：文件基础（正文有 FILE/fopen/EOF）
    page.wait_for_timeout(600)
    page.screenshot(path=os.path.join(OUT, "ui_highlight_lesson.png"))

    page.click("text=测验")
    page.wait_for_selector(".lesson-item")
    page.click(".lesson-item >> nth=2")     # 第 3 块：运算符
    page.wait_for_timeout(500)
    page.screenshot(path=os.path.join(OUT, "ui_highlight_quiz.png"))
    b.close()
print("截图完成")
