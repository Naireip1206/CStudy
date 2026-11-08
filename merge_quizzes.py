# -*- coding: utf-8 -*-
"""merge_quizzes.py —— 把测验题抽到 quizzes.py（一次性脚本，可重复跑）

1) 读 data.py 里现有的 QUIZZES（20 道）+ quizzes_new.py 的 52 道
2) 按知识块排序，写成一个完整的 quizzes.py（72 道，覆盖 36 个知识块）
3) 把 data.py 里的 QUIZZES 定义换成 from quizzes import QUIZZES
"""
import io
import json
import os
import shutil

import data
from quizzes_new import NEW_QUIZZES

APP = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP, "data.py")
QUIZ = os.path.join(APP, "quizzes.py")

old = list(data.QUIZZES)
new_ids = {(q["lesson"], q["question"]) for q in NEW_QUIZZES}
old = [q for q in old if (q["lesson"], q["question"]) not in new_ids]   # 可重复运行

allq = sorted(old + [q for q in NEW_QUIZZES],
              key=lambda q: (q["lesson"], q["question"]))

head = '''# -*- coding: utf-8 -*-
"""quizzes.py —— 全部测验题（72 道，覆盖 36 个知识块，每块 2 道）

字段：
    lesson   对应知识块编号（1~36）
    question 题干（代码换行用 \\n）
    options  四个选项 [A, B, C, D]
    answer   正确选项下标 0~3（不是字母！）
    explain  解析

data.py 通过 `from quizzes import QUIZZES` 取用。
"""

QUIZZES = '''
io.open(QUIZ, "w", encoding="utf-8", newline="\n").write(
    head + json.dumps(allq, ensure_ascii=False, indent=4) + "\n")
print("quizzes.py 写出 %d 道题" % len(allq))

# ---- 改 data.py：QUIZZES 定义换成 import ----
src = io.open(DATA, encoding="utf-8").read()
if "from quizzes import QUIZZES" not in src:
    i = src.index("QUIZZES = [")
    j = src.index("\n]\n", i) + len("\n]\n")
    if not os.path.exists(DATA + ".bak2"):
        shutil.copyfile(DATA, DATA + ".bak2")
    src = src[:i] + "from quizzes import QUIZZES  # noqa: E402  测验题在 quizzes.py（72 道）\n" + src[j:]
    src = src.replace("包含：课程 27 节（lessons.py）、测验 20 题、OJ 练习题 27 道（oj_bank.py / answers_*.py）。",
                      "包含：课程 36 节（lessons.py）、测验 72 题（quizzes.py）、OJ 练习题 36 道（oj_bank.py / answers_*.py）。")
    io.open(DATA, "w", encoding="utf-8", newline="\n").write(src)
    print("data.py: QUIZZES 已改为从 quizzes 导入")
