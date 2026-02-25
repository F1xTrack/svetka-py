# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

project_root = 'G:/_Projects/svetka_py'

assets_data = [
    (f'{project_root}/assets', 'assets'),
    (f'{project_root}/config.yaml', '.'),
]

hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtWebEngineWidgets',
    'cv2',
    'numpy',
    'sounddevice',
    'SoundCard',
    'mss',
    'pyautogui',
    'pynput',
    'edge_tts',
    'fastapi',
    'uvicorn',
    'watchfiles',
]

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=assets_data,
    hiddenimports=hiddenimports,
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
    name='SvetkaAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
