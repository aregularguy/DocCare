# -*- mode: python ; coding: utf-8 -*-
# PyInstaller packing list for DentNest.exe
# Used by build_exe.bat and .github/workflows/build.yml:  pyinstaller --clean DentNest.spec
#
# Patient data (data/dentnest.db, settings.json, logo) is intentionally NOT bundled:
# the app creates and keeps it in a "data" folder next to DentNest.exe.

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        # App icon + dropdown/spin-box arrow SVGs used by the stylesheet
        ('src/resources', 'src/resources'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtPrintSupport',
        'PyQt6.QtSvg',
        'matplotlib',
        'matplotlib.backends.backend_qtagg',
        'pandas',
        'numpy',
        'sqlite3',
        'dateutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Do not exclude unittest: matplotlib/pyparsing need it (see commit efa0655)
    excludes=['tkinter'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DentNest',
    icon='src/resources/icons/dentnest.png',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
