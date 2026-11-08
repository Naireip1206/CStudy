# -*- coding: utf-8 -*-
"""verify_lessons.py —— 课程内容体检
1) 结构检查：27 块齐全、字段齐全、block 连续、basics/points 非空
2) 代码检查：每节课的示例代码用 gcc -std=gnu99 真编译一遍（不运行，避免 scanf 卡住）
用法：python verify_lessons.py
"""
import io
import os
import subprocess
import sys

import lessons

GCC = r"D:\w64devkit\bin\gcc.exe"
TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_verify")
REQUIRED = {"block", "part", "ref", "title", "idea", "basics", "points", "code", "task", "pitfall"}

os.makedirs(TMP, exist_ok=True)
problems = []


def check_structure():
    blocks = [l["block"] for l in lessons.LESSONS]
    if blocks != list(range(1, 37)):
        problems.append("block 编号不是 1~36 连续: %s" % blocks)
    for L in lessons.LESSONS:
        miss = REQUIRED - set(L)
        if miss:
            problems.append("第 %d 块缺字段 %s" % (L["block"], miss))
        if len(L.get("basics", [])) < 3:
            problems.append("第 %d 块基础知识小节不足 3 条" % L["block"])
        if len(L.get("points", [])) < 4:
            problems.append("第 %d 块要点不足 4 条" % L["block"])
        if len(L.get("code", "")) < 150:
            problems.append("第 %d 块示例代码过短" % L["block"])


def check_compile():
    for L in lessons.LESSONS:
        src = os.path.join(TMP, "l%02d.c" % L["block"])
        exe = os.path.join(TMP, "l%02d.exe" % L["block"])
        with io.open(src, "w", encoding="utf-8", newline="\n") as f:
            f.write(L["code"] + "\n")
        r = subprocess.run([GCC, src, "-std=gnu99", "-O1", "-o", exe],
                           capture_output=True, text=True, timeout=90)
        if r.returncode != 0:
            problems.append("第 %d 块编译失败:\n%s" % (L["block"], r.stderr.strip()[:600]))
        elif r.stderr.strip():
            problems.append("第 %d 块有警告:\n%s" % (L["block"], r.stderr.strip()[:400]))


check_structure()
check_compile()

if problems:
    print("发现 %d 个问题：" % len(problems))
    for p in problems:
        print(" -", p)
    sys.exit(1)

print("OK：%d 节课，结构完整，全部示例代码编译通过（含警告检查）" % len(lessons.LESSONS))
