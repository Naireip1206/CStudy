# -*- coding: utf-8 -*-
"""ac_check.py —— 验证"OJ 通过后代码留档"完整链路

1) 提交 WA  → 不留档
2) 提交 AC  → ac/problem_N.c 落盘、进度里记时间、/api/data 里能拿到
3) 再提交 WA → 留档不被覆盖
4) 页面：「通过代码」页能列出并展示；OJ 详情里有多出来的「我的通过代码（留档）」
跑之前备份 progress.json 和 ac/oj 目录，跑完自动还原
"""
import io
import json
import os
import shutil
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

APP = os.path.dirname(os.path.abspath(__file__))
BASE = "http://127.0.0.1:8765"
PF = os.path.join(APP, "progress.json")
AC = os.path.join(APP, "ac")
OJ = os.path.join(APP, "oj")
BAK = os.path.join(APP, "_verify", "ac_check_bak")
PID = 27

os.makedirs(BAK, exist_ok=True)
saved = {}
for p in (PF,):
    if os.path.exists(p):
        saved[p] = io.open(p, encoding="utf-8").read()
for d in (AC, OJ):
    tgt = os.path.join(BAK, os.path.basename(d))
    if os.path.isdir(tgt):
        shutil.rmtree(tgt)
    if os.path.isdir(d):
        shutil.copytree(d, tgt)

ok = True


def check(name, cond, extra=""):
    global ok
    print(("  %-34s %s %s" % (name, "OK" if cond else "!! 失败", extra)).rstrip())
    ok = ok and cond


def api(path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(BASE + path, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


try:
    d = api("/api/data")
    prob = next(p for p in d["oj"] if p["id"] == PID)
    ac_path = os.path.join(AC, "problem_%d.c" % PID)

    # 0) 清掉这道题的留档，确保从零开始
    for p in (ac_path,):
        if os.path.exists(p):
            os.remove(p)

    # 1) 先交错的
    wrong = '#include <stdio.h>\n\nint main(void) {\n    printf("0\\n");\n    return 0;\n}\n'
    r = api("/api/judge", {"id": PID, "code": wrong})
    check("提交错误代码 → WA", r["verdict"] == "WA")
    check("WA 不产生留档", not os.path.exists(ac_path))

    # 2) 再交对的
    ref = prob["reference"]
    r = api("/api/judge", {"id": PID, "code": ref})
    check("提交正确答案 → AC", r["verdict"] == "AC")
    check("ac/problem_%d.c 已落盘" % PID, os.path.exists(ac_path))
    disk = io.open(ac_path, encoding="utf-8").read() if os.path.exists(ac_path) else ""
    check("留档内容与提交一致", disk.strip() == ref.strip())
    rec = (r.get("ac") or {}).get(str(PID))
    check("接口返回留档记录", bool(rec), "| 通过时间 %s" % (rec or {}).get("last", "?"))
    check("记录了行数/次数", bool(rec) and rec.get("lines", 0) > 0 and rec.get("count", 0) >= 1)

    # 3) 再交一次错的，留档不能被覆盖
    r = api("/api/judge", {"id": PID, "code": wrong})
    still = io.open(ac_path, encoding="utf-8").read() if os.path.exists(ac_path) else ""
    check("再次 WA 后留档仍在", r["verdict"] == "WA" and still.strip() == ref.strip())

    # 4) 页面
    with sync_playwright() as pw:
        b = pw.chromium.launch(channel="msedge", headless=True)
        page = b.new_page(viewport={"width": 1300, "height": 1000})
        page.goto(BASE, wait_until="networkidle")
        page.wait_for_timeout(500)

        page.click("text=通过代码")
        page.wait_for_timeout(500)
        txt = page.inner_text("#content")
        check("「通过代码」页列出该题", ("%d." % PID) in txt and "我的通过代码" in page.inner_html("#content"))
        toks = page.query_selector_all("#content .code-body span[class^='tk-']")
        check("留档代码高亮渲染", len(toks) >= 3, "着色 span %d 个" % len(toks))
        check("有复制按钮", page.query_selector("[data-copy]") is not None)
        page.screenshot(path=os.path.join(APP, "_verify", "ui_mycode.png"))

        # OJ 详情里也要能找到
        page.click("text=OJ 刷题")
        page.wait_for_selector(".oj-item")
        page.click(".oj-item >> nth=%d" % (PID - 1))
        page.wait_for_timeout(400)
        detail_html = page.inner_html("#ojdetail")
        check("OJ 详情显示留档折叠块", "我的通过代码（留档" in detail_html)
        b.close()
finally:
    # 还原现场
    if PF in saved:
        io.open(PF, "w", encoding="utf-8").write(saved[PF])
    elif os.path.exists(PF):
        os.remove(PF)
    for d in (AC, OJ):
        tgt = os.path.join(BAK, os.path.basename(d))
        if os.path.isdir(d):
            shutil.rmtree(d, ignore_errors=True)
        if os.path.isdir(tgt):
            shutil.copytree(tgt, d)
        shutil.rmtree(tgt, ignore_errors=True)

print("留档检查:", "通过" if ok else "有问题")
sys.exit(0 if ok else 1)
