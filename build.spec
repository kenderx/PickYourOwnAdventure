# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import customtkinter

block_cipher = None

# Dynamically locate the customtkinter installation directory so the spec file
# remains portable across different machines and environments.
ctk_dir = os.path.dirname(customtkinter.__file__)

# Datas to bundle:
# 1. CustomTkinter assets (themes, assets, etc.)
# 2. Stories directory (including sample story and cover images)
datas = [
    (ctk_dir, 'customtkinter'),
    ('stories', 'stories'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    name='PickYourOwnAdventure',
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
)
