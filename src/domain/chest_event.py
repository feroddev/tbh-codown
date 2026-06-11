from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ChestType(str, Enum):
    BOSS = "boss"
    NORMAL_BROWN = "normal_brown"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ChestEvent:
    item_key: str
    chest_type: ChestType
    count: int
    raw_line: str
