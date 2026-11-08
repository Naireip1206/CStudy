# -*- coding: utf-8 -*-
"""migrate_oj.py —— 把 OJ 题库迁移到 oj_bank.py / answers_a|b.py（一次性脚本，可重复跑）

1) data.py：删掉内联的 OJ_PROBLEMS，改成 from oj_bank import OJ_PROBLEMS
2) answers.py：改写为汇总 answers_a + answers_b 的入口（旧内容备份成 answers_old10.py.bak）
3) 顺手删掉旧的 oj/problem_*.c 模板（都还是没写过的空模板，避免题号错位）
"""
import io
import os
import shutil

APP = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP, "data.py")
ANS = os.path.join(APP, "answers.py")
OJ_DIR = os.path.join(APP, "oj")

# ---------- 1) data.py ----------
src = io.open(DATA, encoding="utf-8").read()
if "from oj_bank import OJ_PROBLEMS" not in src:
    i = src.index("OJ_PROBLEMS = [")
    tail = src[i:]
    assert tail.rstrip().endswith("]"), "OJ_PROBLEMS 不是文件最后一段，先人工确认"
    src = src[:i] + "from oj_bank import OJ_PROBLEMS  # noqa: E402  OJ 题库：27 题，一题一个知识块\n"
    src = src.replace("包含：课程 27 节（内容在 lessons.py）、测验 20 题、OJ 练习题 10 道。",
                      "包含：课程 27 节（lessons.py）、测验 20 题、OJ 练习题 27 道（oj_bank.py / answers_*.py）。")
    if not os.path.exists(DATA + ".bak"):
        shutil.copyfile(DATA, DATA + ".bak")
    io.open(DATA, "w", encoding="utf-8", newline="\n").write(src)
    print("data.py: OJ_PROBLEMS 已改为从 oj_bank 导入")

# ---------- 2) answers.py ----------
new_ans = '''# -*- coding: utf-8 -*-
"""answers.py —— OJ 参考答案汇总入口

27 道题分两个文件维护：
    answers_a.py  第 1~14 题
    answers_b.py  第 15~27 题
每题两个版本：reference（朴素）与 best（精简/高效），AC 后在网页里对比。
"""

from answers_a import ANSWERS as _A
from answers_b import ANSWERS as _B

ANSWERS = {**_A, **_B}
'''
if "from answers_a import ANSWERS" not in io.open(ANS, encoding="utf-8").read():
    shutil.copyfile(ANS, ANS + ".bak")   # 旧 10 题备份（.bak 不会被 import）
    io.open(ANS, "w", encoding="utf-8", newline="\n").write(new_ans)
    print("answers.py 已改为汇总入口（旧内容见 answers.py.bak）")

# ---------- 3) 清理旧 OJ 模板 ----------
if os.path.isdir(OJ_DIR):
    removed = 0
    for name in os.listdir(OJ_DIR):
        if name.startswith("problem_") and name.endswith(".c"):
            path = os.path.join(OJ_DIR, name)
            if os.path.getsize(path) < 120:      # 空模板 91 字节
                os.remove(path)
                removed += 1
    print("清理旧 OJ 模板 %d 个" % removed)

print("迁移完成")
