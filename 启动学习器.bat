@echo off
rem ============================================
rem  启动学习器.bat  C 语言学习器（网页版）
rem  启动本地服务并自动打开浏览器。
rem ============================================
cd /d "%~dp0"

python server.py

if errorlevel 1 (
    echo.
    echo 程序出错了，把上面的报错发给我。
)
pause
