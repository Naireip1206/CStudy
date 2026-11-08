# -*- coding: utf-8 -*-
"""run_lessons.py —— 把能自动跑的示例真跑一遍（不需要键盘输入的那些）
需要输入的程序会被跳过（只看编译结果，verify_lessons.py 已覆盖）。
用法：python run_lessons.py
"""
import os
import subprocess

import lessons

TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_verify")
NEED_INPUT = ("scanf", "fgets", "getchar", "fopen")   # 要键盘输入或会读写本地文件的都跳过

ok, skipped, bad = [], [], []
for L in lessons.LESSONS:
    n = L["block"]
    exe = os.path.join(TMP, "l%02d.exe" % n)
    if not os.path.exists(exe):
        bad.append((n, "没找到可执行文件，先跑 verify_lessons.py"))
        continue
    if any(k in L["code"] for k in NEED_INPUT):
        skipped.append(n)
        continue
    try:
        r = subprocess.run([exe], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            ok.append(n)
        else:
            bad.append((n, "退出码 %d：%s" % (r.returncode, r.stderr.strip()[:200])))
    except subprocess.TimeoutExpired:
        bad.append((n, "超时（5 秒没结束，可能有死循环）"))

print("跑通：", ok)
print("跳过（要键盘输入）：", skipped)
print("有问题：", bad if bad else "无")
