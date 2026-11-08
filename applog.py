# -*- coding: utf-8 -*-
"""
applog.py —— 统一日志（只用标准库 logging，零依赖）

为什么要有它：
    软件发给同学后，出问题只能看到「判题服务内部出错」这么一句话，
    查不到是编译失败、端口占用还是前端 JS 崩了。这个模块把所有关键动作、
    异常堆栈、前端报错统一落到一个文件里，出问题让同学把日志发回来就行。

日志位置（和 progress.json 同一个数据目录）：
    安装版：%LOCALAPPDATA%\\CStudy\\logs\\cstudy-YYYYMMDD.log
    开发版：<程序目录>\\logs\\cstudy-YYYYMMDD.log
    文件名按天切，保留最近 7 天；单条消息过长会截断，避免一条堆栈吃掉几十 KB。

用法：
    import applog
    LOG = applog.setup("1.1.0")      # 在程序最开头调用一次
    LOG.info("...")
    LOG.exception("...")             # 在 except 里用，自带堆栈
"""

import logging
import os
import sys
import threading
import time
import datetime

LOGGER_NAME = "cstudy"
_initialized = False
LOG_DIR = ""
LOG_FILE = ""
MAX_MSG = 4000          # 单条日志最多保留多少字符
KEEP_DAYS = 7           # 保留几天


def _base_dir():
    """和 server.py 保持一致的数据目录：打包后写 AppData，开发时写程序目录。"""
    if getattr(sys, "frozen", False):
        root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(root, "CStudy")
    return os.path.dirname(os.path.abspath(__file__))


def _trim(text, limit=MAX_MSG):
    text = str(text)
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...（已截断，原有 %d 字符）" % len(text)


def _cleanup(directory):
    """删掉超过 KEEP_DAYS 天的旧日志。"""
    try:
        cutoff = time.time() - KEEP_DAYS * 86400
        for name in os.listdir(directory):
            if not (name.startswith("cstudy-") and name.endswith(".log")):
                continue
            path = os.path.join(directory, name)
            try:
                if os.path.getmtime(path) < cutoff:
                    os.remove(path)
            except OSError:
                pass
    except OSError:
        pass


class _Formatter(logging.Formatter):
    def format(self, record):
        # 消息里可能带换行（gcc 报错、堆栈），统一缩进，日志文件才好看
        msg = record.getMessage()
        if "\n" in msg:
            msg = msg.replace("\n", "\n" + " " * 30)
        record.msg = _trim(msg)
        record.args = ()
        return super().format(record)


def setup(version="", extra_info=None, data_dir=None):
    """配置日志，返回 logger。重复调用是安全的（只生效一次）。

    data_dir：日志写到这个目录下的 logs\\；不传就按 server.py 的规则自己算。
    """
    global _initialized, LOG_DIR, LOG_FILE
    LOG = logging.getLogger(LOGGER_NAME)
    if _initialized:
        return LOG

    LOG_DIR = os.path.join(data_dir or _base_dir(), "logs")
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except OSError:
        LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(LOG_DIR, exist_ok=True)
    LOG_FILE = os.path.join(LOG_DIR, "cstudy-%s.log" % datetime.date.today().strftime("%Y%m%d"))

    LOG.setLevel(logging.DEBUG)
    LOG.propagate = False

    fmt = _Formatter(
        fmt="%(asctime)s.%(msecs)03d %(levelname)-5s [%(threadName)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1) 文件：按天切，保留 7 天
    try:
        from logging.handlers import TimedRotatingFileHandler
        fh = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=KEEP_DAYS,
                                      encoding="utf-8", delay=True)
        fh.setFormatter(fmt)
        fh.setLevel(logging.DEBUG)
        LOG.addHandler(fh)
    except Exception:                                  # noqa: BLE001
        pass                                          # 文件写不了也不能让程序起不来

    # 2) 控制台：exe 有黑窗口时能看到，没有 stdout 就跳过
    try:
        if sys.stdout is not None:
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(fmt)
            ch.setLevel(logging.INFO)
            LOG.addHandler(ch)
    except Exception:                                  # noqa: BLE001
        pass

    _cleanup(LOG_DIR)
    _install_hooks(LOG)
    _initialized = True

    LOG.info("=" * 60)
    LOG.info("启动 C 语言学习器 %s", version or "")
    LOG.info("Python %s | %s", sys.version.split()[0], sys.platform)
    LOG.info("frozen=%s | 程序目录=%s", bool(getattr(sys, "frozen", False)),
             os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__)))
    LOG.info("日志文件：%s", LOG_FILE)
    for line in (extra_info or []):
        LOG.info(line)
    return LOG


def _install_hooks(LOG):
    """未捕获的异常也写进日志——不然程序一闪退什么都没留下。"""

    def excepthook(exc_type, exc, tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc, tb)
            return
        LOG.critical("未捕获的异常：", exc_info=(exc_type, exc, tb))
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = excepthook

    if hasattr(threading, "excepthook"):
        def thread_hook(args):
            if args.exc_type is SystemExit:
                return
            LOG.critical("线程 %s 未捕获异常：", getattr(args.thread, "name", "?"),
                         exc_info=(args.exc_type, args.exc_value, args.exc_traceback))
        threading.excepthook = thread_hook


def get():
    """拿 logger（没 setup 过也能用，只是不落文件）。"""
    return logging.getLogger(LOGGER_NAME)


def tail(lines=200):
    """读当前日志文件最后 N 行，给「关于」页展示用。"""
    path = LOG_FILE or os.path.join(_base_dir(), "logs")
    if os.path.isdir(path):
        try:
            names = sorted(n for n in os.listdir(path) if n.startswith("cstudy-"))
            if not names:
                return []
            path = os.path.join(path, names[-1])
        except OSError:
            return []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            data = f.readlines()
    except OSError:
        return []
    return [ln.rstrip("\n") for ln in data[-lines:]]
