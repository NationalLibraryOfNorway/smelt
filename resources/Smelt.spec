# -*- mode: python ; coding: utf-8 -*-
import sys
import platform
import os

is_windows = platform.system() == 'Windows'
is_linux = platform.system() == 'Linux'

# Ensure the paths are correct
pathex = ['..']
resources_path = os.path.join('..', 'resources')

datas = [
    (os.path.join(resources_path, 'icon.ico'), 'icons'),
    (os.path.join(resources_path, 'cuda.png'), 'icons'),
    (os.path.join(resources_path, 'ffmpeg.png'), 'icons'),
]

if is_windows:
    datas.append((os.path.join(resources_path, 'ffmpeg.exe'), '.'))

hidden_imports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'subprocess',
    'shutil',
    'tempfile',
    'zipfile',
    'os',
    'platform'
]

a = Analysis(
    [
        os.path.join('..', 'Smelt.py'),
        os.path.join('..', 'GUI.py'),
        os.path.join('..', 'ffmpeg_commands.py'),
        os.path.join('..', 'Utils.py'),
        os.path.join(resources_path, 'resources_rc.py')
    ],
    pathex=pathex,
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe_common_settings = {
    'pyz': pyz,
    'a.scripts': a.scripts,
    'a.binaries': a.binaries,
    'a.datas': a.datas,
    'strip': False,
    'upx': True,
    'upx_exclude': [],
    'runtime_tmpdir': None,
    'console': False,
    'disable_windowed_traceback': False,
    'argv_emulation': False,
    'target_arch': None,
    'codesign_identity': None,
    'entitlements_file': None,
}

if is_windows:
    exe = EXE(
        **exe_common_settings,
        name='Smelt',
        debug=False,
        bootloader_ignore_signals=False,
        icon=os.path.join(resources_path, 'icon.ico'),
        version=os.path.join(resources_path, 'version.txt'),
    )

if is_linux:
    exe = EXE(
        **exe_common_settings,
        name='Smelt',
        debug=False,
        bootloader_ignore_signals=False,
        strip=True,  # Usually strip binaries on Linux
        console=True,  # Use console for debugging
        icon=None,  # Update this if you have a Linux icon
        version=None,
    )