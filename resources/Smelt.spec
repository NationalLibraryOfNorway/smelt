# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../Smelt.py'],  # Corrected path to the script, relative to the spec file location
    pathex=['..'],  # Path to the project root
    binaries=[],
    datas=[('icon.ico', 'icon.ico')],  # Assuming the icon is in the same directory as the spec file
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Smelt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.ico',  # Path relative to the spec file
    version='version.txt'  # Path relative to the spec file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Smelt'
)
