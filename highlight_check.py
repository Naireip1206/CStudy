# -*- coding: utf-8 -*-
"""highlight_check.py —— 验证语法高亮真的生效且没破坏内容

检查：
1) 课程示例代码：出现 .tk-kw / .tk-fn / .tk-com / .tk-str 等着色 span，且 textContent 与原始代码逐字一致
2) 正文（一句话原理 / 基础知识 / 要点 / 坑）：出现 .tok 行内高亮
3) 测验题干与选项：出现 .tok
4) OJ 描述：出现 .tok；提交正确答案后，参考答案代码块也有着色
跑完清理 progress.json 和 oj/problem_*.c（会备份再还原）
"""
import io
import os
import sys

from playwright.sync_api import sync_playwright

APP = os.path.dirname(os.path.abspath(__file__))
PF = os.path.join(APP, "progress.json")
OJ_DIR = os.path.join(APP, "oj")
before = io.open(PF, encoding="utf-8").read() if os.path.exists(PF) else None

ok = True


def report(name, cond, extra=""):
    global ok
    print(("  %-28s %s %s" % (name, "OK" if cond else "!! 失败", extra)).rstrip())
    ok = ok and cond


try:
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge", headless=True)
        page = b.new_page(viewport={"width": 1300, "height": 1100})
        page.goto("http://127.0.0.1:8765/", wait_until="networkidle")
        page.wait_for_selector(".lesson-item")

        # ---------- 1) 课程代码块 ----------
        items = page.query_selector_all(".lesson-item")
        items[10].click()          # 第 11 块：字符串
        page.wait_for_timeout(400)
        detail = page.query_selector(".lesson-detail[data-detail='10']")
        pre = detail.query_selector(".code-body")
        counts = {}
        for cls in ("tk-kw", "tk-ty", "tk-fn", "tk-com", "tk-str", "tk-num", "tk-hd", "tk-pp"):
            counts[cls] = len(pre.query_selector_all("." + cls))
        print("代码块着色统计:", counts)
        report("关键字+类型着色", counts["tk-kw"] + counts["tk-ty"] >= 5)
        report("库函数着色", counts["tk-fn"] >= 1)
        report("注释着色", counts["tk-com"] >= 1)
        report("字符串着色", counts["tk-str"] >= 1)

        same = page.evaluate(
            """() => {
                const L = DATA.lessons[10];
                const el = document.querySelector(".lesson-detail[data-detail='10'] .code-body");
                return el.textContent === L.code;
            }"""
        )
        report("代码文本未被改动", bool(same))

        # ---------- 2) 正文行内高亮 ----------
        body_toks = len(detail.query_selector_all(".body .tok, .points .tok, .task .tok, .pit .tok"))
        report("正文行内高亮", body_toks >= 10, "数量=%d" % body_toks)

        # ---------- 3) 测验 ----------
        page.click("text=测验")
        page.wait_for_selector(".lesson-item")
        page.click(".lesson-item >> nth=2")     # 第 3 块：运算符
        page.wait_for_timeout(400)
        q_toks = len(page.query_selector_all(".quiz-question .tok, .quiz-opt .tok"))
        report("测验题高亮", q_toks >= 3, "数量=%d" % q_toks)

        # ---------- 4) OJ ----------
        page.click("text=OJ 刷题")
        page.wait_for_selector(".oj-item")
        page.click(".oj-item >> nth=30")        # 第 31 题（描述里有 #define MAX）
        page.wait_for_timeout(400)
        oj_toks = len(page.query_selector_all("#ojdetail .tok"))
        report("OJ 描述高亮", oj_toks >= 2, "数量=%d" % oj_toks)

        ref = page.evaluate("() => DATA.oj.find(p => p.id === 31).reference")
        page.evaluate("(code) => editor.setValue(code)", ref)
        page.click("#submit")
        page.wait_for_selector("#answers .code-body", timeout=60000)
        ans_toks = len(page.query_selector_all("#answers .code-body span[class^='tk-']"))
        report("参考答案高亮", ans_toks >= 5, "数量=%d" % ans_toks)

        page.screenshot(path=os.path.join(APP, "_verify", "ui_highlight.png"), full_page=False)
        b.close()
finally:
    if before is not None:
        io.open(PF, "w", encoding="utf-8").write(before)
    if os.path.isdir(OJ_DIR):
        for name in os.listdir(OJ_DIR):
            os.remove(os.path.join(OJ_DIR, name))

print("语法高亮检查:", "通过" if ok else "有问题")
sys.exit(0 if ok else 1)
