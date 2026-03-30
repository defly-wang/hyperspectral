# -*- mode: python ; coding: utf-8 -*-
import os
import sysconfig
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

pyqt6_plugins_path = '/home/defly/git/hyperspectral/venv/lib/python3.12/site-packages/PyQt6/Qt6/plugins'

datas_pyqt6, binaries_pyqt6, hiddenimports_pyqt6 = collect_all('PyQt6')
datas_matplotlib, binaries_matplotlib, hiddenimports_matplotlib = collect_all('matplotlib')
datas_scipy, binaries_scipy, hiddenimports_scipy = collect_all('scipy')

pyqt6_hiddenimports = hiddenimports_pyqt6 + collect_submodules('PyQt6')

qt_plugins = [
    (os.path.join(pyqt6_plugins_path, 'platforms'), 'PyQt6/Qt6/plugins/platforms'),
    (os.path.join(pyqt6_plugins_path, 'imageformats'), 'PyQt6/Qt6/plugins/imageformats'),
]

datas = datas_pyqt6 + datas_matplotlib + datas_scipy + [('icon.ico', '.')] + qt_plugins

binaries = binaries_pyqt6 + binaries_matplotlib + binaries_scipy + [
    ('/tmp/libxcb-cursor/usr/lib/x86_64-linux-gnu/libxcb-cursor.so.0', '.'),
]

hiddenimports = pyqt6_hiddenimports + hiddenimports_matplotlib + hiddenimports_scipy + [
    'matplotlib.backends.backend_qt5agg',
    'numpy', 'scipy', 'openpyxl', 'sklearn', 'joblib',
    'scipy.signal', 'scipy.ndimage', 'sklearn.ensemble', 'sklearn.svm',
    'sklearn.preprocessing', 'sklearn.metrics', 'sklearn.model_selection',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='HyperspectralDMS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HyperspectralDMS',
)
