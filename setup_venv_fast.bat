@echo off
REM 复用系统已安装的包创建虚拟环境（快速版）

echo ================================================
echo AI广告视频生成系统 - 快速虚拟环境设置
echo 复用系统已安装的包，避免重复下载
echo ================================================
echo.

REM 检查Python是否存在
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

echo [1/3] 创建虚拟环境（允许访问系统包）...
python -m venv venv --system-site-packages

if %errorlevel% neq 0 (
    echo.
    echo 错误: 虚拟环境创建失败
    pause
    exit /b 1
)

echo.
echo [2/3] 检查系统已安装的共同依赖包...
echo 正在检查: PyQt6, Pillow, requests, opencv-python...

call venv\Scripts\activate.bat

REM 显示哪些包已经可用
python -c "import PyQt6; print('✓ PyQt6 已可用')" 2>nul || echo "✗ PyQt6 需要安装"
python -c "import PIL; print('✓ Pillow 已可用')" 2>nul || echo "✗ Pillow 需要安装"
python -c "import requests; print('✓ requests 已可用')" 2>nul || echo "✗ requests 需要安装"
python -c "import cv2; print('✓ opencv-python 已可用')" 2>nul || echo "✗ opencv-python 需要安装"

echo.
echo [3/3] 安装缺失的依赖包...
echo 提示: 已安装的包会自动跳过，只安装缺失的包

pip install -r requirements.txt --no-warn-script-location

call venv\Scripts\deactivate.bat

echo.
echo ================================================
echo 虚拟环境设置完成！
echo ================================================
echo.
echo 通过 --system-site-packages 参数：
echo ✓ 复用了系统已安装的 PyQt6 等包
echo ✓ 避免了大量重复下载
echo ✓ 节省了磁盘空间（约200MB）
echo ✓ 大幅缩短了安装时间
echo.
echo 下一步：
echo   run_venv.bat  - 运行程序
echo ================================================
echo.
pause
