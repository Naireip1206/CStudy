# -*- coding: utf-8 -*-
"""verify_installer.py —— 安装包的真实用户路径验证

1) 用默认安装目录（%LOCALAPPDATA%\\Programs\\CStudy）静默安装一次
2) 检查开始菜单/桌面快捷方式、注册表、文件完整性
3) 测「目录版」和「单文件版」的启动到可用耗时
4) 静默卸载，确认清干净（快捷方式、目录、注册表）
"""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import winreg

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP)
import appinfo          # noqa: E402
VER = appinfo.VERSION
REL = os.path.join(APP, "release")
SETUP = os.path.join(REL, "CStudy-Setup-%s.exe" % VER)
TARGET = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "CStudy")
NAME = "C语言学习器"

ok = True


def check(name, cond, extra=""):
    global ok
    print(("  %-36s %s %s" % (name, "OK" if cond else "!! 失败", extra)).rstrip())
    ok = ok and cond


def wait_ready(exe, port, env_extra=None):
    env = dict(os.environ, CSTUDY_PORT=str(port), **(env_extra or {}))
    t0 = time.time()
    p = subprocess.Popen([exe], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(120):
        time.sleep(0.25)
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d/api/data" % port, timeout=2) as r:
                r.read()
            dt = time.time() - t0
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
            return dt
        except Exception:
            pass
    subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
    return None


def desktop():
    return subprocess.run(
        ["powershell", "-NoProfile", "-Command", "[Environment]::GetFolderPath('Desktop')"],
        capture_output=True, text=True).stdout.strip()


print("[1] 默认目录静默安装")
shutil.rmtree(TARGET, ignore_errors=True)
r = subprocess.run([SETUP, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"], timeout=600)
check("安装返回码 0", r.returncode == 0, str(r.returncode))
check("装到 %LOCALAPPDATA%\\Programs\\CStudy", os.path.isdir(TARGET), TARGET)
check("exe 存在", os.path.exists(os.path.join(TARGET, NAME + ".exe")))
check("compiler 存在", os.path.exists(os.path.join(TARGET, "compiler", "bin", "gcc.exe")))

print("[2] 快捷方式 / 注册表")
desk_lnk = os.path.join(desktop(), "CStudy.lnk")
start_lnk = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu",
                         "Programs", "CStudy", "CStudy.lnk")
check("桌面快捷方式", os.path.exists(desk_lnk), desk_lnk)
check("开始菜单项", os.path.exists(start_lnk), start_lnk)
try:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Uninstall"
                        r"\{6F1B2D74-3A5C-4E8B-9C21-5D7A0E4F6B83}_is1") as k:
        dn = winreg.QueryValueEx(k, "DisplayName")[0]
        loc = winreg.QueryValueEx(k, "InstallLocation")[0]
        sz = winreg.QueryValueEx(k, "EstimatedSize")[0]
    check("控制面板卸载项", dn == "C 语言学习器", "%s | %.1f MB" % (dn, sz / 1024))
    check("InstallLocation 正确", os.path.normcase(loc) == os.path.normcase(TARGET + "\\"), loc)
except OSError as e:
    check("控制面板卸载项", False, str(e))

print("[3] 启动耗时对比（到 API 可用）")
t_dir = wait_ready(os.path.join(TARGET, NAME + ".exe"), 8796)
t_one = wait_ready(os.path.join(REL, NAME + "-精简版.exe"), 8797)
print("  目录版(安装)：%.2f 秒 | 单文件版(exe)：%s 秒" % (t_dir or -1, "%.2f" % t_one if t_one else "超时"))
check("目录版启动 < 3 秒", t_dir is not None and t_dir < 3.0)

print("[3.5] 安装版的「关于」页（卸载按钮 / 版本）")
env = dict(os.environ, CSTUDY_PORT="8799")
p = subprocess.Popen([os.path.join(TARGET, NAME + ".exe")], env=env,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
info = None
for _ in range(40):
    time.sleep(0.5)
    try:
        with urllib.request.urlopen("http://127.0.0.1:8799/api/data", timeout=2) as r:
            info = json.loads(r.read().decode())["app"]
        break
    except Exception:
        pass
check("API 报告已安装（frozen）", bool(info) and info.get("frozen") is True)
check("API 给了卸载器路径", bool(info) and os.path.isfile(info.get("uninstaller", "")),
      (info or {}).get("uninstaller", ""))
check("版本 %s" % VER, (info or {}).get("version") == VER, (info or {}).get("version", ""))
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(channel="msedge", headless=True)
        page = b.new_page(viewport={"width": 1280, "height": 900})
        page.goto("http://127.0.0.1:8799/", wait_until="networkidle")
        page.click("text=关于")
        page.wait_for_timeout(500)
        check("安装版关于页有卸载按钮", page.query_selector("#uninstall") is not None)
        page.screenshot(path=os.path.join(APP, "_verify", "ui_about_installed.png"))
        b.close()
except Exception as e:
    check("安装版关于页", False, str(e)[:120])
subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
time.sleep(1)

print("[4] 静默卸载")
r = subprocess.run([os.path.join(TARGET, "unins000.exe"), "/VERYSILENT", "/SUPPRESSMSGBOXES",
                    "/NORESTART"], timeout=300)
time.sleep(3)
check("卸载返回码 0", r.returncode == 0, str(r.returncode))
check("安装目录已删除", not os.path.isdir(TARGET))
check("桌面快捷方式已删除", not os.path.exists(desk_lnk))
check("开始菜单已删除", not os.path.isdir(os.path.dirname(start_lnk)))

# 清掉测试产生的学习进度
shutil.rmtree(os.path.join(os.environ["LOCALAPPDATA"], "CStudy"), ignore_errors=True)
print("验证:", "通过" if ok else "有问题")
sys.exit(0 if ok else 1)
