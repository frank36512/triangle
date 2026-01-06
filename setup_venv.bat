@echo off
REM 创建和激活虚拟环境脚本

echo ================================================
echo AI广告视频生成系统 - 虚拟环境设置
echo ================================================
echo.

REM 检查Python是否存在
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

echo 正在创建虚拟环境 venv...
python -m venv venv

if %errorlevel% neq 0 (
    echo.
    echo 错误: 虚拟环境创建失败
    pause
    exit /b 1
)

echo.
echo 虚拟环境创建成功！
echo.
echo ================================================
echo 下一步操作：
echo ================================================
echo 1. 激活虚拟环境：
echo    venv\Scripts\activate
echo.
echo 2. 安装依赖：
echo    pip install -r requirements.txt
echo.
echo 3. 运行程序：
echo    python main.py
echo.
echo 或者直接运行：
echo    install_venv.bat  (安装依赖到虚拟环境)
echo    run_venv.bat      (在虚拟环境中运行程序)
echo ================================================
echo.
pause
