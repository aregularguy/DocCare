# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for DentNest
This creates a standalone Windows executable with all dependencies bundled.
"""

block_cipher = None

# Analysis - Find all Python files and dependencies
a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include data directory for database
        ('data', 'data'),
        # Bundle icon files so they're accessible at runtime
        ('src/resources/icons', 'src/resources/icons'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'matplotlib',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_qtagg',
        'pandas',
        'numpy',
        'sqlite3',
        'dateutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'test',
        'unittest',
        'email',
        'http',
        'xml',
        'pydoc',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary files to reduce size
a.datas = [x for x in a.datas if not x[0].startswith('tk')]
a.binaries = [x for x in a.binaries if not x[0].startswith('tk')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DentNest',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/resources/icons/dentnest.ico',  # Windows taskbar + title bar icon
    # version='version_info.txt'  # Uncomment and create this file if you want version metadata
)
