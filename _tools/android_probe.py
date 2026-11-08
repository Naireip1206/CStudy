# -*- coding: utf-8 -*-
"""android_probe.py —— 为安卓 v2（本地编译判题）做可行性探查

1) 从清华镜像取 Termux 的 tcc 包（aarch64），解出 .deb 看里面有什么
2) 检查 ELF 架构，确认是不是 Android aarch64 可执行文件
3) 顺手看 Gradle 缓存里有没有 AGP（决定能不能离线编 APK）
"""
import io
import lzma
import os
import re
import tarfile
import urllib.request

WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "android")
os.makedirs(WORK, exist_ok=True)
MIRROR = "https://mirrors.tuna.tsinghua.edu.cn/termux/apt/termux-main/pool/main/t/tcc/"


def fetch(url, timeout=60):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read()


def ar_members(data):
    """解析 ar 归档（.deb 就是 ar），返回 [(name, bytes)]"""
    assert data[:8] == b"!<arch>\n", data[:8]
    pos = 8
    out = []
    while pos + 60 <= len(data):
        hdr = data[pos:pos + 60]
        name = hdr[0:16].decode("ascii", "ignore").strip().rstrip("/")
        size = int(hdr[48:58].decode("ascii").strip())
        body = data[pos + 60:pos + 60 + size]
        out.append((name, body))
        pos += 60 + size + (size % 2)
    return out


print("[1] 取 tcc 包列表")
html = fetch(MIRROR).decode("utf-8", "ignore")
debs = sorted(set(re.findall(r'href="([^"]+\.deb)"', html)))
print("  ", debs)
target = [d for d in debs if "aarch64" in d]
if not target:
    raise SystemExit("镜像里没有 aarch64 包")
deb_url = MIRROR + target[-1]
print("[2] 下载", deb_url)
raw = fetch(deb_url)
print("   %.0f KB" % (len(raw) / 1024))
path = os.path.join(WORK, target[-1])
open(path, "wb").write(raw)

print("[3] 解包")
members = dict(ar_members(raw))
print("   ar 成员:", list(members))
data_tar = None
for name, body in members.items():
    if name.startswith("data.tar"):
        data_tar = (name, body)
print("   data:", data_tar[0] if data_tar else None)
buf = io.BytesIO(data_tar[1])
if data_tar[0].endswith(".xz"):
    buf = io.BytesIO(lzma.decompress(data_tar[1]))
elif data_tar[0].endswith(".gz"):
    import gzip
    buf = io.BytesIO(gzip.decompress(data_tar[1]))

outdir = os.path.join(WORK, "tcc_root")
os.makedirs(outdir, exist_ok=True)
with tarfile.open(fileobj=buf) as tf:
    members = tf.getmembers()
    for m in members:
        if m.isdir():
            continue
    tf.extractall(outdir)

print("[4] 包内文件：")
total = 0
for root, dirs, files in os.walk(outdir):
    for n in sorted(files):
        p = os.path.join(root, n)
        sz = os.path.getsize(p)
        total += sz
        rel = os.path.relpath(p, outdir)
        kind = ""
        with open(p, "rb") as f:
            head = f.read(20)
        if head[:4] == b"\x7fELF":
            ei_class = head[4]
            ei_data = head[5]
            mach = int.from_bytes(head[18:20], "little")
            kind = "ELF class=%d machine=0x%x" % (ei_class, mach)
        print("   %-58s %8.1f KB %s" % (rel, sz / 1024, kind))
print("   合计 %.1f MB" % (total / 1048576))

print("[5] Gradle / AGP 缓存")
g = os.path.join(os.environ["USERPROFILE"], ".gradle", "caches", "modules-2", "files-2.1")
for art in ("com.android.tools.build/gradle", "org.jetbrains.kotlin/kotlin-gradle-plugin"):
    p = os.path.join(g, *art.split("/"))
    print("  ", art, "->", sorted(os.listdir(p)) if os.path.isdir(p) else "缺")
