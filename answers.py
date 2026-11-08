# -*- coding: utf-8 -*-
"""answers.py —— OJ 参考答案汇总入口

27 道题分三个文件维护：
    answers_a.py  第 1~14 题
    answers_b.py  第 15~27 题
    answers_c.py  第 28~36 题
每题两个版本：reference（朴素）与 best（精简/高效），AC 后在网页里对比。
"""

from answers_a import ANSWERS as _A
from answers_b import ANSWERS as _B
from answers_c import ANSWERS as _C

ANSWERS = {**_A, **_B, **_C}
