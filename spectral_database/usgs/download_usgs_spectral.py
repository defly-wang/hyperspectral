#!/usr/bin/env python3
"""
USGS光谱库下载脚本

用于下载USGS Spectral Library Version 7的ASCII格式光谱数据
官方主页: https://www.usgs.gov/labs/spectroscopy-lab/science/spectral-library
数据下载: https://www.sciencebase.gov/catalog/item/586e8c88e4b0f5ce109fccae

使用方法:
    python download_usgs_spectral.py [options]

选项:
    --data-dir DIR     指定数据下载目录 (默认: ../spectral_database/usgs)
    --files FILES      指定要下载的文件，多个文件用逗号分隔
                       可选文件: splib07a, splib07b, cvASD, cvAVIRISc2014, rsASTER, rsSentinel2
    --all              下载所有ASCII格式数据 (约110MB)
    --minerals-only    只下载矿物章节 (ChapterM_Minerals)
    --rocks-only       只下载岩石/土壤章节 (ChapterS_SoilsAndMixtures)
"""

import os
import sys
import argparse
import urllib.request
import zipfile
from pathlib import Path

BASE_URL = "https://www.sciencebase.gov/catalog/file/get/586e8c88e4b0f5ce109fccae"

FILE_MAPPING = {
    "splib07a": "ASCIIdata_splib07a.zip",       # 20.8 MB - 原始测量光谱
    "splib07b": "ASCIIdata_splib07b.zip",       # 41.4 MB - 过采样光谱
    "cvASD": "ASCIIdata_splib07b_cvASD.zip",   # 27.1 MB - ASD卷积
    "cvAVIRISc2014": "ASCIIdata_splib07b_cvAVIRISc2014.zip",  # 4.1 MB - AVIRIS卷积
    "rsASTER": "ASCIIdata_splib07b_rsASTER.zip",  # 1.3 MB - ASTER重采样
    "rsSentinel2": "ASCIIdata_splib07b_rsSentinel2.zip",  # 1.4 MB - Sentinel-2重采样
}

def download_file(url, filename, data_dir):
    """下载单个文件"""
    filepath = os.path.join(data_dir, filename)
    
    if os.path.exists(filepath):
        file_size = os.path.getsize(filepath)
        print(f"文件已存在: {filename} ({file_size / 1024 / 1024:.2f} MB)")
        return True
    
    print(f"正在下载: {filename}")
    print(f"URL: {url}")
    
    try:
        urllib.request.urlretrieve(url, filepath)
        file_size = os.path.getsize(filepath)
        print(f"下载完成: {filename} ({file_size / 1024 / 1024:.2f} MB)")
        return True
    except Exception as e:
        print(f"下载失败: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return False

def download_and_extract(url, filename, data_dir, extract=True):
    """下载并解压文件"""
    if not download_file(url, filename, data_dir):
        return False
    
    if not extract:
        return True
    
    filepath = os.path.join(data_dir, filename)
    
    if not filename.endswith('.zip'):
        return True
    
    try:
        print(f"正在解压: {filename}")
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        print(f"解压完成: {filename}")
        return True
    except Exception as e:
        print(f"解压失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="USGS光谱库下载脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--data-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "usgs"),
        help="数据下载目录"
    )
    parser.add_argument(
        "--files",
        help="指定要下载的文件，可用值: " + ", ".join(FILE_MAPPING.keys())
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="下载所有ASCII格式数据"
    )
    parser.add_argument(
        "--minerals-only",
        action="store_true",
        help="下载矿物章节数据"
    )
    parser.add_argument(
        "--rocks-only",
        action="store_true",
        help="下载岩石/土壤章节数据"
    )
    parser.add_argument(
        "--no-extract",
        action="store_true",
        help="只下载不解压"
    )
    
    args = parser.parse_args()
    
    data_dir = os.path.abspath(args.data_dir)
    os.makedirs(data_dir, exist_ok=True)
    
    files_to_download = []
    
    if args.files:
        for file_key in args.files.split(","):
            file_key = file_key.strip()
            if file_key in FILE_MAPPING:
                files_to_download.append(file_key)
            else:
                print(f"警告: 未知文件类型 '{file_key}'")
    
    if args.all:
        files_to_download = list(FILE_MAPPING.keys())
    
    if not files_to_download and not args.minerals_only and not args.rocks_only:
        files_to_download = ["splib07a", "rsASTER"]  # 默认下载
    
    print(f"数据下载目录: {data_dir}")
    print(f"将下载以下文件: {files_to_download}")
    print()
    
    success_count = 0
    for file_key in files_to_download:
        filename = FILE_MAPPING[file_key]
        url = f"{BASE_URL}?name={filename}"
        if download_and_extract(url, filename, data_dir, not args.no_extract):
            success_count += 1
    
    print()
    print(f"下载完成: {success_count}/{len(files_to_download)} 个文件")
    
    if args.minerals_only or args.rocks_only:
        print("\n注意: 下载后，请使用以下命令查看章节目录:")
        if args.minerals_only:
            print("  ls ChapterM_Minerals/")
        if args.rocks_only:
            print("  ls ChapterS_SoilsAndMixtures/")
    
    return 0 if success_count == len(files_to_download) else 1

if __name__ == "__main__":
    sys.exit(main())
