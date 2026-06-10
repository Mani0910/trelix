# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None
base_dir = r'c:\QA\mxonetrelix'

webview_datas = collect_data_files('webview')
webview_imports = collect_submodules('webview')

a = Analysis(
    [os.path.join(base_dir, 'app.py')],
    pathex=[base_dir],
    binaries=[],
    datas=[
        (os.path.join(base_dir, 'index.html'), '.'),
        (os.path.join(base_dir, 'fireeye.sh'), '.'),
        (os.path.join(base_dir, 'config.py'), '.'),
    ] + webview_datas,
    hiddenimports=[
        'flask',
        'flask_limiter',
        'flask_limiter.util',
        'limits',
        'limits.storage',
        'limits.strategies',
        'paramiko',
        'openpyxl',
        'smb',
        'smb.SMBConnection',
        'werkzeug',
        'werkzeug.utils',
        'jinja2',
        'webview',
        'webview.platforms',
        'webview.platforms.edgechromium',
        'pythonnet',
        'clr_loader',
        'bottle',
        'proxy_tools',
    ] + webview_imports,
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
    name='trelix',
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
