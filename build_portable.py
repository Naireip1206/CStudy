# -*- coding: utf-8 -*-
"""build_portable.py —— 一键打出"免安装、免 Python"的便携版

产物（都在 release/ 下）：
    C语言学习器-完整版/            exe + compiler + 说明 + 建快捷方式.bat
    C语言学习器-完整版.zip
    C语言学习器-精简版.exe          不带编译器（有 MinGW 的机器可用）

流程：PyInstaller 打包 → 复制裁剪好的 compiler → 写说明 → 起 exe 自测（API + 判题）→ 压缩
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

import appinfo

APP = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(APP, "build")
DIST = os.path.join(APP, "dist")
REL = os.path.join(APP, "release")
COMPILER = os.path.join(BUILD, "compiler")
NAME = "C语言学习器"
SHORTCUT = appinfo.SHORTCUT_NAME
EXE = os.path.join(DIST, NAME + ".exe")


def sh(cmd, **kw):
    print(">", " ".join(cmd) if isinstance(cmd, list) else cmd)
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def build_exe():
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onefile",
        "--name", NAME,
        "--icon", os.path.join(APP, "icon.ico"),
        "--add-data", os.path.join(APP, "static") + ";static",
        "--distpath", DIST,
        "--workpath", os.path.join(BUILD, "pyinstaller"),
        "--specpath", os.path.join(BUILD, "spec"),
        "--exclude-module", "tkinter",
        "--exclude-module", "unittest",
        "--exclude-module", "pydoc",
        "--exclude-module", "doctest",
        "--exclude-module", "test",
        "--exclude-module", "lib2to3",
        os.path.join(APP, "server.py"),
    ]
    r = sh(args)
    if r.returncode != 0:
        print(r.stdout[-2000:])
        print(r.stderr[-4000:])
        sys.exit(1)
    print("exe 大小：%.1f MB" % (os.path.getsize(EXE) / 1048576))


README = """C 语言学习器  ·  使用说明
==================================================

【怎么用】
1. 把整个文件夹解压到一个位置（别只拖 exe 出来，compiler 文件夹要跟着）
2. 双击「C语言学习器.exe」
3. 会弹出一个黑色窗口，几秒后浏览器自动打开学习界面
4. 学完直接关掉黑色窗口就退出了（浏览器页面可以留着，不影响）

【界面里有什么】
  课程   36 节：printf → 指针 → 结构体 → 链表 → 文件 → 算法
  测验   72 道四选一（每个知识点 2 道）
  OJ     36 道题，网页里直接写代码，一键编译判分，报错自动翻译成中文
  错题本 答错的题自动收集，可以写笔记
  进度   课程/测验/OJ 完成情况

【OJ 需要编译器】
完整版已经把 MinGW gcc 放在 compiler 文件夹里，开箱即用。
如果你只拿了精简版 exe，OJ 会提示找不到编译器——课程和测验仍然完全可用。
想临时用别的编译器：设置环境变量 CSTUDY_GCC 指向你的 gcc.exe 即可。

【数据存在哪】
  C:\\Users\\你的用户名\\AppData\\Local\\CStudy
  progress.json  学习进度
  oj\\            每道题你正在写的草稿（会随提交更新）
  ac\\            判题通过（AC）的代码留档，一题一个 .c 文件，不会因为你后面改错而丢失
  网页左边「通过代码」页可以直接看这些通过过的代码，还能一键复制。
  换电脑想带走进度，把整个 CStudy 文件夹拷过去就行。

【常见问题】
· 浏览器没自动打开：手动访问黑色窗口里显示的网址
· 提示端口被占用：程序会自动换下一个端口，按窗口里显示的网址访问
· 360/火绒报毒：PyInstaller 打包的 exe 常被误报，加信任即可（源码就是本文件夹里的 .py）
· 想重学：关掉程序，删掉 AppData\\Local\\CStudy\\progress.json

【给同学的一句话】
这是自己写的 C 语言练习册，36 个知识点 + 108 道题，做错了会告诉你为什么错。
有问题直接找作者反馈。
"""

SHORTCUT_BAT = r"""@echo off
chcp 65001 >nul
rem 在桌面创建「C 语言学习器」快捷方式（带图标），桌面被重定向到别的盘也能找到
set "TARGET=%~dp0C语言学习器.exe"
powershell -NoProfile -Command ^
  "$desk=[Environment]::GetFolderPath('Desktop');" ^
  "$lnk=Join-Path $desk 'CStudy.lnk';" ^
  "$s=(New-Object -ComObject WScript.Shell).CreateShortcut($lnk);" ^
  "$s.TargetPath='%TARGET%';" ^
  "$s.WorkingDirectory=Split-Path '%TARGET%';" ^
  "$s.IconLocation='%TARGET%,0';" ^
  "$s.Description='C 语言学习器 · 36 节课程 / 72 题测验 / 36 道 OJ';" ^
  "$s.Save(); Write-Host ('已创建：' + $lnk)"
if errorlevel 1 (echo 创建失败，可以直接双击 exe 使用。)
pause
"""


def assemble():
    # 先清掉可能还开着的旧实例，否则 exe 被占用、复制会失败
    subprocess.run(["taskkill", "/IM", NAME + ".exe", "/F"], capture_output=True)
    time.sleep(0.5)
    full = os.path.join(REL, NAME + "-完整版")
    # 只清理自己产出的东西，别把 release 整锅端（安装包 CStudy-Setup-*.exe 也在这儿）
    os.makedirs(REL, exist_ok=True)
    shutil.rmtree(full, ignore_errors=True)
    os.makedirs(full, exist_ok=True)
    shutil.copy2(EXE, os.path.join(full, NAME + ".exe"))
    if not os.path.isdir(COMPILER):
        sys.exit("!! 没找到 %s，先跑 _tools/make_portable_compiler.py" % COMPILER)
    shutil.copytree(COMPILER, os.path.join(full, "compiler"))
    with open(os.path.join(full, "使用说明.txt"), "w", encoding="utf-8-sig", newline="\r\n") as f:
        f.write(README)
    with open(os.path.join(full, "创建桌面快捷方式.bat"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write(SHORTCUT_BAT)

    # 精简版单独放一份（不带编译器）
    shutil.copy2(EXE, os.path.join(REL, NAME + "-精简版.exe"))

    # zip：用 Python zipfile，中文文件名会带 UTF-8 标记，Win10/11 资源管理器正常显示
    zip_path = os.path.join(REL, NAME + "-完整版.zip")
    import zipfile
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for root, dirs, files in os.walk(full):
            for n in files:
                abs_p = os.path.join(root, n)
                rel_p = os.path.join(NAME + "-完整版", os.path.relpath(abs_p, full))
                z.write(abs_p, rel_p)
    size = os.path.getsize(zip_path) / 1048576
    print("压缩包：%s（%.1f MB）" % (zip_path, size))
    return full, zip_path


def self_test(full):
    """真跑一遍：起 exe → 读 API → 用自带编译器判一道题 → 看存档写没写

    数据目录用 CSTUDY_DATA 隔离到临时目录 —— 绝不能 rmtree %LOCALAPPDATA%\\CStudy，
    那里面是用户真实的进度和 AC 留档（曾经因为这里删过一次，把用户的 AC 记录冲掉了）。
    """
    appdata_dir = os.path.join(tempfile.gettempdir(), "CStudyPortableTest", "_userdata")
    shutil.rmtree(os.path.dirname(appdata_dir), ignore_errors=True)
    os.makedirs(appdata_dir, exist_ok=True)

    env = dict(os.environ)
    env["CSTUDY_PORT"] = "8791"
    env["CSTUDY_DATA"] = appdata_dir
    proc = subprocess.Popen([os.path.join(full, NAME + ".exe")],
                            cwd=full, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    base = "http://127.0.0.1:8791"
    data = None
    for _ in range(60):
        time.sleep(1)
        try:
            with urllib.request.urlopen(base + "/api/data", timeout=3) as r:
                data = json.loads(r.read().decode("utf-8"))
            break
        except Exception:
            if proc.poll() is not None:
                print("!! exe 提前退出：", proc.stdout.read()[:2000])
                return False
    if not data:
        print("!! 30 秒内没起来")
        proc.kill()
        return False

    print("API：%d 节 / %d 测验 / %d OJ" % (len(data["lessons"]), len(data["quizzes"]), len(data["oj"])))

    ones = next(p for p in data["oj"] if p["id"] == 27)
    body = json.dumps({"id": 27, "code": ones["reference"]}).encode()
    req = urllib.request.Request(base + "/api/judge", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        verdict = json.loads(r.read().decode("utf-8"))["verdict"]
    print("调用自带编译器判第 27 题 →", verdict)

    saved = os.path.join(appdata_dir, "progress.json")
    ok = os.path.exists(saved)
    print("存档写到数据目录（临时隔离）：", ok, "|", saved)
    # 单文件 exe 会派生子进程，按进程树清掉（别误伤别的实例）
    subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
    shutil.rmtree(os.path.dirname(appdata_dir), ignore_errors=True)
    return verdict == "AC" and ok


if __name__ == "__main__":
    build_exe()
    full_dir, zip_path = assemble()
    ok = self_test(full_dir)
    print("自测：", "通过" if ok else "失败")
    sys.exit(0 if ok else 1)
