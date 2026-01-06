@echo off
REM 在虚拟环境中安装依赖

echo ================================================
echo AI广告视频生成系统 - 虚拟环境依赖安装
echo ================================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo 错误: 虚拟环境不存在，请先运行 setup_venv.bat 创建虚拟环境
    echo.
    pause
    exit /b 1
)

echo 正在激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo 正在安装依赖包...
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo 错误: 依赖安装失败
    call venv\Scripts\deactivate.bat
    pause
    exit /b 1
)

echo.
echo ================================================
echo 依赖安装完成！
echo ================================================
echo.
echo 虚拟环境已激活，你可以：
echo 1. 运行程序：python main.py
echo 2. 或关闭此窗口，使用 run_venv.bat 运行
echo.
echo 要退出虚拟环境，输入：deactivate
echo ================================================
echo.

REM 保持窗口打开
cmd /k
