@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo =========================================
echo   Hyperspectral Viewer 打包脚本
echo =========================================

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo [1/4] 检查虚拟环境...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo 警告: 未找到虚拟环境 venv，将使用系统 Python
)

echo.
echo [2/4] 安装 PyInstaller...
pip install pyinstaller -q

echo.
echo [3/4] 清理旧构建...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo.
echo [4/4] 开始打包...
pyinstaller hyperspectral.spec --clean

echo.
echo =========================================
echo   打包完成!
echo =========================================
echo.
echo 输出目录: dist\HyperspectralViewer\
echo 可执行文件: dist\HyperspectralViewer\HyperspectralViewer.exe
echo.
echo 运行方式:
echo   cd dist\HyperspectralViewer
echo   HyperspectralViewer.exe
echo.

endlocal
pause
