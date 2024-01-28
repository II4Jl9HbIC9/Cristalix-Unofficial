from __future__ import annotations

import dataclasses
import typing

from src.seedwork.application.query import Query
from src.modules.csm.application.module import csm_module
from src.modules.csm.domain.player import Player
from src.modules.csm.domain.player_id import PlayerId
from src.modules.csm.application.services.query_service import PlayerQueryService
from src.seedwork.application.query_handler import QueryResult


@dataclasses.dataclass(frozen=True)
class GetPlayer(Query):
    nickname: str


@csm_module.query_handler()
async def get_player(
    query: GetPlayer, query_service: PlayerQueryService,
) -> QueryResult[Player]:
    player_read_model = await query_service.get_player(query.nickname)
    player = Player(
        id=PlayerId(player_read_model.nickname),
        api_uuid=player_read_model.api_uuid,
    )
    player.set_stats(player_read_model.stats)
    return QueryResult.success(payload=player)
