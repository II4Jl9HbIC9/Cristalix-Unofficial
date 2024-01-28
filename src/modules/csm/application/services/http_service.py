from __future__ import annotations

import abc
import typing

if typing.TYPE_CHECKING:
    from src.modules.csm.domain.player_stats import PlayerStats


class ScrappingError(Exception):
    pass


class PlayerIdScrappingError(ScrappingError):
    pass


class AsyncHttpService(abc.ABC):
    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    async def request_player_api_uuid(self, player_nickname: str) -> str:
        ...

    @abc.abstractmethod
    async def request_player_stats(
        self, player_nickname: str, player_api_id: typing.Optional[str] = None,
    ) -> PlayerStats:
        ...
