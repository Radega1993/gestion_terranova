# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Get the base directory
base_dir = os.getcwd()

# Create a runtime hook to fix Babel imports
with open('runtime-hook.py', 'w') as f:
    f.write('''
import os
import sys

# Add the application directory to the path
if getattr(sys, 'frozen', False):
    # Running in a bundle
    bundle_dir = os.path.dirname(sys.executable)
    app_dir = os.path.join(bundle_dir, 'app')
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    
    # Fix Babel imports
    babel_dir = os.path.join(bundle_dir, 'babel')
    if os.path.exists(babel_dir) and babel_dir not in sys.path:
        sys.path.insert(0, babel_dir)
''')

# Collect Babel data files
babel_datas = collect_data_files('babel')

a = Analysis(
    ['app/main.py'],
    pathex=[base_dir],
    binaries=[],
    datas=[
        ('gestion_terranova.db', 'app/database'),
    ] + babel_datas,
    hiddenimports=[
        'babel.numbers',
        'babel.dates',
        'babel.plural',
        'babel.messages',
        'babel.core',
        'babel.locale',
        'babel.util',
        'babel.dates',
        'babel.numbers',
        'babel.numbers.format',
        'babel.numbers.parse',
        'babel.numbers.plural',
        'babel.numbers.symbols',
        'babel.numbers.validators',
        'babel.plural',
        'babel.messages',
        'babel.calendar',
        'babel.timezone',
        'babel.timezone.zoneinfo',
        'babel.timezone.zoneinfo.zoneinfo',
        'babel.timezone.zoneinfo.zoneinfo.zoneinfo',
        'sqlalchemy.sql.default_comparator',
        'sqlalchemy.ext.baked',
        'PIL._tkinter_finder',
        'tkcalendar',
        'reportlab.graphics.barcode',
        'reportlab.graphics.barcode.code128',
        'reportlab.graphics.barcode.code39',
        'reportlab.graphics.barcode.code93',
        'reportlab.graphics.barcode.usps',
        'reportlab.graphics.barcode.usps4s',
        'reportlab.graphics.barcode.qr',
        'pkg_resources.py2_warn',
    ],
    hookspath=['.'],  # Add current directory to hook path
    hooksconfig={},
    runtime_hooks=['runtime-hook.py'],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GestionTerranova',
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
)
