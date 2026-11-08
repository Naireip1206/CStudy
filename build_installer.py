# -*- coding: utf-8 -*-
"""build_installer.py —— 打一个正式的 Windows 安装包（Inno Setup）

流程：
1. PyInstaller --onedir 出「目录版」（启动比 onefile 快，安装包也该用这种）
2. 生成 app.iss（中文向导、装到 %LOCALAPPDATA%\\Programs\\CStudy、桌面/开始菜单快捷方式、卸载项）
3. ISCC 编译成 release\\CStudy-Setup-1.0.0.exe
4. 自测：静默安装到临时目录 → 起 exe 调 API + 判一道题 → 静默卸载 → 检查清理

用法：python build_installer.py
"""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

import appinfo

APP = os.path.dirname(os.path.abspath(__file__))
NAME = "C语言学习器"
VERSION = appinfo.VERSION
SHORTCUT = appinfo.SHORTCUT_NAME
VER4 = VERSION + ".0" if VERSION.count(".") == 2 else VERSION
VER_TUPLE = "(" + ",".join((VERSION.split(".") + ["0", "0"])[:4]) + ")"
BUILD = os.path.join(APP, "build")
DIST_ONEDIR = os.path.join(APP, "dist_onedir")
REL = os.path.join(APP, "release")
COMPILER = os.path.join(BUILD, "compiler")
ISL = os.path.join(BUILD, "inno_lang", "ChineseSimplified.isl")
ISS = os.path.join(BUILD, "app.iss")
ISCC = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Inno Setup 6", "ISCC.exe")
APPID = "{{6F1B2D74-3A5C-4E8B-9C21-5D7A0E4F6B83}"

VERSION_INFO = f'''VSVersionInfo(
  ffi=FixedFileInfo(filevers={VER_TUPLE}, prodvers={VER_TUPLE}, mask=0x3f, flags=0x0,
                    OS=0x40004, fileType=0x1, subtype=0x0, date=(0,0)),
  kids=[
    StringFileInfo([
      StringTable('080404b0', [
        StringStruct('CompanyName', '{appinfo.AUTHOR["name"]}'),
        StringStruct('FileDescription', 'C 语言学习器'),
        StringStruct('FileVersion', '{VER4}'),
        StringStruct('InternalName', 'CStudy'),
        StringStruct('OriginalFilename', 'C语言学习器.exe'),
        StringStruct('ProductName', 'C 语言学习器'),
        StringStruct('ProductVersion', '{VER4}'),
        StringStruct('LegalCopyright', 'Copyright (C) 2026')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [2052, 1200])])
  ]
)
'''

ISS_TMPL = r'''#define AppName "C 语言学习器"
#define AppVersion "1.0.1"
#define AppExe "C语言学习器.exe"
#define AppPublisher "Naireip"
#define Shortcut "CStudy"

[Setup]
AppId={appid}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\CStudy
DefaultGroupName={#Shortcut}
DisableProgramGroupPage=yes
DisableWelcomePage=no
PrivilegesRequired=lowest
OutputDir={rel}
OutputBaseFilename=CStudy-Setup-{#AppVersion}
SetupIconFile={icon}
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
VersionInfoVersion=1.0.1.0
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} 安装程序
VersionInfoProductName={#AppName}

[Languages]
Name: "zh"; MessagesFile: "{isl}"
Name: "en"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标："; Flags: checkedonce

[Files]
Source: "{onedsrc}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "{compiler}\*"; DestDir: "{app}\compiler"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "{readme}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#Shortcut}"; Filename: "{app}\{#AppExe}"
Name: "{group}\卸载 {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#Shortcut}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "立即运行 {#AppName}"; Flags: nowait postinstall skipifsilent
'''


def sh(cmd, timeout=900):
    print(">", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def build_onedir():
    vi = os.path.join(BUILD, "version_info.txt")
    with open(vi, "w", encoding="utf-8", newline="\n") as f:
        f.write(VERSION_INFO)
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onedir",
        "--name", NAME,
        "--icon", os.path.join(APP, "icon.ico"),
        "--version-file", vi,
        "--add-data", os.path.join(APP, "static") + ";static",
        "--distpath", DIST_ONEDIR,
        "--workpath", os.path.join(BUILD, "pyi_installer"),
        "--specpath", os.path.join(BUILD, "spec_installer"),
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
        print(r.stdout[-1500:])
        print(r.stderr[-3000:])
        sys.exit(1)
    out = os.path.join(DIST_ONEDIR, NAME)
    print("目录版：%s（%.1f MB）" % (out, dirsize(out) / 1048576))
    return out


def dirsize(p):
    t = 0
    for r, d, fs in os.walk(p):
        for n in fs:
            t += os.path.getsize(os.path.join(r, n))
    return t


def make_iss(onedsrc):
    if not os.path.exists(ISCC):
        sys.exit("找不到 Inno Setup 的 ISCC.exe：%s" % ISCC)
    if not os.path.exists(ISL):
        sys.exit("缺少中文字典：%s" % ISL)
    readme = os.path.join(REL, NAME + "-完整版", "使用说明.txt")
    if not os.path.exists(readme):
        sys.exit("缺少使用说明：%s" % readme)
    iss = (ISS_TMPL
           .replace("1.0.1.0", VER4)          # 先换 4 段版号，再换 3 段
           .replace("1.0.1", VERSION)
           .replace("{appid}", APPID)
           .replace("{rel}", REL)
           .replace("{icon}", os.path.join(APP, "icon.ico"))
           .replace("{isl}", ISL)
           .replace("{onedsrc}", onedsrc)
           .replace("{compiler}", COMPILER)
           .replace("{readme}", readme))
    with open(ISS, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(iss)
    print("已生成脚本：", ISS)
    r = sh([ISCC, "/Qp", ISS])
    print(r.stdout.strip()[-800:])
    if r.returncode != 0:
        print(r.stderr[-2000:])
        sys.exit(1)
    setup = os.path.join(REL, "CStudy-Setup-%s.exe" % VERSION)
    if not os.path.exists(setup):
        sys.exit("没生成安装包")
    print("安装包：%s（%.1f MB）" % (setup, os.path.getsize(setup) / 1048576))
    return setup


def wait_api(port, timeout=45):
    for _ in range(timeout):
        time.sleep(1)
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d/api/data" % port, timeout=3) as r:
                return json.loads(r.read().decode())
        except Exception:
            pass
    return None


def self_test(setup):
    testdir = os.path.join(os.environ["TEMP"], "CStudyInstallTest")
    shutil.rmtree(testdir, ignore_errors=True)
    # 数据目录隔离在 testdir 里（CSTUDY_DATA）：绝不能再 rmtree 用户真实的
    # %LOCALAPPDATA%\CStudy —— 那里面是他的 AC 留档和学习进度。
    datadir = os.path.join(testdir, "_userdata")

    log = os.path.join(BUILD, "install.log")
    r = sh([setup, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART",
            "/DIR=" + testdir, "/LOG=" + log], timeout=600)
    print("静默安装返回码:", r.returncode)
    exe = os.path.join(testdir, NAME + ".exe")
    ok = os.path.exists(exe)
    print("  exe 存在:", ok)
    print("  compiler 就绪:", os.path.exists(os.path.join(testdir, "compiler", "bin", "gcc.exe")))
    print("  _internal 存在:", os.path.isdir(os.path.join(testdir, "_internal")))
    print("  使用说明:", os.path.exists(os.path.join(testdir, "使用说明.txt")))
    print("  卸载器:", os.path.exists(os.path.join(testdir, "unins000.exe")))

    env = dict(os.environ, CSTUDY_PORT="8794", CSTUDY_DATA=datadir)
    p = subprocess.Popen([exe], cwd=testdir, env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    d = wait_api(8794)
    print("  API:", "36 节 / %d 测验 / %d OJ" % (len(d["quizzes"]), len(d["oj"])) if d else "没起来")
    verdict = ""
    if d:
        prob = next(x for x in d["oj"] if x["id"] == 1)
        body = json.dumps({"id": 1, "code": prob["reference"]}).encode()
        req = urllib.request.Request("http://127.0.0.1:8794/api/judge", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            verdict = json.loads(resp.read().decode())["verdict"]
        print("  判题:", verdict)
    subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
    time.sleep(1)

    # 打包版的日志必须真的落盘（发给同学后靠它排错）
    logdir = os.path.join(datadir, "logs")
    logfiles = sorted(os.listdir(logdir)) if os.path.isdir(logdir) else []
    logs_ok = any(n.endswith(".log") for n in logfiles)
    print("  运行日志:", ("有 " + ", ".join(logfiles)) if logs_ok else "缺失 ← 打包后日志功能失效")

    # 注册表卸载项
    import winreg
    key = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\{6F1B2D74-3A5C-4E8B-9C21-5D7A0E4F6B83}_is1"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
            name = winreg.QueryValueEx(k, "DisplayName")[0]
            ver = winreg.QueryValueEx(k, "DisplayVersion")[0]
        print("  注册表卸载项:", name, ver)
        reg_ok = True
    except OSError as e:
        print("  注册表卸载项: 缺失", e)
        reg_ok = False

    # 静默卸载
    unins = os.path.join(testdir, "unins000.exe")
    r = sh([unins, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"], timeout=300)
    time.sleep(3)
    print("卸载返回码:", r.returncode, "| 目录还在:", os.path.isdir(testdir),
          "| exe 还在:", os.path.exists(exe))
    cleaned = not os.path.exists(exe)

    shutil.rmtree(testdir, ignore_errors=True)
    return ok and d is not None and verdict == "AC" and cleaned and reg_ok and logs_ok


if __name__ == "__main__":
    onedsrc = os.path.join(DIST_ONEDIR, NAME)
    if "--skip-pyi" in sys.argv and os.path.isdir(onedsrc):
        print("跳过 PyInstaller，直接用已有的目录版：", onedsrc)
    else:
        onedsrc = build_onedir()
    setup = make_iss(onedsrc)
    ok = self_test(setup)
    print("安装包自测：", "通过" if ok else "失败")
    sys.exit(0 if ok else 1)
