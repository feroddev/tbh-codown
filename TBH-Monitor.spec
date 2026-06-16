# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

project_root = Path(SPECPATH)

datas = [
    (str(project_root / "packaging" / "config.yaml"), "."),
    (str(project_root / "assets" / "tbh_monitor.ico"), "assets"),
    (str(project_root / "assets" / "tbh_monitor.png"), "assets"),
    (str(project_root / "src" / "data" / "boss_chests.json"), "src/data"),
    (str(project_root / "src" / "data" / "stages.json"), "src/data"),
]
binaries = []
hiddenimports = [
    "PIL",
    "PIL._tkinter_finder",
    "yaml",
    "Crypto",
    "Crypto.Cipher.AES",
    "es3_modifier",
]

for package in ("customtkinter",):
    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hiddenimports

a = Analysis(
    [str(project_root / "src" / "main.py")],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["plyer"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TBH-Monitor",
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
    icon=str(project_root / "assets" / "tbh_monitor.ico"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="TBH-Monitor",
)
