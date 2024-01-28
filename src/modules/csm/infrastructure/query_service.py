from __future__ import annotations

import typing

from src.modules.csm.domain.player_id import PlayerId
from src.modules.csm.domain.player import Player
from src.modules.csm.application.services.query_service import PlayerQueryService
from src.modules.csm.application.models.player_read_model import PlayerReadModel

if typing.TYPE_CHECKING:
    from src.modules.csm.domain.player_repository import PlayerRepository
    from src.modules.csm.application.services.http_service import AsyncHttpService


class MongoPlayerQueryService(PlayerQueryService):
    __slots__: typing.Sequence[str] = ("_repository", "_http_service",)

    def __init__(self, repository: PlayerRepository, http_service: AsyncHttpService) -> None:
        self._repository = repository
        self._http_service = http_service

    def _aggregate_from_read_model(self, read_model: PlayerReadModel) -> Player:
        player = Player(
            id=PlayerId(read_model.nickname),
            api_uuid=read_model.api_uuid,
        )
        return player

    async def get_player(self, nickname: str) -> PlayerReadModel:
        player = await self._repository.get_by_id(PlayerId(nickname))
        if player is None:
            player_api_uuid = await self._http_service.request_player_api_uuid(nickname)
            player_stats = await self._http_service.request_player_stats(
                nickname, player_api_id=player_api_uuid,
            )
            player_read_model = PlayerReadModel(
                nickname=nickname,
                api_uuid=player_api_uuid,
                stats=player_stats,
            )

            await self._repository.insert(
                self._aggregate_from_read_model(player_read_model)
            )
            return player_read_model

        player_stats = await self._http_service.request_player_stats(
            nickname, player_api_id=player.api_uuid,
        )
        player.set_stats(player_stats)

        player_read_model = PlayerReadModel(
            nickname=nickname,
            api_uuid=player.api_uuid,
            stats=player.stats,
        )
        return player_read_model
