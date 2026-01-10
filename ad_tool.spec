# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os
import cv2

"""
PyInstaller配置文件
用于将应用打包为独立的EXE文件
"""

block_cipher = None

# 获取cv2的路径
cv2_dir = os.path.dirname(cv2.__file__)

# 收集 cv2 的所有依赖
cv2_datas, cv2_binaries, cv2_hiddenimports = collect_all('cv2')

# 确保cv2在datas中
found_cv2_in_datas = False
for src, dest in cv2_datas:
    if dest == 'cv2':
        found_cv2_in_datas = True
        break

if not found_cv2_in_datas:
    cv2_datas.append((cv2_dir, 'cv2'))

a = Analysis(
    ['main.py'],
    pathex=['E:\\ad_tool\\venv\\Lib\\site-packages'],
    binaries=cv2_binaries,
    datas=[
        ('resources', 'resources'),  # 包含资源文件
    ] + cv2_datas,
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtMultimedia',
        'PyQt6.QtMultimediaWidgets',
        'PIL',
        'PIL._imaging',
        'requests',
        'aiohttp',
        'cv2',
        'numpy',
    ] + cv2_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI广告视频生成系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='adplay.ico',  # 使用adplay.ico作为图标
)
