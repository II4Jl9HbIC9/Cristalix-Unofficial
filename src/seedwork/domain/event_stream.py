from __future__ import annotations

import typing
import dataclasses

from src.seedwork.domain.event import Event


@dataclasses.dataclass
class EventStream:
    events: list[Event]
    version: int
