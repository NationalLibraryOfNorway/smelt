# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../Smelt.py', '../GUI.py', '../ffmpeg_commands.py', '../Utils.py', '../resources/resources_rc.py'],
    pathex=['..'],
    binaries=[],
    datas=[
    ('../resources/icon.ico', 'icons'),
    ('../resources/cuda.png', 'icons'),
    ('../resources/ffmpeg.png', 'icons'),
    ('../resources/ffmpeg.exe', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Smelt',
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
    icon=['../resources/icon.ico'],
    version='../resources/version.txt'
)
