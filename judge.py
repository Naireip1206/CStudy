# -*- coding: utf-8 -*-
"""
judge.py —— OJ 判题器
负责：调 gcc 编译用户写的 .c → 用样例输入跑一遍 → 比对输出 → 给出判题结果。

判题结果五种（学 OJ 必懂的行话）：
    AC  Accepted      通过
    WA  Wrong Answer  答案错误
    CE  Compile Error 编译错误
    TLE Time Limit    超时（可能死循环）
    RE  Runtime Error 运行崩溃
"""

import subprocess
import os
import re
import shutil
import sys


def find_gcc():
    """找一个能用的 gcc：环境变量 → 程序自带 compiler → 打包目录 → 本机常见位置 → PATH。

    便携版把 MinGW 放在 exe 旁边的 compiler\\bin\\gcc.exe；
    开发机上是 D:\\w64devkit\\bin\\gcc.exe；朋友机器上如果装了 MSYS2/MinGW 也能自动用上。
    """
    if os.environ.get("CSTUDY_GCC_DISABLE"):   # 调试用：强制当作"没有编译器"
        return ""
    here = os.path.dirname(os.path.abspath(__file__))
    frozen = bool(getattr(sys, "frozen", False))
    exe_dir = os.path.dirname(os.path.abspath(sys.executable)) if frozen else here
    meipass = getattr(sys, "_MEIPASS", "")

    cands = [
        os.environ.get("CSTUDY_GCC", ""),
        os.path.join(exe_dir, "compiler", "bin", "gcc.exe"),
        os.path.join(exe_dir, "..", "compiler", "bin", "gcc.exe"),
        os.path.join(here, "compiler", "bin", "gcc.exe"),
        os.path.join(meipass, "compiler", "bin", "gcc.exe"),
        r"D:\w64devkit\bin\gcc.exe",
        r"C:\msys64\mingw64\bin\gcc.exe",
        r"C:\MinGW\bin\gcc.exe",
    ]
    for p in cands:
        if p and os.path.isfile(p):
            return os.path.normpath(p)
    found = shutil.which("gcc")
    return found or ""


# 编译用哪个 gcc（启动时算一次；空字符串 = 没找到，判题会给出中文提示）
GCC = find_gcc()

NO_GCC_MSG = ("找不到 C 编译器（gcc）。\n"
              "完整版请确认程序旁边有 compiler 文件夹；\n"
              "也可以装个 MinGW/MSYS2，或设置环境变量 CSTUDY_GCC 指向 gcc.exe。\n"
              "课程和测验不需要编译器，可以正常用。")

# 判题结果的中文说明
VERDICT_TEXT = {
    "AC":  "通过",
    "WA":  "答案错误",
    "CE":  "编译错误",
    "TLE": "超时",
    "RE":  "运行错误",
}


def compile_c(src_path, exe_path):
    """编译 src_path 成 exe_path。
    返回 (ok, error_text)。ok=True 编译成功，否则 error_text 是报错信息。"""
    try:
        r = subprocess.run(
            [GCC, src_path, "-std=gnu99", "-O2", "-o", exe_path],
            capture_output=True, text=True, timeout=30,
        )
    except FileNotFoundError:
        return False, NO_GCC_MSG
    except subprocess.TimeoutExpired:
        return False, "编译超时（不正常，检查编译器）。"

    if r.returncode == 0:
        return True, ""
    return False, translate_gcc_error(r.stderr)


def run_program(exe_path, input_text, time_limit=2):
    """运行编译好的程序，喂入 input_text，限时 time_limit 秒。
    返回 (verdict, stdout, stderr)。"""
    try:
        r = subprocess.run(
            [exe_path],
            input=input_text,
            capture_output=True, text=True,
            timeout=time_limit,
        )
    except subprocess.TimeoutExpired:
        return "TLE", "", "运行超过 %d 秒，可能是死循环。" % time_limit

    if r.returncode != 0:
        return "RE", "", "程序异常退出（退出码 %d），可能数组越界或除 0。" % r.returncode

    return "OK", r.stdout, r.stderr


def tokens(s):
    """把一个字符串按空白切成一串 token，用于忽略多余空格/换行。"""
    return s.split()


def judge(src_path, problem):
    """完整判题：编译 + 跑所有样例 + 比对。
    返回一个 dict：{verdict, message, detail}。"""
    if not GCC:
        return {"verdict": "CE", "message": NO_GCC_MSG, "detail": ""}
    exe_path = os.path.splitext(src_path)[0] + ".exe"

    # 1) 编译
    ok, err = compile_c(src_path, exe_path)
    if not ok:
        return {"verdict": "CE", "message": err, "detail": ""}

    # 2) 逐个样例跑
    results = []
    all_pass = True
    for i, s in enumerate(problem["samples"], 1):
        verdict, stdout, stderr = run_program(exe_path, s["input"], problem.get("time_limit", 2))
        if verdict == "TLE":
            all_pass = False
            results.append({"no": i, "verdict": "TLE", "info": stderr})
            break
        if verdict == "RE":
            all_pass = False
            results.append({"no": i, "verdict": "RE", "info": stderr})
            break
        # 比对输出（忽略多余空白）
        if tokens(stdout) == tokens(s["output"]):
            results.append({"no": i, "verdict": "AC", "info": ""})
        else:
            all_pass = False
            results.append({
                "no": i, "verdict": "WA", "info": "",
                "actual": stdout.strip(), "expected": s["output"].strip(),
            })

    if all_pass:
        return {"verdict": "AC", "message": "全部样例通过！", "detail": results}
    return {"verdict": "WA", "message": "有样例没通过，看下面细节。", "detail": results}


# ============================================================
# gcc 报错中文化：把英文报错翻译成好懂的提示
# ============================================================
def translate_gcc_error(err_text):
    """解析 gcc 的 stderr，提取 error 行并翻译成中文。"""
    lines = []
    for line in err_text.splitlines():
        # 只关心 error 和 warning 行
        m = re.search(r"^(.*?):(\d+):(\d+):\s*(error|warning):\s*(.*)$", line)
        if m:
            file_name = os.path.basename(m.group(1))
            line_no = m.group(2)
            col_no = m.group(3)
            kind = m.group(4)
            msg = m.group(5)
            cn = _translate_msg(msg)
            prefix = "错误" if kind == "error" else "警告"
            lines.append(f"第 {line_no} 行：{cn}")
    if not lines:
        # 没匹配到标准格式，原样返回前几行
        return "编译失败，原始报错：\n" + err_text[:500]
    return "编译失败：\n" + "\n".join(lines[:8])


def _translate_msg(msg):
    """把一条 gcc 错误消息翻译成中文。用关键词匹配，尽量覆盖常见错误。"""
    if "expected ';' before" in msg or "expected ';'" in msg:
        return "少了分号 ;"
    if "expected '}' before" in msg or "expected '}'" in msg:
        return "少了右大括号 }（检查是否成对）"
    if "expected ')' before" in msg:
        return "少了右括号 )"
    if "expected declaration or statement at end of input" in msg:
        return "文件末尾缺东西，通常是少了右大括号 }"
    if "undeclared" in msg and "first use" in msg:
        name = re.search(r"'(\w+)'", msg)
        return ("变量没声明就用了" + (f"（{name.group(1)}）" if name else "") +
                "：先定义再使用，或检查拼写 / 是否忘了 #include")
    if "lvalue required as left operand" in msg:
        return "赋值号左边不是变量，可能是把 == 写成 = 了"
    if "stray '\\" in msg:
        return "代码里混进了中文字符或全角符号（如中文逗号、中文括号）"
    if "implicit declaration" in msg:
        return "函数没声明就调用，可能忘了 #include 对应头文件"
    if "expected 'while'" in msg:
        return "do-while 循环少了结尾的 while"
    if "conflicting types" in msg:
        return "同一个函数/变量的类型前后不一致"
    if "unknown type name" in msg:
        name = re.search(r"'(\w+)'", msg)
        return ("类型名不认识" + (f"（{name.group(1)}）" if name else "") +
                "：拼写错了，或忘了 #include")
    if "expected expression before" in msg:
        return "这里缺一个表达式，检查上一行是否漏了分号或括号"
    if "dereferencing pointer to incomplete type" in msg:
        return "用了未完整定义的结构体，忘了 #include 或没定义"
    if "too few arguments" in msg:
        return "函数调用时参数给少了"
    if "too many arguments" in msg:
        return "函数调用时参数给多了"
    # 兜底：返回原文（截断）
    return msg
