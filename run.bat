@echo off
REM 运行程序脚本

echo ================================================
echo AI广告视频生成系统
echo ================================================
echo.

REM 检查依赖是否安装
python -c "import PyQt6" 2>nul
if %errorlevel% neq 0 (
    echo 警告: 依赖包未安装，请先运行 install.bat
    echo.
    pause
    exit /b 1
)

echo 正在启动程序...
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo 程序异常退出，请查看日志文件: logs/app.log
    pause
)
