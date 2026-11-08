# -*- coding: utf-8 -*-
"""verify_oj.py —— OJ 题库体检（真跑判题器）

对 27 道题逐一：
    1) 用 reference 提交 → 必须 AC（顺带验证样例输出是真实跑出来的）
    2) 用 best 提交      → 必须 AC
    3) 用一段明显错的代码 → 必须 WA（确认判题不是永远 AC）
产物放在 _verify/oj/ 下，不碰你自己的 oj/problem_N.c
"""
import io
import os
import subprocess
import sys

import data
import judge

GCC = r"D:\w64devkit\bin\gcc.exe"
TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_verify", "oj")
os.makedirs(TMP, exist_ok=True)

WRONG = '#include <stdio.h>\n\nint main(void) {\n    printf("999999\\n");\n    return 0;\n}\n'

bad = []
for p in data.OJ_PROBLEMS:
    pid = p["id"]
    ans = __import__("answers").ANSWERS.get(pid)
    if not ans:
        bad.append((pid, "没有参考答案"))
        continue
    for kind in ("reference", "best"):
        src = os.path.join(TMP, "p%02d_%s.c" % (pid, kind))
        io.open(src, "w", encoding="utf-8", newline="\n").write(ans[kind] + "\n")
        # 编译时也检查警告（judge 不报警告，这里单独跑一次 gcc）
        w = subprocess.run([GCC, src, "-std=gnu99", "-O2", "-Wall", "-o", os.path.join(TMP, "x.exe")],
                           capture_output=True, text=True, timeout=60)
        if w.returncode != 0:
            bad.append((pid, "%s 编译失败: %s" % (kind, w.stderr.strip()[:300])))
            continue
        if w.stderr.strip():
            bad.append((pid, "%s 有警告: %s" % (kind, w.stderr.strip()[:250])))
        r = judge.judge(src, p)
        if r["verdict"] != "AC":
            bad.append((pid, "%s 判题结果 %s: %s" % (kind, r["verdict"], r["message"])))

    wsrc = os.path.join(TMP, "p%02d_wrong.c" % pid)
    io.open(wsrc, "w", encoding="utf-8", newline="\n").write(WRONG)
    r = judge.judge(wsrc, p)
    if r["verdict"] != "WA":
        bad.append((pid, "错误代码竟然判成 %s（判题器有问题）" % r["verdict"]))

print("检查 %d 道题 × 3 个提交" % len(data.OJ_PROBLEMS))
if bad:
    print("发现 %d 个问题：" % len(bad))
    for pid, msg in bad:
        print(" - 第 %d 题：%s" % (pid, msg))
    sys.exit(1)
print("OK：%d 道题的 reference / best 全部 AC，错误代码全部 WA" % len(data.OJ_PROBLEMS))
