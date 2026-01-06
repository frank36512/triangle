@echo off
REM 安装依赖脚本

echo ================================================
echo AI广告视频生成系统 - 依赖安装
echo ================================================
echo.

echo 正在检查Python版本...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

echo.
echo 正在安装依赖包...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ================================================
echo 依赖安装完成！
echo ================================================
echo.
echo 下一步：
echo 1. 在"系统设置"中配置API密钥
echo 2. 运行 run.bat 启动程序
echo.
pause
