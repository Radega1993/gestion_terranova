# -*- mode: python ; coding: utf-8 -*-
import os

# Get the base directory
base_dir = os.getcwd()

a = Analysis(
    ['app/main.py'],
    pathex=[base_dir],
    binaries=[],
    datas=[
        ('gestion_terranova.db', 'app/database'),
    ],
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
    runtime_hooks=[],
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
