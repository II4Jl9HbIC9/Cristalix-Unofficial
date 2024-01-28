from __future__ import annotations

import dataclasses
import typing

from src.seedwork.domain.value_object import ValueObject

if typing.TYPE_CHECKING:
    from src.modules.csm.domain.csc import CscStatistic
    from src.modules.csm.domain.events import EventsStatistic


@dataclasses.dataclass(frozen=True)
class PlayerStats(ValueObject):
    csc_stats: CscStatistic
    events_stats: EventsStatistic
