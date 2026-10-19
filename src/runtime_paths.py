from __future__ import annotations

import shutil
import sys
from functools import lru_cache
from pathlib import Path


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def app_root() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def bundle_root() -> Path:
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", app_root()))
    return project_root()


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@lru_cache(maxsize=1)
def default_config_path() -> Path:
    return app_root() / "config.yaml"


def resolve_config_path(config_path: Path) -> Path:
    if config_path.is_absolute():
        return config_path

    cwd_candidate = Path.cwd() / config_path
    if cwd_candidate.exists():
        return cwd_candidate.resolve()

    return (app_root() / config_path).resolve()


def resolve_app_relative_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (app_root() / candidate).resolve()


def bundled_resource(relative_path: str) -> Path | None:
    candidate = bundle_root() / relative_path
    if candidate.exists():
        return candidate
    return None


def ensure_default_config(config_path: Path | None = None) -> Path:
    target = resolve_config_path(config_path or default_config_path())
    if target.exists():
        return target

    target.parent.mkdir(parents=True, exist_ok=True)
    for candidate in [
        bundled_resource("config.yaml"),
        bundled_resource("config.dist.yaml"),
        project_root() / "config.yaml",
        project_root() / "config.dist.yaml",
    ]:
        if candidate is not None and candidate.exists():
            shutil.copy2(candidate, target)
            break
    return target


def app_icon_path() -> Path | None:
    for relative in ("assets/tbh_monitor.ico", "assets/tbh_monitor.png"):
        path = bundled_resource(relative)
        if path is not None:
            return path

    for relative in ("assets/tbh_monitor.ico", "assets/tbh_monitor.png"):
        path = project_root() / relative
        if path.exists():
            return path
    return None
