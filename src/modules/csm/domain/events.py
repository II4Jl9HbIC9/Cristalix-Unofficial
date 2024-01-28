from __future__ import annotations

import dataclasses

from src.seedwork.domain.value_object import ValueObject


@dataclasses.dataclass(frozen=True)
class EventsStatistic(ValueObject):
    wins: int
    kills: int
    games: int
    deaths: int
