from __future__ import annotations

import abc

from src.seedwork.domain.repository import EventlessRepository
from src.modules.csm.domain.player import Player
from src.modules.csm.domain.player_id import PlayerId


class PlayerRepository(EventlessRepository[PlayerId, Player], abc.ABC):
    pass
