# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../Smelt.py', '../resources/resources_rc.py'],  # Include the main script and the resources file
    pathex=['..'],  # Path to the project root
    binaries=[],
    datas=[('../resources/icon.ico', 'icon.ico')],  # Correct path to icon
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtNetwork',
        'PyQt5.QtPrintSupport',
        'sip',  # Ensure sip is included
    ],
    hookspath=['resources/hooks'],  # Path to additional hooks if any
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
    debug=False,  # Disable debugging for the final build
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='../resources/icon.ico',  # Correct path to icon
    version='../resources/version.txt'  # Correct path to version file
)
