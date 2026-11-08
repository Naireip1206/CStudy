# -*- coding: utf-8 -*-
"""
server.py —— C 语言学习器（网页版）本地服务
零依赖：Python 标准库 http.server 起本地服务，浏览器打开界面。
内容（课程/测验/OJ 题）直接读 data.py + answers.py，出题就是改这两个文件。
判题逻辑复用 judge.py。
"""

import http.server
import json
import os
import subprocess
import threading
import time
import webbrowser
import datetime
import sys

import appinfo
import applog
import data
import judge
import answers

# 是否运行在 PyInstaller 打包出来的 exe 里
FROZEN = bool(getattr(sys, "frozen", False))

if FROZEN:
    # 单文件 exe：静态资源被解包到临时目录；用户数据写到 AppData，重装/移动 exe 都不丢
    ASSET_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    # CSTUDY_DATA 只给打包自测用：把数据目录指到临时目录，别碰用户真实学习数据
    USER_DIR = (os.environ.get("CSTUDY_DATA")
                or os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "CStudy"))
else:
    ASSET_DIR = os.path.dirname(os.path.abspath(__file__))
    USER_DIR = ASSET_DIR

STATIC_DIR = os.path.join(ASSET_DIR, "static")
OJ_DIR = os.path.join(USER_DIR, "oj")
AC_DIR = os.path.join(USER_DIR, "ac")          # 通过（AC）的代码留档
PROGRESS_FILE = os.path.join(USER_DIR, "progress.json")
os.makedirs(USER_DIR, exist_ok=True)
os.makedirs(AC_DIR, exist_ok=True)

PORT = int(os.environ.get("CSTUDY_PORT") or 8765)

# 日志：文件在 <数据目录>\logs\，按天切、留 7 天
LOG = applog.setup(appinfo.VERSION, data_dir=USER_DIR, extra_info=[
    "数据目录=%s" % USER_DIR,
    "静态资源=%s" % STATIC_DIR,
    "端口=%d" % PORT,
    "编译器=%s" % (judge.GCC or "（没找到，OJ 不能判题）"),
])

progress = {"days": 0, "last": "", "lessons": {}, "oj": {}, "ac": {}, "submissions": [],
            "quiz_wrong": [], "notes": {"quiz": {}, "oj": {}}}

OJ_TEMPLATE = '#include <stdio.h>\n\nint main(void) {\n    // 在这里写你的代码\n    return 0;\n}\n'


# ============================================================
# 进度读写（progress.json）
# ============================================================
def load_progress():
    global progress
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                progress = json.load(f)
            progress.setdefault("submissions", [])
            progress.setdefault("quiz_wrong", [])
            progress.setdefault("ac", {})
            progress.setdefault("notes", {"quiz": {}, "oj": {}})
            LOG.info("读回进度：%d 节课 / %d 道 OJ 有记录 / AC %d 道 / 提交 %d 次",
                     len(progress.get("lessons", {})), len(progress.get("oj", {})),
                     len(progress.get("ac", {})), len(progress.get("submissions", [])))
        except Exception:
            # 进度文件坏了：先备份再继续，至少别把用户数据直接冲掉
            LOG.exception("读 progress.json 失败，已备份坏文件并用空进度启动")
            try:
                bad = PROGRESS_FILE + ".broken-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                os.replace(PROGRESS_FILE, bad)
                LOG.warning("坏文件已另存：%s", bad)
            except OSError:
                LOG.exception("备份坏进度文件也失败了")


def save_progress():
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    except Exception:
        LOG.exception("写 progress.json 失败（进度可能丢失）：%s", PROGRESS_FILE)
        raise


def add_day():
    today = datetime.date.today().strftime("%Y%m%d")
    if today != progress.get("last", ""):
        progress["days"] = progress.get("days", 0) + 1
        progress["last"] = today
        save_progress()


def get_oj_src(pid):
    if not os.path.exists(OJ_DIR):
        os.makedirs(OJ_DIR)
    path = os.path.join(OJ_DIR, f"problem_{pid}.c")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(OJ_TEMPLATE)
    return path


def read_oj_code(pid):
    with open(get_oj_src(pid), "r", encoding="utf-8") as f:
        return f.read()


# ============================================================
# AC 代码留档（通过了就把代码存一份，随时能翻）
# ============================================================
def find_uninstaller():
    """安装版才有 unins000.exe；便携版返回空字符串。"""
    if not FROZEN:
        return ""
    d = os.path.dirname(os.path.abspath(sys.executable))
    p = os.path.join(d, "unins000.exe")
    return p if os.path.isfile(p) else ""


def save_ac(pid, code):
    """把通过（AC）的代码写到 ac/problem_N.c，并在进度里记下首次/最近通过时间。
    以后改到 WA 也不覆盖这份留档，直到你再次 AC。"""
    path = os.path.join(AC_DIR, f"problem_{pid}.c")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(code if code.endswith("\n") else code + "\n")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    rec = progress.setdefault("ac", {}).setdefault(str(pid), {})
    if not rec.get("first"):
        rec["first"] = now
    rec["last"] = now
    rec["count"] = int(rec.get("count", 0)) + 1
    rec["lines"] = code.count("\n") + 1


def read_all_ac():
    """返回 {pid: {code, first, last, count, lines}}，给前端"通过代码"页用。"""
    out = {}
    meta = progress.get("ac", {})
    if os.path.isdir(AC_DIR):
        for name in os.listdir(AC_DIR):
            if not (name.startswith("problem_") and name.endswith(".c")):
                continue
            try:
                pid = int(name[len("problem_"):-2])
                with open(os.path.join(AC_DIR, name), "r", encoding="utf-8") as f:
                    code = f.read()
            except (ValueError, OSError):
                continue
            m = meta.get(str(pid), {})
            out[str(pid)] = {
                "code": code,
                "first": m.get("first", ""),
                "last": m.get("last", ""),
                "count": m.get("count", 1),
                "lines": code.count("\n") + (0 if code.endswith("\n") else 1),
            }
    return out


# ============================================================
# HTTP 处理
# ============================================================
class AppServer(http.server.ThreadingHTTPServer):
    """Windows 上 allow_reuse_address=True 会让两个进程绑同一个端口（不报错），
    这里关掉，端口被占时才能真正抛错、让主程序顺延到下一个端口。"""

    allow_reuse_address = False
    daemon_threads = True


class Handler(http.server.BaseHTTPRequestHandler):
    # BaseHTTPRequestHandler 自己也会调 log_message（send_response 时），
    # 但那里拿不到耗时和异常，所以统一在 _dispatch 里记一条完整日志。
    def log_message(self, fmt, *args):
        pass

    def _mark(self, code):
        self._status = code

    def _serve_file(self, name, ctype):
        full = os.path.join(STATIC_DIR, name)
        try:
            with open(full, "rb") as f:
                body = f.read()
        except OSError:
            LOG.warning("静态文件缺失：%s", full)
            self._mark(404)
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        # 本地开发：改完样式/脚本刷新就能生效，别让浏览器拿缓存
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self._mark(200)

    def _send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self._mark(code)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _dispatch(self, impl):
        """统一入口：计时 + 兜住异常 + 落日志。任何情况下都不让请求悄悄消失。"""
        self._status = "-"
        t0 = time.perf_counter()
        try:
            impl()
        except (BrokenPipeError, ConnectionResetError):
            LOG.debug("%s %s 客户端提前断开（页面关了或刷新了）", self.command, self.path)
        except Exception:
            LOG.exception("处理 %s %s 时抛出未捕获异常", self.command, self.path)
            self._status = 500
            try:
                self.send_error(500)
            except Exception:                          # noqa: BLE001
                pass
        finally:
            ms = (time.perf_counter() - t0) * 1000
            LOG.info("%s %s -> %s (%.0f ms)", self.command, self.path, self._status, ms)

    def do_GET(self):
        self._dispatch(self._get_impl)

    def do_POST(self):
        self._dispatch(self._post_impl)

    def _get_impl(self):
        route = self.path.split("?")[0]
        if route in ("/", "/index.html"):
            self._serve_file("index.html", "text/html; charset=utf-8")
        elif route == "/style.css":
            self._serve_file("style.css", "text/css; charset=utf-8")
        elif route == "/app.js":
            self._serve_file("app.js", "text/javascript; charset=utf-8")
        elif route in ("/icon.ico", "/favicon.ico"):
            self._serve_file("icon.ico", "image/x-icon")
        elif route.startswith("/vendor/"):
            name = route[len("/vendor/"):]
            ctype = "text/css" if name.endswith(".css") else "text/javascript"
            self._serve_file("vendor/" + name, ctype + "; charset=utf-8")
        elif route == "/api/data":
            oj_codes = {str(p["id"]): read_oj_code(p["id"]) for p in data.OJ_PROBLEMS}
            oj_list = []
            for p in data.OJ_PROBLEMS:
                p2 = dict(p)
                ans = answers.ANSWERS.get(p["id"], {})
                p2["reference"] = ans.get("reference", "")
                p2["best"] = ans.get("best", "")
                oj_list.append(p2)
            self._send_json({
                "lessons": data.LESSONS,
                "quizzes": data.QUIZZES,
                "oj": oj_list,
                "oj_codes": oj_codes,
                "ac": read_all_ac(),
                "app": {
                    "version": appinfo.VERSION,
                    "build": appinfo.BUILD_DATE,
                    "name": appinfo.APP_NAME,
                    "author": appinfo.AUTHOR,
                    "uninstaller": find_uninstaller(),
                    "frozen": FROZEN,
                    "data_dir": USER_DIR,
                    "log_dir": applog.LOG_DIR,
                },
                "progress": progress,
            })
        elif route.startswith("/api/open/"):
            try:
                pid = int(route.rsplit("/", 1)[1])
                os.startfile(get_oj_src(pid))
                LOG.info("用系统编辑器打开 OJ #%d 源码", pid)
                self._send_json({"ok": True})
            except Exception:
                LOG.exception("打开 OJ 源码失败：%s", route)
                self._send_json({"ok": False})
        elif route == "/api/logs":
            # 关于页「查看日志」用：返回最近 N 行
            n = 200
            if "?" in self.path:
                for kv in self.path.split("?", 1)[1].split("&"):
                    if kv.startswith("n="):
                        try:
                            n = max(20, min(2000, int(kv[2:])))
                        except ValueError:
                            pass
            self._send_json({"path": applog.LOG_FILE, "dir": applog.LOG_DIR,
                             "lines": applog.tail(n)})
        else:
            self._mark(404)
            self.send_error(404)

    def _post_impl(self):
        route = self.path.split("?")[0]
        if route == "/api/judge":
            self._handle_judge()
        elif route == "/api/uninstall":
            self._handle_uninstall()
        elif route == "/api/progress":
            self._handle_progress()
        elif route == "/api/log":
            self._handle_client_log()
        elif route == "/api/open-log":
            self._handle_open_log()
        else:
            self._mark(404)
            self.send_error(404)

    # ------------------------------------------------------------
    # 日志相关接口
    # ------------------------------------------------------------
    def _handle_client_log(self):
        """前端（浏览器）主动上报：JS 报错、判题请求失败等。

        这是排查「页面点了没反应」最有用的一条 —— 后端根本不知道前端崩了。"""
        try:
            body = self._read_json()
        except Exception:
            body = {}
        level = str(body.get("level", "ERROR")).upper()
        source = str(body.get("source", "web"))[:40]
        message = str(body.get("message", ""))[:2000]
        stack = str(body.get("stack", ""))[:3000]
        where = str(body.get("where", ""))[:200]
        text = "[前端:%s] %s%s" % (source, message, ("  @ " + where) if where else "")
        if stack:
            text += "\n" + stack
        if level == "INFO":
            LOG.info(text)
        elif level == "WARNING":
            LOG.warning(text)
        else:
            LOG.error(text)
        self._send_json({"ok": True})

    def _handle_open_log(self):
        """在资源管理器里打开日志文件夹。"""
        try:
            os.startfile(applog.LOG_DIR)
            LOG.info("打开日志文件夹：%s", applog.LOG_DIR)
            self._send_json({"ok": True, "dir": applog.LOG_DIR})
        except Exception as exc:                       # noqa: BLE001
            LOG.exception("打开日志文件夹失败")
            self._send_json({"ok": False, "message": str(exc)})

    def _handle_judge(self):
        """判题入口：任何异常都要给前端一个 JSON，别让页面干等。"""
        try:
            self._judge_impl()
        except Exception as exc:                      # noqa: BLE001
            LOG.exception("判题接口内部异常（已返回 CE 给前端）")
            try:
                self._send_json({"verdict": "CE",
                                 "message": "判题服务内部出错：%s" % exc,
                                 "detail": "", "progress": progress, "ac": read_all_ac()})
            except Exception:
                LOG.exception("连错误 JSON 都发不回去了")

    def _judge_impl(self):
        t0 = time.perf_counter()
        body = self._read_json()
        pid = int(body.get("id", 0))
        code = body.get("code", "")
        problem = next((p for p in data.OJ_PROBLEMS if p["id"] == pid), None)
        if problem is None:
            LOG.warning("判题请求里的题号不存在：%r", body.get("id"))
            self._send_json({"error": "题目不存在"}, 404)
            return
        src = get_oj_src(pid)
        with open(src, "w", encoding="utf-8") as f:
            f.write(code)
        result = judge.judge(src, problem)
        ms = (time.perf_counter() - t0) * 1000
        verdict = result["verdict"]
        LOG.info("判题 #%d（%s）→ %s，%.0f ms，代码 %d 行",
                 pid, problem.get("title", ""), verdict, ms, code.count("\n") + 1)
        if verdict == "CE":
            # 编译错误是学生最常见的求助点，把翻译后的提示记下来（判题器已经翻成中文）
            LOG.warning("判题 #%d 判定 CE：%s", pid, result.get("message", ""))
        elif verdict == "WA":
            fails = [r for r in (result.get("detail") or []) if r.get("verdict") != "AC"]
            LOG.info("判题 #%d 有 %d 个样例没过（第一个：#%s %s）", pid, len(fails),
                     fails[0].get("no") if fails else "-", fails[0].get("verdict") if fails else "-")
        progress["oj"][str(pid)] = result["verdict"]
        if verdict == "AC":
            save_ac(pid, code)          # 通过了就把这份代码留档
            LOG.info("判题 #%d 通过，代码已留档到 %s", pid, AC_DIR)
        progress.setdefault("submissions", []).append({
            "time": datetime.datetime.now().strftime("%m-%d %H:%M:%S"),
            "pid": pid,
            "verdict": result["verdict"],
            "code": code,
            "message": result["message"],
            "detail": result["detail"],
        })
        if len(progress["submissions"]) > 300:      # 别让 progress.json 无限膨胀
            progress["submissions"] = progress["submissions"][-300:]
        save_progress()
        self._send_json({
            "verdict": result["verdict"],
            "message": result["message"],
            "detail": result["detail"],
            "ac": read_all_ac(),
            "progress": progress,
        })

    def _handle_uninstall(self):
        """关于页的「卸载」按钮：安装版直接拉起 Inno 的卸载程序。"""
        path = find_uninstaller()
        if not path:
            self._send_json({"ok": False, "message": "便携版没有卸载程序，直接删掉程序文件夹即可（学习进度在 %s）" % USER_DIR})
            return
        try:
            subprocess.Popen([path], cwd=os.path.dirname(path),
                             creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))
            LOG.info("已拉起卸载程序：%s", path)
        except Exception as exc:                      # noqa: BLE001
            LOG.exception("启动卸载程序失败：%s", path)
            self._send_json({"ok": False, "message": "启动卸载程序失败：%s" % exc})
            return
        self._send_json({"ok": True, "message": "卸载程序已启动，按向导走完即可；本页面可以关掉了。"})
        # 卸载器要删掉本程序，先让服务自己退出
        threading.Timer(1.5, lambda: os._exit(0)).start()

    def _handle_progress(self):
        global progress
        body = self._read_json()
        changed = []
        if "lessons" in body:
            progress["lessons"] = body["lessons"]
            changed.append("lessons")
        if "oj" in body:
            progress["oj"] = body["oj"]
            changed.append("oj")
        if "quiz_wrong" in body:
            progress["quiz_wrong"] = body["quiz_wrong"]
            changed.append("quiz_wrong")
        if "notes" in body:
            progress["notes"] = body["notes"]
            changed.append("notes")
        save_progress()
        LOG.debug("保存进度：%s", ",".join(changed) or "（没有可保存的字段）")
        self._send_json({"ok": True, "progress": progress})


def main():
    load_progress()
    add_day()

    # 端口被占用（比如开过两次）就顺延，避免启动失败
    server = None
    port = PORT
    for cand in range(PORT, PORT + 20):
        try:
            server = AppServer(("127.0.0.1", cand), Handler)
            port = cand
            break
        except OSError as exc:
            LOG.warning("端口 %d 被占用，换下一个（%s）", cand, exc)
            continue
    if server is None:
        LOG.error("端口 %d~%d 全被占用，启动失败", PORT, PORT + 19)
        print("端口 %d~%d 都被占用了，启动失败。" % (PORT, PORT + 19))
        input("按回车退出……")
        return
    if port != PORT:
        LOG.info("端口顺延：%d → %d", PORT, port)

    url = "http://127.0.0.1:%d/" % port
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    LOG.info("服务已就绪：%s", url)

    print("=" * 56)
    print("  C 语言学习器  ·  36 节课 / 72 道测验 / 36 道 OJ")
    print("  网址：%s" % url)
    if judge.GCC:
        print("  编译器：已就绪（OJ 可以判题）")
    else:
        print("  编译器：未找到 —— OJ 暂时不能判题，课程和测验正常")
        print("          完整版请确认 exe 旁边有 compiler 文件夹")
    print("  存档目录：%s" % USER_DIR)
    print("  运行日志：%s" % applog.LOG_DIR)
    print("  关掉这个黑窗口 = 退出程序")
    print("=" * 56)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOG.info("收到 Ctrl+C，程序退出")
    except Exception:
        LOG.exception("服务主循环异常退出")
        raise
    finally:
        try:
            server.server_close()
        except Exception:                          # noqa: BLE001
            pass
        LOG.info("服务已关闭")


if __name__ == "__main__":
    main()
