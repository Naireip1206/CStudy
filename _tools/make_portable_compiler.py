# -*- coding: utf-8 -*-
"""make_portable_compiler.py —— 从 D:\\w64devkit 裁一份最小 64 位 gcc（够编译全部 OJ 答案）

思路：
1. 只复制 bin(gcc/as/ld) + libexec(cc1/collect2) + lib 里必要的启动对象和 import 库
2. lib/gcc 下丢掉 32 位、C++/Fortran/OpenMP 那一堆库，只留 libgcc.a
3. 头文件用 gcc -H 真扫一遍依赖，只保留实际用到的（Windows API 那一坨全不要）
4. 用裁剪后的编译器把 36 道题的 reference + best 共 72 个程序全编一遍做验收
"""
import os
import re
import shutil
import subprocess
import sys

SRC = r"D:\w64devkit"
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "compiler")
GCCVER = "16.2.0"
TARGET = "x86_64-w64-mingw32"
GCCDIR = os.path.join("lib", "gcc", TARGET, GCCVER)

BIN_FILES = ["gcc.exe", "as.exe", "ld.exe"]
LIBEXEC_FILES = ["cc1.exe", "collect2.exe"]
LIB_FILES = [
    "crt1.o", "crt1u.o", "crt2.o", "crt2u.o", "crtbegin.o", "crtend.o",
    "dllcrt1.o", "dllcrt2.o", "libmingw32.a", "libmingwex.a", "libmingwthrd.a",
    "libmsvcrt.a", "libmsvcrt-os.a", "libm.a", "libmoldname.a", "libpthread.a",
    "libkernel32.a", "libuser32.a", "libadvapi32.a", "libshell32.a",
    "libgdi32.a", "libcomdlg32.a", "libcomctl32.a", "libole32.a", "liboleaut32.a",
    "libuuid.a", "libws2_32.a", "libshlwapi.a", "libbcrypt.a", "libucrtbase.a",
]
# gcc 自带 include 里 C 语言必需的小文件（不依赖扫描，稳定保留）
GCC_HDR_KEEP = [
    "stddef.h", "stdarg.h", "stdbool.h", "stdalign.h", "stdatomic.h", "stdnoreturn.h",
    "float.h", "varargs.h", "iso646.h", "limits.h", "syslimits.h", "unwind.h",
    "omp.h", "mm_malloc.h", "xmmintrin.h", "emmintrin.h", "immintrin.h",
]

PROBE = r"""#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <ctype.h>
#include <time.h>
#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdarg.h>
#include <float.h>
#include <errno.h>
#include <locale.h>
#include <signal.h>
#include <setjmp.h>
#include <wchar.h>
#include <wctype.h>
#include <inttypes.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <io.h>
#include <process.h>

typedef struct Node { int data; struct Node *next; } Node;

static int cmp(const void *a, const void *b) {
    return *(const int*)a - *(const int*)b;
}

int main(int argc, char **argv) {
    int *a = (int*)malloc(4 * sizeof(int));
    Node *n = (Node*)malloc(sizeof(Node));
    if (!a || !n) return 1;
    a[0] = 3; a[1] = 1; a[2] = 2; a[3] = 4;
    qsort(a, 4, sizeof(int), cmp);
    n->data = a[3]; n->next = NULL;
    char buf[64];
    snprintf(buf, sizeof buf, "%d %.2f %s %zu", n->data, sqrt(2.0), "ok", (size_t)4);
    long long big = 1234567890123LL;
    uint32_t u = 4294967295u;
    bool t = true;
    FILE *fp = fopen("_probe.tmp", "w");
    if (fp) { fprintf(fp, "%lld %u\n", big, u); fclose(fp); remove("_probe.tmp"); }
    time_t tt = time(NULL);
    printf("%s | %d %c %lld %d %ld\n", buf, isdigit('7'), (char)toupper('a'), big, (int)t, (long)tt);
    fprintf(stderr, "%d\n", argc);
    free(a); free(n);
    return 0;
}"""


def rm(path):
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    elif os.path.exists(path):
        os.remove(path)


def main():
    rm(DST)
    os.makedirs(DST, exist_ok=True)

    for f in BIN_FILES:
        p = os.path.join(SRC, "bin", f)
        os.makedirs(os.path.join(DST, "bin"), exist_ok=True)
        shutil.copy2(p, os.path.join(DST, "bin", f))

    lex_src = os.path.join(SRC, "libexec", "gcc", TARGET, GCCVER)
    lex_dst = os.path.join(DST, "libexec", "gcc", TARGET, GCCVER)
    os.makedirs(lex_dst, exist_ok=True)
    for f in LIBEXEC_FILES:
        shutil.copy2(os.path.join(lex_src, f), os.path.join(lex_dst, f))

    # lib/gcc：只留 C 需要的
    gcc_src = os.path.join(SRC, GCCDIR)
    gcc_dst = os.path.join(DST, GCCDIR)
    os.makedirs(gcc_dst, exist_ok=True)
    for name in os.listdir(gcc_src):
        p = os.path.join(gcc_src, name)
        if name in ("crtbegin.o", "crtend.o", "crtfastmath.o", "libgcc.a", "libgcc_eh.a"):
            if os.path.isfile(p):
                shutil.copy2(p, os.path.join(gcc_dst, name))
        elif name == "include":
            os.makedirs(os.path.join(gcc_dst, "include"), exist_ok=True)
            for h in GCC_HDR_KEEP:
                hp = os.path.join(p, h)
                if os.path.exists(hp):
                    shutil.copy2(hp, os.path.join(gcc_dst, "include", h))
        elif name == "include-fixed":
            shutil.copytree(p, os.path.join(gcc_dst, "include-fixed"), dirs_exist_ok=True)

    # lib 根：启动对象 + import 库
    for f in LIB_FILES:
        p = os.path.join(SRC, "lib", f)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(DST, "lib", f))

    # 先把整个 mingw include 复制到临时位置，用 -H 扫出依赖，再删掉用不到的
    # （空 include 目录 gcc 连 stdio.h 都找不到，扫不出任何东西）
    stage = os.path.join(DST, "include")
    shutil.copytree(os.path.join(SRC, "include"), stage, dirs_exist_ok=True)
    probe_c = os.path.join(DST, "_probe.c")
    with open(probe_c, "w", encoding="utf-8") as f:
        f.write(PROBE)

    env = dict(os.environ)
    env["PATH"] = os.path.join(DST, "bin") + ";" + env.get("PATH", "")
    hdr = subprocess.run(
        [os.path.join(DST, "bin", "gcc.exe"), "-std=gnu99", "-H", "-fsyntax-only", probe_c],
        capture_output=True, text=True, env=env,
    )
    needed = []
    for line in hdr.stderr.splitlines():
        m = re.match(r"^\.+\s+(.+)$", line)
        if m:
            needed.append(m.group(1).strip())
    print("依赖头文件 %d 个" % len(needed))
    missing = [n for n in needed if not os.path.isabs(n)]
    if missing:
        print("!! 出现非绝对路径，可能有问题:", missing[:3])

    # 注意：gcc 会优先从自己所在的 prefix（DST）里找头，所以扫出来的路径是 DST\include\...
    # 这里同时按 DST 和 SRC 两个前缀归一出相对路径
    roots = [os.path.normpath(stage), os.path.normpath(os.path.join(SRC, "include"))]
    keep = set()
    for path in needed:
        p = os.path.normpath(path)
        for root in roots:
            if p.lower().startswith(root.lower()):
                keep.add(os.path.relpath(p, root).replace("\\", "/").lower())
                break
    print("依赖里属于 mingw include 的：%d 个" % len(keep))

    # 剪枝：stage 里没被扫到的全删
    removed = 0
    for root, dirs, files in os.walk(stage, topdown=False):
        for n in files:
            full = os.path.join(root, n)
            rel = os.path.relpath(full, stage).replace("\\", "/").lower()
            if rel not in keep:
                os.remove(full)
                removed += 1
        for d in dirs:
            p = os.path.join(root, d)
            if not os.listdir(p):
                os.rmdir(p)
    print("剪掉多余头文件 %d 个，保留 %d 个" % (removed, len(keep)))

    # 验收 1：探针能编能跑
    exe = os.path.join(DST, "_probe.exe")
    r = subprocess.run([os.path.join(DST, "bin", "gcc.exe"), probe_c, "-std=gnu99", "-O2",
                        "-o", exe], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print("探针编译失败:\n", r.stderr[-3000:])
        sys.exit(1)
    run = subprocess.run([exe], capture_output=True, text=True)
    print("探针运行:", run.stdout.strip()[:120], "| rc =", run.returncode)
    rm(probe_c)
    rm(exe)

    # 验收 2：72 个 OJ 答案全编一遍
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import answers  # noqa: E402
    bad = []
    tmp = os.path.join(DST, "_check")
    os.makedirs(tmp, exist_ok=True)
    for pid, pair in sorted(answers.ANSWERS.items()):
        for kind, code in pair.items():
            c = os.path.join(tmp, "p%d_%s.c" % (pid, kind))
            with open(c, "w", encoding="utf-8") as f:
                f.write(code + "\n")
            rr = subprocess.run([os.path.join(DST, "bin", "gcc.exe"), c, "-std=gnu99", "-O2",
                                 "-o", c[:-2] + ".exe"], capture_output=True, text=True, env=env)
            if rr.returncode != 0:
                bad.append((pid, kind, rr.stderr.strip().splitlines()[0][:120]))
    shutil.rmtree(tmp, ignore_errors=True)
    print("OJ 答案编译：%d 个失败" % len(bad))
    for b in bad[:10]:
        print("   ", b)

    total = 0
    for root, dirs, files in os.walk(DST):
        for n in files:
            total += os.path.getsize(os.path.join(root, n))
    print("最终大小：%.1f MB" % (total / 1048576))
    if bad:
        sys.exit(1)


main()
