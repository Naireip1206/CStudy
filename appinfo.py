# -*- coding: utf-8 -*-
"""appinfo.py —— 软件元信息（版本号、作者），改版号只改这里

server.py（关于页 / 页面标题）、build_installer.py（安装包文件名、exe 版本信息）
都从这里取，避免版本号写得到处都是。
"""

VERSION = "1.1.0"
BUILD_DATE = "2026-11-08"

APP_NAME = "C 语言学习器"
SHORTCUT_NAME = "CStudy"          # 桌面 / 开始菜单快捷方式的名字

# 关于页展示的作者信息：只放名字和联系方式，其它一律不写
AUTHOR = {
    "name": "Naireip",
    "avatar": "N",
    "qq": "1302212726",
    "note": "自学 C 语言时做的练习软件，顺手做成了能发给同学的样子。",
    "stack": ["Python 标准库（http.server）", "CodeMirror 编辑器", "MinGW-w64 gcc 判题", "Claude / DeepSeek 辅助生成"],
}
