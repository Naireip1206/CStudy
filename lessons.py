# -*- coding: utf-8 -*-
"""lessons.py —— 课程总装（27 节，对应《知识地图》第 1~27 块）

课程内容分三个文件维护，方便单独修改：
    lessons_a.py   第 1~9 块   阶段一（基础语法）+ 第 9 块（数组）
    lessons_b.py   第 10~18 块 阶段二（数组/字符串/函数）+ 阶段三开头（指针）
    lessons_c.py   第 19~27 块 指针深化 + 阶段四（结构体/链表/位运算）

每节课的字段：block / part / ref / title / idea / basics / points / code / task / pitfall
data.py 通过 `from lessons import LESSONS` 取用；app.js 负责把 basics 和 points 渲染出来。
"""

from lessons_a import LESSONS as _A
from lessons_b import LESSONS as _B
from lessons_c import LESSONS as _C
from lessons_d import LESSONS as _D

LESSONS = _A + _B + _C + _D
