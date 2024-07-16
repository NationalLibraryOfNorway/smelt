# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../Smelt.py'],  # Corrected path to the script, relative to the spec file location
    pathex=['..'],  # Path to the project root
    binaries=[],
    datas=[('resources/icon.ico', 'icon.ico')],  # Corrected path to icon
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'sip'
    ],  # Add any other hidden imports if necessary
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
    debug=True,  # Enable debugging
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='resources/icon.ico',  # Corrected path to icon
    version='resources/version.txt'  # Corrected path to version file
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
