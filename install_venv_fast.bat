@echo off
REM 快速安装依赖（利用系统已有包）

echo ================================================
echo AI广告视频生成系统 - 快速依赖安装
echo ================================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo 虚拟环境不存在，正在创建...
    call setup_venv_fast.bat
    exit /b
)

echo 正在激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo 正在检查已安装的包...
python -m pip list

echo.
echo 正在安装缺失的依赖（已安装的会自动跳过）...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo 警告: 部分依赖安装可能失败，但不影响已有包的使用
)

echo.
echo ================================================
echo 依赖检查完成！
echo ================================================
echo.
echo 已安装的核心包：
python -c "import PyQt6; print('✓ PyQt6')" 2>nul
python -c "import PIL; print('✓ Pillow')" 2>nul
python -c "import requests; print('✓ requests')" 2>nul
python -c "import cv2; print('✓ opencv-python')" 2>nul
python -c "import aiohttp; print('✓ aiohttp')" 2>nul

echo.
echo 虚拟环境已就绪！
echo 运行程序：python main.py
echo.

REM 保持窗口打开
cmd /k
