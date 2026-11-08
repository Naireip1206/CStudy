import os

ROOT = r"D:\w64devkit"


def size(p):
    t = 0
    for r, d, f in os.walk(p):
        for n in f:
            try:
                t += os.path.getsize(os.path.join(r, n))
            except OSError:
                pass
    return t / 1024 / 1024


for name in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, name)
    if os.path.isdir(p):
        print("DIR  %-14s %7.1f MB" % (name, size(p)))
    else:
        print("FILE %-14s %7.2f MB" % (name, os.path.getsize(p) / 1024 / 1024))

print("\n--- bin (前 20) ---")
b = os.path.join(ROOT, "bin")
for n in sorted(os.listdir(b))[:20]:
    print("   ", n, round(os.path.getsize(os.path.join(b, n)) / 1024 / 1024, 2), "MB")

print("\n--- libexec 树 ---")
for r, d, f in os.walk(os.path.join(ROOT, "libexec")):
    depth = r[len(ROOT):].count("\\")
    if depth <= 5:
        print("  " * depth + r.replace(ROOT, "") + "  (%d 文件, %.1f MB)" % (len(f), sum(os.path.getsize(os.path.join(r, x)) for x in f) / 1048576))

print("\n--- 顶层非标准目录 ---")
for n in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, n)
    if os.path.isdir(p) and n not in ("bin", "etc", "include", "lib", "lib32", "libexec", "share", "src"):
        print("   ", n, round(size(p), 1), "MB")
