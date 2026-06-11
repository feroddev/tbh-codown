from __future__ import annotations

from datetime import datetime
from enum import Enum

from src.data.stage_codec import Difficulty


class Language(str, Enum):
    PT_BR = "pt-BR"
    EN = "en"

    @classmethod
    def from_code(cls, code: str | None) -> Language:
        if code is None:
            return cls.PT_BR
        normalized = code.strip().lower().replace("_", "-")
        if normalized in {"en", "en-us", "english"}:
            return cls.EN
        return cls.PT_BR


_current_language = Language.PT_BR

MESSAGES: dict[str, dict[str, str]] = {
    "pt-BR": {
        "app_title": "TBH Monitor — Baús & Rotação",
        "sidebar_title": "TBH Monitor",
        "language_label": "Idioma",
        "lang_pt_br": "Português (BR)",
        "lang_en": "English",
        "chest_timers_title": "Cronômetros",
        "timers_drag_hint": "Ordenação automática por urgência · arraste para ajustar prioridade",
        "timers_next_phase": "Próxima fase: {instruction} ({chest})",
        "timers_none_enabled": "Configure baús à esquerda para ver cronômetros.",
        "watch_title": "Baús monitorados",
        "add_chest": "+ Adicionar baú",
        "common_chest_short": "Comum",
        "common_chest_lv_short": "Comum Lv{level}",
        "common_chest_timer": "Baú comum",
        "chest_kind_boss": "Chefe",
        "chest_kind_common": "Comum",
        "timer_waiting": "Aguardando",
        "timer_active": "Ativo",
        "timer_expired": "Expirado",
        "chest_name_4": "Baú de Chefe 4",
        "chest_name_5": "Baú de Chefe 5",
        "chest_name_7": "Baú de Chefe 7",
        "chest_name_15": "Baú de Chefe 15",
        "chest_name_20": "Baú de Chefe 20",
        "chest_name_30": "Baú de Chefe 30",
        "chest_name_40": "Baú de Chefe 40",
        "chest_name_50": "Baú de Chefe 50",
        "chest_name_65": "Baú de Chefe 65",
        "chest_name_80": "Baú de Chefe 80",
        "chest_name_short_4": "Box 4",
        "chest_name_short_5": "Box 5",
        "chest_name_short_7": "Box 7",
        "chest_name_short_15": "Lv15",
        "chest_name_short_20": "Lv20",
        "chest_name_short_30": "Lv30",
        "chest_name_short_40": "Lv40",
        "chest_name_short_50": "Lv50",
        "chest_name_short_65": "Lv65",
        "chest_name_short_80": "Lv80",
        "consider_common_chest": "Baú comum",
        "dry_run_mode": "Modo simulação (só log)",
        "timer_duration_minutes": "Min",
        "start_monitor": "Iniciar monitor",
        "stop_monitor": "Parar monitor",
        "save_rotation": "Salvar rotação",
        "status": "Status",
        "status_stopped": "Parado",
        "status_running": "Rodando",
        "current_map": "Mapa em jogo: {label}",
        "all_maps_title": "Todos os mapas do jogo ({count})",
        "priority_hint": (
            "Prioridade = ordem na rotação (1, 2, 3…). "
            "Troque de mapa manualmente no jogo — o app só monitora e indica o próximo."
        ),
        "rotation_title": "Rotação",
        "chest_farm_title": "Farm por baú",
        "header_chest_map": "Baú · Mapa",
        "chest_lv": "Baú Lv {level}",
        "chest_lv_short": "Baú Lv {level}",
        "log_chest_drop": "{time} · Baú Lv{level} · {map_name} — {difficulty}",
        "log_chest_drop_detail": "{time} · Baú {kind} Lv{level} · {map_name} — {difficulty}",
        "log_chest_ignored": "{time} · Baú Lv{level} · {map_name} — ignorado: {reason}",
        "log_timer_skipped": "{time} · {label} — cronômetro já ativo, não reiniciado",
        "log_timer_not_watched": "{time} · Lv{level} · {map_name} — fora dos baús monitorados",
        "no_maps_for_chest": "Sem mapas",
        "rotation_empty": "Nenhum baú ativo.",
        "you_are_here": " · aqui",
        "no_boss_chest": "Sem baú",
        "stage_short": "{act}.{stage}",
        "enemy_lv": "Inimigo Lv {level}",
        "go_button": "Ir",
        "events": "Drops",
        "filter_act": "Ato:",
        "filter_difficulty": "Dificuldade:",
        "filter_all": "Todos",
        "search_placeholder": "Buscar mapa…",
        "header_prio": "Prio",
        "header_map_chest": "Mapa · Baú de chefe",
        "act_stage_difficulty": "Ato {act} · Fase {stage} · {difficulty}",
        "act_stage_arrow": "Ato {act} → Fase {stage} → {difficulty}",
        "in_game_instruction": "No jogo: Ato {act} → Fase {stage} → {difficulty}",
        "error_no_maps_rotation": "Ative pelo menos um nível de baú no farm.",
        "success_rotation_saved": "Configuração salva com sucesso.",
        "error_no_maps_start": "Ative pelo menos um nível de baú antes de iniciar.",
        "warning_switch_in_progress": "Aguarde a troca de mapa em andamento.",
        "dry_run_switch_title": "Modo simulação",
        "dry_run_switch_body": "Simularia troca para:\n{instruction}\n{label}",
        "confirm_switch_title": "Confirmar troca",
        "confirm_switch_body": "Ir para:\n{instruction}\n{label}?",
        "log_rotation_saved": "Rotação salva.",
        "log_monitor_started": "Monitor iniciado.",
        "log_monitor_stopped": "Monitor parado pelo usuário.",
        "log_monitor_error": "Erro no monitor: {error}",
        "log_switching_to": "Trocando para {label}...",
        "log_switch_complete": "Troca concluída: {label}",
        "log_switch_error": "Erro ao trocar mapa: {error}",
        "map_in_game": "Mapa em jogo: {label} (stageKey={stage_key}, {stage_label})",
        "stage_not_in_rotation": "Fase atual ({stage_label}, key={stage_key}) não está na rotação configurada",
        "save_status_unknown": "Save: stageKey={stage_key} | baús de chefe={boss_count}",
        "save_status_known": "Save: stageKey={stage_key} | mapa={label} | baús de chefe={boss_count}",
        "boss_chest_detected_lv": "Baú de chefe Lv {level} detectado — expira em {minutes} minutos",
        "boss_chest_detected": "Baú de chefe detectado — expira em {minutes} minutos",
        "drop_ignored_not_in_rotation": "Drop ignorado: a fase em que você está não está na rotação configurada",
        "ignored_reason": "Ignorado: {reason}",
        "drop_advance_next": "Drop em {from_label} — troque manualmente para: {to_label} ({instruction})",
        "simulation_next_map": "[simulação] Próximo mapa sugerido: {label} ({instruction})",
        "monitor_started": "Monitor iniciado [{mode}] | save={save_name}",
        "rotation_configured": "Rotação configurada: {labels}",
        "file_not_found": "Arquivo não encontrado: {error}",
        "error_read_save": "Erro ao ler save: {error}",
        "error_read_player_log": "Erro ao ler Player.log: {error}",
        "cannot_read_save": "Não foi possível ler o save: {error}",
        "monitor_stopped": "Monitor parado",
        "mode_simulation": "simulação",
        "mode_active": "ativo",
        "switch_save_restart": "save + reinício",
        "switch_ui_clicks": "cliques na UI",
        "farm_maps_only_hint": "Cada linha abaixo mostra o baú nativo daquele mapa.",
        "drop_reason_common_ignored": "Baú comum ignorado (opção desativada)",
        "drop_reason_common_no_rotation": "Baú comum não avança rotação (só baú de chefe)",
        "drop_reason_boss_detected": "Baú de chefe detectado no save",
        "drop_reason_boss_not_monitored": "Baú de chefe {item_key} não monitorado neste mapa",
        "drop_reason_valid": "Drop válido para rotação",
        "rotation_order": "Rotação #{order}",
    },
    "en": {
        "app_title": "TBH Monitor — Chests & Rotation",
        "sidebar_title": "TBH Monitor",
        "language_label": "Language",
        "lang_pt_br": "Português (BR)",
        "lang_en": "English",
        "chest_timers_title": "Timers",
        "timers_drag_hint": "Auto-sorted by urgency · drag to adjust priority",
        "timers_next_phase": "Next phase: {instruction} ({chest})",
        "timers_none_enabled": "Configure chests on the left to see timers.",
        "watch_title": "Watched chests",
        "add_chest": "+ Add chest",
        "common_chest_short": "Common",
        "common_chest_lv_short": "Common Lv{level}",
        "common_chest_timer": "Common chest",
        "chest_kind_boss": "Boss",
        "chest_kind_common": "Common",
        "timer_waiting": "Waiting",
        "timer_active": "Active",
        "timer_expired": "Expired",
        "chest_name_4": "Stage Boss Box 4",
        "chest_name_5": "Stage Boss Box 5",
        "chest_name_7": "Stage Boss Box 7",
        "chest_name_15": "Stage Boss Box Lv15",
        "chest_name_20": "Stage Boss Box Lv20",
        "chest_name_30": "Stage Boss Box Lv30",
        "chest_name_40": "Stage Boss Box Lv40",
        "chest_name_50": "Stage Boss Box Lv50",
        "chest_name_65": "Stage Boss Box Lv65",
        "chest_name_80": "Stage Boss Box Lv80",
        "chest_name_short_4": "Box 4",
        "chest_name_short_5": "Box 5",
        "chest_name_short_7": "Box 7",
        "chest_name_short_15": "Lv15",
        "chest_name_short_20": "Lv20",
        "chest_name_short_30": "Lv30",
        "chest_name_short_40": "Lv40",
        "chest_name_short_50": "Lv50",
        "chest_name_short_65": "Lv65",
        "chest_name_short_80": "Lv80",
        "consider_common_chest": "Common chest",
        "dry_run_mode": "Simulation mode (log only)",
        "timer_duration_minutes": "Min",
        "start_monitor": "Start monitor",
        "stop_monitor": "Stop monitor",
        "save_rotation": "Save rotation",
        "status": "Status",
        "status_stopped": "Stopped",
        "status_running": "Running",
        "current_map": "Current map: {label}",
        "all_maps_title": "All game maps ({count})",
        "priority_hint": (
            "Priority = rotation order (1, 2, 3…). "
            "Switch maps manually in-game — the app only monitors and suggests the next one."
        ),
        "rotation_title": "Rotation",
        "chest_farm_title": "Chest farm",
        "header_chest_map": "Chest · Map",
        "chest_lv": "Chest Lv {level}",
        "chest_lv_short": "Chest Lv {level}",
        "log_chest_drop": "{time} · Chest Lv{level} · {map_name} — {difficulty}",
        "log_chest_drop_detail": "{time} · {kind} Lv{level} chest · {map_name} — {difficulty}",
        "log_chest_ignored": "{time} · Chest Lv{level} · {map_name} — ignored: {reason}",
        "log_timer_skipped": "{time} · {label} — timer already active, not restarted",
        "log_timer_not_watched": "{time} · Lv{level} · {map_name} — not in watched chests",
        "no_maps_for_chest": "No maps",
        "rotation_empty": "No active chests.",
        "you_are_here": " · here",
        "no_boss_chest": "No chest",
        "stage_short": "{act}.{stage}",
        "enemy_lv": "Enemy Lv {level}",
        "go_button": "Go",
        "events": "Drops",
        "filter_act": "Act:",
        "filter_difficulty": "Difficulty:",
        "filter_all": "All",
        "search_placeholder": "Search map…",
        "header_prio": "Prio",
        "header_map_chest": "Map · Boss chest",
        "act_stage_difficulty": "Act {act} · Stage {stage} · {difficulty}",
        "act_stage_arrow": "Act {act} → Stage {stage} → {difficulty}",
        "in_game_instruction": "In-game: Act {act} → Stage {stage} → {difficulty}",
        "error_no_maps_rotation": "Enable at least one chest level in the farm panel.",
        "success_rotation_saved": "Configuration saved successfully.",
        "error_no_maps_start": "Enable at least one chest level before starting.",
        "warning_switch_in_progress": "Wait for the map switch in progress.",
        "dry_run_switch_title": "Simulation mode",
        "dry_run_switch_body": "Would simulate switch to:\n{instruction}\n{label}",
        "confirm_switch_title": "Confirm switch",
        "confirm_switch_body": "Go to:\n{instruction}\n{label}?",
        "log_rotation_saved": "Rotation saved.",
        "log_monitor_started": "Monitor started.",
        "log_monitor_stopped": "Monitor stopped by user.",
        "log_monitor_error": "Monitor error: {error}",
        "log_switching_to": "Switching to {label}...",
        "log_switch_complete": "Switch complete: {label}",
        "log_switch_error": "Map switch error: {error}",
        "map_in_game": "Current map: {label} (stageKey={stage_key}, {stage_label})",
        "stage_not_in_rotation": "Current stage ({stage_label}, key={stage_key}) is not in configured rotation",
        "save_status_unknown": "Save: stageKey={stage_key} | boss chests={boss_count}",
        "save_status_known": "Save: stageKey={stage_key} | map={label} | boss chests={boss_count}",
        "boss_chest_detected_lv": "Boss chest Lv {level} detected — expires in {minutes} min",
        "boss_chest_detected": "Boss chest detected — expires in {minutes} min",
        "drop_ignored_not_in_rotation": "Drop ignored: current stage is not in configured rotation",
        "ignored_reason": "Ignored: {reason}",
        "drop_advance_next": "Drop on {from_label} — switch manually to: {to_label} ({instruction})",
        "simulation_next_map": "[simulation] Suggested next map: {label} ({instruction})",
        "monitor_started": "Monitor started [{mode}] | save={save_name}",
        "rotation_configured": "Configured rotation: {labels}",
        "file_not_found": "File not found: {error}",
        "error_read_save": "Error reading save: {error}",
        "error_read_player_log": "Error reading Player.log: {error}",
        "cannot_read_save": "Could not read save: {error}",
        "monitor_stopped": "Monitor stopped",
        "mode_simulation": "simulation",
        "mode_active": "active",
        "switch_save_restart": "save + restart",
        "switch_ui_clicks": "UI clicks",
        "farm_maps_only_hint": "Each row below shows that map's native boss chest.",
        "drop_reason_common_ignored": "Common chest ignored (option disabled)",
        "drop_reason_common_no_rotation": "Common chest does not advance rotation (boss only)",
        "drop_reason_boss_detected": "Boss chest detected in save",
        "drop_reason_boss_not_monitored": "Boss chest {item_key} not monitored on this map",
        "drop_reason_valid": "Valid drop for rotation",
        "rotation_order": "Rotation #{order}",
    },
}


def get_language() -> Language:
    return _current_language


def set_language(language: Language | str) -> None:
    global _current_language
    if isinstance(language, str):
        _current_language = Language.from_code(language)
    else:
        _current_language = language


def t(key: str, language: Language | None = None, **kwargs: object) -> str:
    locale = language or _current_language
    bucket = MESSAGES.get(locale.value, MESSAGES["en"])
    template = bucket.get(key, MESSAGES["en"].get(key, key))
    if kwargs:
        return template.format(**kwargs)
    return template


def translate_map_name(name: str, language: Language | None = None) -> str:
    from src.data.map_name_i18n import MAP_NAMES_PT_BR

    locale = language or _current_language
    if locale == Language.EN:
        return name
    return MAP_NAMES_PT_BR.get(name, name)


def difficulty_display_name(difficulty: str, language: Language | None = None) -> str:
    locale = language or _current_language
    if locale == Language.EN:
        return difficulty
    try:
        diff = Difficulty(difficulty)
    except ValueError:
        return difficulty
    names = {
        Difficulty.NORMAL: "Normal",
        Difficulty.NIGHTMARE: "Pesadelo",
        Difficulty.HELL: "Inferno",
        Difficulty.TORMENT: "Tormenta",
    }
    return names.get(diff, difficulty)


def format_act_stage(
    act: int,
    stage: int,
    difficulty: str,
    language: Language | None = None,
) -> str:
    return t(
        "act_stage_difficulty",
        language=language,
        act=act,
        stage=stage,
        difficulty=difficulty_display_name(difficulty, language),
    )


def format_act_stage_arrow(
    act: int,
    stage: int,
    difficulty: str,
    language: Language | None = None,
) -> str:
    return t(
        "act_stage_arrow",
        language=language,
        act=act,
        stage=stage,
        difficulty=difficulty_display_name(difficulty, language),
    )


def format_stage_short(
    act: int,
    stage: int,
    language: Language | None = None,
) -> str:
    return t("stage_short", language=language, act=act, stage=stage)


def format_watch_map_label(
    *,
    act: int,
    stage: int,
    difficulty: str,
    map_name: str | None = None,
    language: Language | None = None,
) -> str:
    stage_part = format_stage_short(act, stage, language=language)
    difficulty_part = difficulty_display_name(difficulty, language)
    if map_name:
        localized_name = translate_map_name(map_name, language)
        return f"{stage_part} {localized_name} · {difficulty_part}"
    return f"{stage_part} · {difficulty_part}"


def format_game_instruction_for_stage_key(
    stage_key: int,
    language: Language | None = None,
) -> str:
    from src.data.stage_catalog import find_catalog_entry
    from src.data.stage_codec import decode_stage_key

    entry = find_catalog_entry(stage_key)
    if entry is not None:
        return format_act_stage_arrow(
            entry.act,
            entry.stage,
            entry.difficulty,
            language=language,
        )

    stage = decode_stage_key(stage_key)
    return format_act_stage_arrow(
        stage.act,
        stage.stage,
        stage.difficulty.value,
        language=language,
    )


def format_watch_map_label_for_stage_key(
    stage_key: int,
    language: Language | None = None,
) -> str:
    from src.data.stage_catalog import find_catalog_entry
    from src.data.stage_codec import decode_stage_key

    entry = find_catalog_entry(stage_key)
    if entry is not None:
        return format_watch_map_label(
            act=entry.act,
            stage=entry.stage,
            difficulty=entry.difficulty,
            map_name=entry.name,
            language=language,
        )

    stage = decode_stage_key(stage_key)
    return format_watch_map_label(
        act=stage.act,
        stage=stage.stage,
        difficulty=stage.difficulty.value,
        language=language,
    )


def format_current_stage_label(
    stage_key: int,
    language: Language | None = None,
) -> str:
    from src.data.stage_catalog import find_catalog_entry
    from src.data.stage_codec import decode_stage_key

    entry = find_catalog_entry(stage_key)
    if entry is not None:
        return (
            f"{format_map_drop_label(act=entry.act, stage=entry.stage, map_name=entry.name, language=language)}"
            f" · {difficulty_display_name(entry.difficulty, language)}"
        )

    stage = decode_stage_key(stage_key)
    return format_watch_map_label(
        act=stage.act,
        stage=stage.stage,
        difficulty=stage.difficulty.value,
        language=language,
    )


def format_chest_level_label(level: int, language: Language | None = None) -> str:
    return t("chest_lv", language=language, level=level)


def chest_kind_label(chest_type, language: Language | None = None) -> str:
    from src.domain.chest_event import ChestType

    if chest_type == ChestType.NORMAL_BROWN:
        return t("chest_kind_common", language=language)
    return t("chest_kind_boss", language=language)


def format_map_drop_label(
    *,
    act: int,
    stage: int,
    map_name: str,
    language: Language | None = None,
) -> str:
    localized_name = translate_map_name(map_name, language)
    return f"{format_stage_short(act, stage, language=language)} {localized_name}"


def localized_map_label_for_stage_key(
    stage_key: int,
    language: Language | None = None,
) -> str:
    from src.data.stage_catalog import find_catalog_entry
    from src.data.stage_codec import decode_stage_key

    entry = find_catalog_entry(stage_key)
    if entry is not None:
        return (
            f"{format_map_drop_label(act=entry.act, stage=entry.stage, map_name=entry.name, language=language)}"
            f" — Lv{entry.enemy_level}"
        )

    stage = decode_stage_key(stage_key)
    return format_watch_map_label(
        act=stage.act,
        stage=stage.stage,
        difficulty=stage.difficulty.value,
        language=language,
    )


def localized_map_label(
    map_config,
    language: Language | None = None,
) -> str:
    return localized_map_label_for_stage_key(map_config.stage_key, language=language)


def format_chest_drop_log(
    *,
    chest_level: int,
    map_name: str,
    act: int,
    stage: int,
    difficulty: str,
    chest_kind: str,
    language: Language | None = None,
    dropped_at: datetime | None = None,
) -> str:
    timestamp = dropped_at or datetime.now()
    return t(
        "log_chest_drop_detail",
        language=language,
        time=timestamp.strftime("%H:%M:%S"),
        kind=chest_kind,
        level=chest_level,
        map_name=format_map_drop_label(
            act=act,
            stage=stage,
            map_name=map_name,
            language=language,
        ),
        difficulty=difficulty_display_name(difficulty, language),
    )
