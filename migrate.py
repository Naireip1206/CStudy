# -*- coding: utf-8 -*-
"""migrate.py —— 一次性迁移脚本：
1) 把 data.py 里旧的 10 节 LESSONS 删掉，改成 from lessons import LESSONS
2) 把 20 道测验的 lesson 编号，从旧 1~10 映射到新块号（1,2,4,5,7,8,9,11,13,17）
3) 备份原文件为 *.bak
可重复运行（已迁移过会自动跳过）。
"""
import io
import re
import shutil
import os

APP = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP, "data.py")

# 旧第 n 节课 -> 新的知识地图块号
OLD_TO_NEW = {1: 1, 2: 2, 3: 4, 4: 5, 5: 7, 6: 8, 7: 9, 8: 11, 9: 13, 10: 17}

src = io.open(DATA, encoding="utf-8").read()
changed = []

# ---------- 1) 替换 LESSONS 定义 ----------
if "from lessons import LESSONS" not in src:
    i = src.index("LESSONS = [")
    j = src.index("\n]\n", i) + len("\n]\n")
    new_block = (
        "# 课程数据已迁移到 lessons.py（27 节，每节含基础知识 / 要点清单）\n"
        "# 维护顺序：lessons_a.py（1-9）→ lessons_b.py（10-18）→ lessons_c.py（19-27）\n"
        "from lessons import LESSONS  # noqa: E402\n"
    )
    src = src[:i] + new_block + src[j:]
    changed.append("replaced old LESSONS with import")

src = src.replace("包含：课程 10 节、测验 20 题、OJ 练习题 10 道。",
                  "包含：课程 27 节（内容在 lessons.py）、测验 20 题、OJ 练习题 10 道。")

# ---------- 2) 重映射测验的 lesson 编号 ----------
if "lesson" in src:
    counter = {"k": 0}

    def repl(m):
        idx = counter["k"]
        old = idx // 2 + 1          # 旧数据每节 2 题，按出现顺序还原旧节号
        counter["k"] += 1
        new = OLD_TO_NEW.get(old, old)
        return '"lesson": %d,' % new

    if counter["k"] == 0:
        pass
    new_src, n = re.subn(r'"lesson":\s*(\d+),', repl, src)
    # 只在确实是旧编号体系时才替换（20 题、节号最大 10）
    olds = [int(x) for x in re.findall(r'"lesson":\s*(\d+),', src)]
    if n and max(olds) <= 10 and len(olds) == 20:
        src = new_src
        changed.append("remapped %d quiz lesson numbers" % n)
    else:
        changed.append("quiz mapping skipped (already migrated? lessons=%d)" % len(olds))

# ---------- 3) 备份 + 写回 ----------
bak = DATA + ".bak"
if not os.path.exists(bak):
    shutil.copyfile(DATA, bak)

io.open(DATA, "w", encoding="utf-8", newline="\n").write(src)
print("done:", ", ".join(changed) if changed else "nothing to do")
