@echo off
REM 打包EXE脚本

echo ================================================
echo AI广告视频生成系统 - 打包EXE
echo ================================================
echo.

echo 正在检查PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 未检测到PyInstaller，正在安装...
    pip install pyinstaller
)

echo.
echo 正在清理旧的打包文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo 正在打包EXE（这可能需要几分钟）...
pyinstaller ad_tool.spec

if %errorlevel% neq 0 (
    echo.
    echo 错误: 打包失败
    pause
    exit /b 1
)

echo.
echo ================================================
echo 打包完成！
echo ================================================
echo.
echo EXE文件位置: dist\AI广告视频生成系统.exe
echo.
pause
