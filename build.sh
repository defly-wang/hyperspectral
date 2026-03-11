#!/bin/bash

set -e

echo "========================================="
echo "  Hyperspectral Viewer 打包脚本"
echo "========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "[1/4] 检查并激活虚拟环境..."
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "错误: 未找到虚拟环境 venv，请先创建虚拟环境"
    exit 1
fi

echo ""
echo "[2/4] 安装 PyInstaller..."
pip install pyinstaller -q

echo ""
echo "[3/4] 清理旧构建..."
rm -rf build dist

echo ""
echo "[4/4] 开始打包..."
pyinstaller hyperspectral.spec --clean

echo ""
echo "========================================="
echo "  打包完成!"
echo "========================================="
echo ""
echo "输出目录: dist/HyperspectralViewer/"
echo "可执行文件: dist/HyperspectralViewer/HyperspectralViewer"
echo ""
echo "运行方式:"
echo "  cd dist/HyperspectralViewer"
echo "  ./HyperspectralViewer"
echo ""
