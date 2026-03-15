# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for building clash-verge-rev CLI as a standalone binary.

Usage:
    pyinstaller clash-verge-rev.spec --clean

Output:
    dist/clash-verge-rev
"""

from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
import os
import sys

# Get the base directory
base_dir = os.path.dirname(os.path.abspath(SPECPATH))

block_cipher = None

# Analysis step - find all dependencies
a = Analysis(
    ['cli_anything/clash_verge_rev/clash_verge_rev_cli.py'],
    pathex=[base_dir],
    binaries=[],
    datas=[],
    hiddenimports=[
        'cli_anything.clash_verge_rev.core',
        'cli_anything.clash_verge_rev.core.config',
        'cli_anything.clash_verge_rev.core.runtime',
        'cli_anything.clash_verge_rev.core.service',
        'cli_anything.clash_verge_rev.core.backup',
        'cli_anything.clash_verge_rev.utils',
        'cli_anything.clash_verge_rev.utils.output',
        'cli_anything.clash_verge_rev.utils.validators',
        'click',
        'yaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'pytest',
        'unittest',
        'tkinter',
        'django',
        'flask',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Create the archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Build options for single binary
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='clash-verge-rev',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Single file mode
    onefile=True,
)
