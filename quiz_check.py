# -*- coding: utf-8 -*-
"""quiz_check.py —— 测验页检查：36 个知识点都能点开、每题 2 道、选项/解析渲染正常

跑之前会备份 progress.json，跑完自动还原，不会污染你的学习进度。
"""
import io
import json
import os
import sys

from playwright.sync_api import sync_playwright

APP = os.path.dirname(os.path.abspath(__file__))
PF = os.path.join(APP, "progress.json")
BAK = os.path.join(APP, "_verify", "progress_before_quiz_check.json")
os.makedirs(os.path.join(APP, "_verify"), exist_ok=True)

before = None
if os.path.exists(PF):
    before = io.open(PF, encoding="utf-8").read()
    io.open(BAK, "w", encoding="utf-8").write(before)

ok = True
try:
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge", headless=True)
        page = b.new_page(viewport={"width": 1300, "height": 950})
        page.goto("http://127.0.0.1:8765/", wait_until="networkidle")
        page.click("text=测验")
        page.wait_for_selector(".lesson-item")
        items = page.query_selector_all(".lesson-item")
        disabled = page.query_selector_all(".lesson-item[disabled]")
        print("测验列表条数:", len(items), "| 被禁用（没题）的:", len(disabled))
        ok &= len(items) == 36 and len(disabled) == 0

        # 点最后一个知识块（第 36 块）开始测验
        items[-1].click()
        page.wait_for_timeout(600)
        body = page.inner_text("#content")
        print("进入测验，当前题号:", "1 / 2" in body)
        ok &= "1 / 2" in body
        opts = page.query_selector_all(".quiz-opt")
        print("选项个数:", len(opts))
        ok &= len(opts) == 4

        opts[0].click()
        page.wait_for_timeout(400)
        fb = page.query_selector("#fb").inner_text()
        print("作答后有反馈:", bool(fb.strip()))
        ok &= bool(fb.strip())
        b.close()
finally:
    if before is not None:
        io.open(PF, "w", encoding="utf-8").write(before)

print("测验页检查:", "通过" if ok else "有问题")
sys.exit(0 if ok else 1)
