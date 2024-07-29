# -*- mode: python ; coding: utf-8 -*-
import sys
import platform

is_windows = platform.system() == 'Windows'
is_linux = platform.system() == 'Linux'

datas = [
    ('../resources/icon.ico', 'icons'),
    ('../resources/cuda.png', 'icons'),
    ('../resources/ffmpeg.png', 'icons'),
]

if is_windows:
    datas.append(('../resources/ffmpeg.exe', '.'))

a = Analysis(
    ['../Smelt.py', '../GUI.py', '../ffmpeg_commands.py', '../Utils.py', '../resources/resources_rc.py'],
    pathex=['..'],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

if is_windows:
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
        icon='../resources/icon.ico' if is_windows else None,
        version='../resources/version.txt' if is_windows else None,
    )

if is_linux:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name='Smelt',
        debug=False,
        bootloader_ignore_signals=False,
        strip=True,  # Usually strip binaries on Linux
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=True,  # Use console for debugging
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=None,  # Update this if you have a Linux icon
        version=None,
    )
