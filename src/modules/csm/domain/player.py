from __future__ import annotations

import typing

from src.seedwork.domain.aggregate import Aggregate

if typing.TYPE_CHECKING:
    from src.modules.csm.domain.player_id import PlayerId
    from src.modules.csm.domain.player_stats import PlayerStats


class Player(Aggregate):
    # Пока что анемичная модель агрегата игрока, ну чё поделать...

    def __init__(
        self,
        id: PlayerId,
        api_uuid: str,
    ) -> None:
        self._id = id
        self._api_uuid = api_uuid
        self._stats: typing.Optional[PlayerStats] = None

    @property
    def id(self) -> PlayerId:
        return self._id

    @property
    def api_uuid(self) -> str:
        return self._api_uuid

    @property
    def stats(self) -> PlayerStats:
        return self._stats

    def set_stats(self, stats: PlayerStats) -> None:
        self._stats = stats
