from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MapConfig:
    priority: int
    label: str
    act: int
    stage: int
    difficulty: str
    stage_key: int
    ui: dict[str, dict[str, int | float]]
    enabled: bool = True
    boss_chest_keys: tuple[str, ...] = field(default_factory=tuple)
    best_boss_drop_keys: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RotationResult:
    previous_index: int
    current_index: int
    previous_map: MapConfig
    current_map: MapConfig
    wrapped_to_first: bool


class RotationEngine:
    def __init__(self, maps: list[MapConfig], current_index: int = 0) -> None:
        active_maps = [item for item in maps if item.enabled]
        if not active_maps:
            raise ValueError("At least one enabled map must be configured")

        self._maps = sorted(active_maps, key=lambda item: item.priority)
        normalized_index = self._normalize_index(current_index, maps)
        if normalized_index < 0 or normalized_index >= len(self._maps):
            normalized_index = 0

        self._current_index = normalized_index

    @staticmethod
    def _normalize_index(current_index: int, all_maps: list[MapConfig]) -> int:
        if not all_maps:
            return 0

        sorted_maps = sorted(all_maps, key=lambda item: item.priority)
        if current_index < len(sorted_maps):
            candidate = sorted_maps[current_index]
            enabled_maps = [item for item in sorted_maps if item.enabled]
            for index, enabled_map in enumerate(enabled_maps):
                if enabled_map.priority == candidate.priority:
                    return index

        return 0

    @property
    def maps(self) -> list[MapConfig]:
        return list(self._maps)

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def current_map(self) -> MapConfig:
        return self._maps[self._current_index]

    def find_index_by_stage_key(self, stage_key: int) -> int | None:
        for index, map_config in enumerate(self._maps):
            if map_config.stage_key == stage_key:
                return index
        return None

    def find_map_by_stage_key(self, stage_key: int) -> MapConfig | None:
        index = self.find_index_by_stage_key(stage_key)
        if index is None:
            return None
        return self._maps[index]

    def sync_to_stage_key(self, stage_key: int) -> MapConfig | None:
        index = self.find_index_by_stage_key(stage_key)
        if index is None:
            return None
        self._current_index = index
        return self._maps[index]

    def advance_on_chest_drop(self) -> RotationResult:
        previous_index = self._current_index
        previous_map = self._maps[previous_index]
        next_index = (previous_index + 1) % len(self._maps)
        self._current_index = next_index
        current_map = self._maps[next_index]

        return RotationResult(
            previous_index=previous_index,
            current_index=next_index,
            previous_map=previous_map,
            current_map=current_map,
            wrapped_to_first=next_index == 0 and len(self._maps) > 1,
        )
