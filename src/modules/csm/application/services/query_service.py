from __future__ import annotations

import abc
import typing

if typing.TYPE_CHECKING:
    from src.modules.csm.application.models.player_read_model import PlayerReadModel


class PlayerQueryService(abc.ABC):
    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    async def get_player(self, nickname: str) -> PlayerReadModel:
        ...

