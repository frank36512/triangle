@echo off
REM 在虚拟环境中运行程序

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo 错误: 虚拟环境不存在，请先运行 setup_venv.bat
    echo.
    pause
    exit /b 1
)

echo ================================================
echo AI广告视频生成系统 (虚拟环境)
echo ================================================
echo.

REM 激活虚拟环境并运行程序
call venv\Scripts\activate.bat

REM 检查依赖是否安装
python -c "import PyQt6" 2>nul
if %errorlevel% neq 0 (
    echo 警告: 依赖包未安装，请先运行 install_venv.bat
    echo.
    call venv\Scripts\deactivate.bat
    pause
    exit /b 1
)

echo 正在启动程序...
echo.
python main.py

REM 退出虚拟环境
call venv\Scripts\deactivate.bat

if %errorlevel% neq 0 (
    echo.
    echo 程序异常退出，请查看日志文件: logs/app.log
    pause
)
