# -*- coding: utf-8 -*-
"""
data.py —— C 语言学习器（Python 版）的全部数据
包含：课程 36 节（lessons.py）、测验 72 题（quizzes.py）、OJ 练习题 36 道（oj_bank.py / answers_*.py）。
想加内容，直接往对应列表末尾加一条即可。
"""

# ============================================================
# 课程（10 节，每节固定五块）
#   title   标题
#   idea    一句话原理
#   code    最小可运行示例代码
#   task    动手改一改
#   pitfall 一句话坑
# ============================================================
# 课程数据已迁移到 lessons.py（27 节，每节含基础知识 / 要点清单）
# 维护顺序：lessons_a.py（1-9）→ lessons_b.py（10-18）→ lessons_c.py（19-27）
from lessons import LESSONS  # noqa: E402

# ============================================================
# 测验题（20 题，每题四选一）
#   lesson    对应第几节课
#   question  题干
#   options   四个选项 [A, B, C, D]
#   answer    正确答案下标 0~3
#   explain   解析（答错时显示）
# ============================================================
from quizzes import QUIZZES  # noqa: E402  测验题在 quizzes.py（72 道）

# ============================================================
# OJ 练习题（10 道，可编译判分）
#   title        题目名
#   difficulty   难度
#   description  题目描述
#   input_format 输入格式
#   output_format 输出格式
#   samples      样例 [{input, output}, ...]
#   time_limit   时间限制（秒）
# ============================================================
from oj_bank import OJ_PROBLEMS  # noqa: E402  OJ 题库：27 题，一题一个知识块
