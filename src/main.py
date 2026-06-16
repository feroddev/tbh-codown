from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.application.monitor_service import MonitorService
from src.config_loader import load_config
from src.runtime_paths import ensure_default_config, resolve_config_path
from src.data.stage_codec import decode_stage_key
from src.infrastructure.game_paths import format_discovered_paths
from src.infrastructure.save_reader import SaveReader
from src.infrastructure.windows_console import ensure_console_for_cli
from src.ui.app import run_gui

logger = logging.getLogger(__name__)


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def run_monitor(config_path: Path, dry_run: bool) -> int:
    config = load_config(config_path)
    service = MonitorService(config, dry_run=dry_run)

    try:
        service.run()
    except KeyboardInterrupt:
        logger.info("Monitor parado pelo usuário")
        service.stop()
    except FileNotFoundError as error:
        logger.error("%s", error)
        return 1

    return 0


def run_status(config_path: Path) -> int:
    config = load_config(config_path)
    reader = SaveReader(config.save_file_path, password=config.es3_password)
    snapshot = reader.read_snapshot()
    stage = decode_stage_key(snapshot.current_stage_key)
    print(f"stageKey={snapshot.current_stage_key} ({stage.label})")
    print(f"baús de chefe={snapshot.boss_box_count}")
    print(f"baús comuns={snapshot.box_data.normal_box_count()}")
    return 0


def run_paths() -> int:
    print(format_discovered_paths())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TBH Monitor — baús e rotação de mapas")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Caminho do arquivo config.yaml (padrão: ao lado do executável)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Detecta baús sem enviar notificações de próximo mapa",
    )
    parser.add_argument("--verbose", action="store_true", help="Logs detalhados")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("monitor", help="Executar monitor no terminal").set_defaults(command="monitor")
    subparsers.add_parser("gui", help="Abrir interface gráfica").set_defaults(command="gui")
    subparsers.add_parser("status", help="Mostrar stage atual do save").set_defaults(command="status")
    subparsers.add_parser("paths", help="Mostrar caminhos detectados do jogo").set_defaults(command="paths")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "gui"
    if command != "gui":
        ensure_console_for_cli()

    configure_logging(args.verbose)

    config_path = ensure_default_config(resolve_config_path(args.config))
    if command == "gui":
        run_gui(config_path)
        return 0

    if command == "status":
        return run_status(config_path)
    if command == "paths":
        return run_paths()

    dry_run = args.dry_run or load_config(config_path).monitor.dry_run
    return run_monitor(config_path, dry_run)


if __name__ == "__main__":
    sys.exit(main())
