# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import sys

import pefile
from PyInstaller.utils.hooks import collect_all


def collect_environment_dlls():
    """Resolve DLLs imported by extension modules in the active environment."""
    prefix = Path(sys.prefix)
    roots = [prefix / "DLLs"]
    roots.extend(path.parent for path in prefix.glob("Lib/site-packages/**/*.pyd"))
    search_dirs = {path for path in roots if path.is_dir()}
    search_dirs.update({prefix / "Library" / "bin", prefix / "DLLs"})

    candidates = {}
    for directory in search_dirs:
        for path in directory.glob("*"):
            if path.suffix.lower() in {".dll", ".pyd"}:
                candidates.setdefault(path.name.lower(), path)

    extension_modules = []
    for directory in roots:
        extension_modules.extend(directory.glob("*.pyd"))

    collected = []
    collected_paths = set()
    queued = set(extension_modules)
    visited = set()
    while queued:
        module = queued.pop()
        if module in visited:
            continue
        visited.add(module)

        try:
            binary = pefile.PE(str(module), fast_load=True)
            binary.parse_data_directories(
                directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]]
            )
        except (OSError, pefile.PEFormatError):
            continue

        for entry in getattr(binary, "DIRECTORY_ENTRY_IMPORT", []):
            dependency_name = entry.dll.decode("ascii", "ignore").lower()
            dependency = candidates.get(dependency_name)
            if dependency is None or dependency.suffix.lower() != ".dll":
                continue
            if dependency not in visited and dependency not in queued:
                queued.add(dependency)
            if dependency not in collected_paths:
                collected.append((dependency, "."))
                collected_paths.add(dependency)

    return [(str(path), destination) for path, destination in collected]


datas = [('assets', 'assets')]
binaries = collect_environment_dlls()
hiddenimports = []

tmp_ret = collect_all('curl_cffi')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('yt_dlp')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'torch', 'pandas', 'scipy', 'numpy', 'matplotlib', 'IPython', 'jupyter', 'tkinter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CinemaPy',
    debug=False,
    icon='assets/icons/app_icon.ico',
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CinemaPy',
)
