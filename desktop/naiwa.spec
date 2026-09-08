# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

ROOT = Path(SPECPATH).parent
webview_datas, webview_binaries, webview_hidden = collect_all("webview")

a = Analysis(
    [str(ROOT / "desktop" / "main.py")],
    pathex=[str(ROOT / "backend"), str(ROOT)],
    binaries=webview_binaries,
    datas=webview_datas + [
        (str(ROOT / "frontend" / "dist"), "frontend/dist"),
        (str(ROOT / "images"), "images"),
    ],
    hiddenimports=webview_hidden + ["app.models.entities", "scripts.seed_data", "uvicorn.logging"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "pytest", "httpx"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="NAIWA",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(ROOT / "desktop" / "naiwa.ico"),
    version=str(ROOT / "desktop" / "version_info.txt"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="NAIWA",
)
