# -*- coding: utf-8 -*-
"""ui_check.py —— 用 Playwright 打开 http://127.0.0.1:8765/ ，验证渲染
课程：27 条，点开第 11 块出现「要点清单」/教材行/示例代码
OJ：27 条，点最后一题显示「第 27 块」与样例，编辑器就位
产出：_verify/ui_lesson11.png、_verify/ui_oj27.png
只读检查，不提交代码，不会写 progress.json
"""
import os
import sys

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_verify")
os.makedirs(OUT, exist_ok=True)


def main():
    ok = True
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge", headless=True)
        page = b.new_page(viewport={"width": 1280, "height": 1000})
        page.goto(URL, wait_until="networkidle")

        # ---- 课程 ----
        page.wait_for_selector(".lesson-item")
        items = page.query_selector_all(".lesson-item")
        print("课程列表条数:", len(items))
        ok &= len(items) == 36
        items[10].click()
        page.wait_for_timeout(400)
        detail = page.query_selector(".lesson-detail[data-detail='10']")
        heads = [h.inner_text() for h in detail.query_selector_all(".sec-head")]
        lis = detail.query_selector_all(".points li")
        ref = detail.query_selector(".lesson-ref").inner_text()
        pre = detail.query_selector(".code-body").inner_text()
        print("小节标题:", heads)
        print("要点条数:", len(lis), "| 教材行:", ref, "| 示例代码行数:", pre.count("\n") + 1)
        ok &= len(lis) >= 4 and "第 11 块" in ref
        page.screenshot(path=os.path.join(OUT, "ui_lesson11.png"))

        # ---- OJ ----
        page.click("text=OJ 刷题")
        page.wait_for_selector(".oj-item")
        ojs = page.query_selector_all(".oj-item")
        print("OJ 列表条数:", len(ojs))
        ok &= len(ojs) == 36
        ojs[-1].click()
        page.wait_for_timeout(600)
        text = page.inner_text("#ojdetail")
        has_editor = page.query_selector(".CodeMirror") is not None
        print("题目详情含「第 36 块」:", "第 36 块" in text, "| 编辑器:", has_editor)
        ok &= ("第 36 块" in text) and has_editor and ("样例" in text)
        page.screenshot(path=os.path.join(OUT, "ui_oj27.png"))
        b.close()

    print("UI 检查:", "通过" if ok else "有问题")
    sys.exit(0 if ok else 1)


main()
