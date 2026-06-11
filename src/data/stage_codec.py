from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Difficulty(str, Enum):
    NORMAL = "Normal"
    NIGHTMARE = "Nightmare"
    HELL = "Hell"
    TORMENT = "Torment"


DIFFICULTY_CODES: dict[int, Difficulty] = {
    1: Difficulty.NORMAL,
    2: Difficulty.NIGHTMARE,
    3: Difficulty.HELL,
    4: Difficulty.TORMENT,
}

DIFFICULTY_TO_CODE: dict[Difficulty, int] = {value: key for key, value in DIFFICULTY_CODES.items()}


@dataclass(frozen=True)
class StageIdentity:
    stage_key: int
    act: int
    stage: int
    difficulty: Difficulty

    @property
    def label(self) -> str:
        return f"{self.act}-{self.stage} ({self.difficulty.value})"


def encode_stage_key(act: int, stage: int, difficulty: Difficulty) -> int:
    return DIFFICULTY_TO_CODE[difficulty] * 1000 + act * 100 + stage


def decode_stage_key(stage_key: int) -> StageIdentity:
    difficulty_code = stage_key // 1000
    act = (stage_key % 1000) // 100
    stage = stage_key % 100
    difficulty = DIFFICULTY_CODES.get(difficulty_code)
    if difficulty is None:
        raise ValueError(f"Unsupported stage key: {stage_key}")
    return StageIdentity(stage_key=stage_key, act=act, stage=stage, difficulty=difficulty)


def difficulty_from_name(name: str) -> Difficulty:
    normalized = name.strip().lower()
    for difficulty in Difficulty:
        if difficulty.value.lower() == normalized:
            return difficulty
    raise ValueError(f"Unknown difficulty: {name}")
