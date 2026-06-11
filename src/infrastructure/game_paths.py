from __future__ import annotations

import os
import re
import sys
from collections.abc import Callable
from pathlib import Path

DEFAULT_ES3_PASSWORD = "emuMqG3bLYJ938ZDCfieWJ"
COMPANY_NAME = "TesseractStudio"
GAME_FOLDER = "TaskbarHero"
SAVE_FILE_NAME = "SaveFile_Live.es3"
SAVE_FILE_TEST_BACKUP_NAME = "SaveFile_Live.es3.test_backup"
ACTIVE_SAVE_FILE_PATTERN = re.compile(r"^SaveFile_Live_\d+\.es3\.bak$")
PLAYER_LOG_NAME = "Player.log"
GAME_EXE_NAME = "TaskBarHero.exe"

GAME_RESOURCES_ASSETS = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\TaskbarHero\TaskBarHero_Data\resources.assets"
)
DEFAULT_PLAYER_LOG = Path.home() / "AppData/LocalLow/TesseractStudio/TaskbarHero/Player.log"
DEFAULT_SAVE_FILE = Path.home() / "AppData/LocalLow/TesseractStudio/TaskbarHero/SaveFile_Live.es3"
DEFAULT_GAME_EXE = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\TaskbarHero\TaskBarHero.exe"
)


def _unity_local_low_dir() -> Path:
    return Path.home() / "AppData/LocalLow" / COMPANY_NAME / GAME_FOLDER


def _unity_mac_dir() -> Path:
    return Path.home() / "Library/Application Support" / COMPANY_NAME / GAME_FOLDER


def _unity_linux_dir() -> Path:
    return Path.home() / ".config/unity3d" / COMPANY_NAME / GAME_FOLDER


def candidate_game_data_dirs() -> list[Path]:
    candidates: list[Path] = []

    if sys.platform == "win32":
        candidates.append(_unity_local_low_dir())
        local_low = Path.home() / "AppData/LocalLow"
        if local_low.exists():
            for company_dir in local_low.iterdir():
                if not company_dir.is_dir():
                    continue
                game_dir = company_dir / GAME_FOLDER
                if game_dir.is_dir():
                    candidates.append(game_dir)
    elif sys.platform == "darwin":
        candidates.append(_unity_mac_dir())
    else:
        candidates.append(_unity_linux_dir())

    unique: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def discover_game_data_dir() -> Path | None:
    for directory in candidate_game_data_dirs():
        if not directory.exists():
            continue
        if (directory / SAVE_FILE_NAME).exists() or (directory / PLAYER_LOG_NAME).exists():
            return directory
    return None


def discover_player_log() -> Path:
    data_dir = discover_game_data_dir()
    if data_dir is not None:
        log_path = data_dir / PLAYER_LOG_NAME
        if log_path.exists():
            return log_path

    default = _default_player_log_for_platform()
    if default.exists():
        return default
    return default


def is_active_save_file_name(name: str) -> bool:
    if name == SAVE_FILE_NAME or name == SAVE_FILE_TEST_BACKUP_NAME:
        return True
    return ACTIVE_SAVE_FILE_PATTERN.fullmatch(name) is not None


def list_active_save_candidates(base_path: Path) -> list[Path]:
    directory = base_path.parent
    if not directory.is_dir():
        return [base_path] if base_path.exists() else []

    candidates = [
        entry
        for entry in directory.iterdir()
        if entry.is_file() and is_active_save_file_name(entry.name)
    ]
    if candidates:
        return sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)
    return [base_path] if base_path.exists() else []


def discover_save_file() -> Path:
    data_dir = discover_game_data_dir()
    if data_dir is not None:
        save_path = data_dir / SAVE_FILE_NAME
        if save_path.exists():
            return save_path

    default = _default_save_file_for_platform()
    if default.exists():
        return default
    return default


def _default_player_log_for_platform() -> Path:
    if sys.platform == "win32":
        return _unity_local_low_dir() / PLAYER_LOG_NAME
    if sys.platform == "darwin":
        return _unity_mac_dir() / PLAYER_LOG_NAME
    return _unity_linux_dir() / PLAYER_LOG_NAME


def _default_save_file_for_platform() -> Path:
    if sys.platform == "win32":
        return _unity_local_low_dir() / SAVE_FILE_NAME
    if sys.platform == "darwin":
        return _unity_mac_dir() / SAVE_FILE_NAME
    return _unity_linux_dir() / SAVE_FILE_NAME


def _steam_install_roots() -> list[Path]:
    if sys.platform != "win32":
        return []

    roots: list[Path] = []
    for env_key in ("ProgramFiles(x86)", "ProgramFiles"):
        base = os.environ.get(env_key)
        if not base:
            continue
        steam_root = Path(base) / "Steam"
        if steam_root.exists():
            roots.append(steam_root)

    extra_roots: list[Path] = []
    for steam_root in roots:
        library_file = steam_root / "steamapps/libraryfolders.vdf"
        if not library_file.exists():
            continue
        content = library_file.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r'"path"\s+"([^"]+)"', content):
            library_path = Path(match.group(1).replace("\\\\", "\\"))
            if library_path.exists():
                extra_roots.append(library_path)

    combined: list[Path] = []
    seen: set[Path] = set()
    for root in [*roots, *extra_roots]:
        resolved = root.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        combined.append(resolved)
    return combined


def discover_game_exe() -> Path:
    candidates: list[Path] = [DEFAULT_GAME_EXE]

    for steam_root in _steam_install_roots():
        candidates.append(steam_root / "steamapps/common/TaskbarHero" / GAME_EXE_NAME)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return DEFAULT_GAME_EXE


def resolve_path(
    configured: str | Path | None,
    *,
    discover: Callable[[], Path],
) -> Path:
    if configured:
        path = Path(configured)
        if path.exists():
            return path
    return discover()


def discover_es3_password(game_resources_path: Path | None = None) -> str:
    resources_path = game_resources_path or GAME_RESOURCES_ASSETS
    if not resources_path.exists():
        game_exe = discover_game_exe()
        if game_exe.exists():
            resources_path = game_exe.parent / "TaskBarHero_Data/resources.assets"

    if not resources_path.exists():
        return DEFAULT_ES3_PASSWORD

    data = resources_path.read_bytes()
    marker = b"SaveFile_Live.es3"
    index = data.find(marker)
    if index < 0:
        return DEFAULT_ES3_PASSWORD

    chunk = data[index : index + 120]
    match = re.search(rb"SaveFile_Live\.es3\x00([A-Za-z0-9]{8,64})", chunk)
    if match:
        return match.group(1).decode("ascii")
    return DEFAULT_ES3_PASSWORD


def format_discovered_paths() -> str:
    data_dir = discover_game_data_dir()
    player_log = discover_player_log()
    save_file = discover_save_file()
    game_exe = discover_game_exe()

    lines = [
        f"game_data_dir: {data_dir or '(not found)'}",
        f"player_log:    {player_log} {'(exists)' if player_log.exists() else '(missing)'}",
        f"save_file:     {save_file} {'(exists)' if save_file.exists() else '(missing)'}",
        f"game_exe:      {game_exe} {'(exists)' if game_exe.exists() else '(missing)'}",
    ]
    return "\n".join(lines)
