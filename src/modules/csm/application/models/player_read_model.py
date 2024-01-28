from __future__ import annotations

import dataclasses
import typing

from src.seedwork.domain.value_object import ValueObject

if typing.TYPE_CHECKING:
    from src.modules.csm.domain.player_stats import PlayerStats


@dataclasses.dataclass(frozen=True)
class PlayerReadModel(ValueObject):
    nickname: str
    api_uuid: str
    stats: PlayerStats
