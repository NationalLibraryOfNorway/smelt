# -*- mode: python ; coding: utf-8 -*-
import sys
import platform
import os

is_windows = platform.system() == 'Windows'
is_linux = platform.system() == 'Linux'

pathex = ['..']
resources_path = os.path.join('..', 'resources')

datas = [
    (os.path.join(resources_path, 'icon.ico'), 'icons'),
    (os.path.join(resources_path, 'cuda.png'), 'icons'),
    (os.path.join(resources_path, 'ffmpeg.png'), 'icons'),
]

if is_windows:
    datas.append((os.path.join(resources_path, 'ffmpeg.exe'), '.'))


a = Analysis(
    [
        os.path.join('..', 'Smelt.py'),
        os.path.join('..', 'GUI.py'),
        os.path.join('..', 'ffmpeg_commands.py'),
        os.path.join('..', 'Utils.py'),
        os.path.join(resources_path, 'resources_rc.py')
    ],
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
