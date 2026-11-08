# -*- coding: utf-8 -*-
"""readme_check.py —— README 里的文件名/路径/图片是否真实存在

避免 README 写了一个不存在的脚本名，别人照着敲报错。
跑法：python _tools/readme_check.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
text = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()

cand = set()
# 反引号里的路径/文件名
for m in re.finditer(r"`([^`\n]+)`", text):
    s = m.group(1).strip()
    if re.fullmatch(r"[\w\-./\\\u4e00-\u9fff]+\.(py|js|css|html|json|md|ico|png|zip|exe|bat|isl)", s):
        cand.add(s)
# markdown 图片
for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
    cand.add(m.group(1))

bad = []
# 这些是「打包后的程序目录里」才有的运行时文件，不在仓库里，跳过
RUNTIME_ONLY = {"compiler\\bin\\gcc.exe", "compiler/bin/gcc.exe"}
for s in sorted(cand):
    p = s.replace("\\", "/")
    if p in RUNTIME_ONLY:
        print("  [SKIP] %-40s （打包产物里的运行时文件）" % s)
        continue
    # 忽略 release 里带版本号的产物（可能还没打）
    if p.startswith("release/") and not os.path.exists(os.path.join(ROOT, p)):
        print("  [SKIP] %-40s （release 产物，可能尚未生成本版）" % s)
        continue
    if not os.path.exists(os.path.join(ROOT, p)):
        bad.append(s)
        print("  [MISS] %s" % s)
    else:
        print("  [OK]   %s" % s)

# 版本一致性
sys.path.insert(0, ROOT)
import appinfo  # noqa: E402
if appinfo.VERSION not in text:
    bad.append("版本号 %s 没出现在 README 里" % appinfo.VERSION)
    print("  [MISS] README 里找不到当前版本号 %s" % appinfo.VERSION)
else:
    print("  [OK]   版本号 %s 已写进 README" % appinfo.VERSION)

print("\n检查了 %d 个引用，%s" % (len(cand), "全部存在" if not bad else "缺失 %d 个" % len(bad)))
sys.exit(0 if not bad else 1)
