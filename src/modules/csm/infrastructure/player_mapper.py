from __future__ import annotations

import typing

from src.seedwork.infrastructure.mapper import DataMapper
from src.modules.csm.domain.player import Player
from src.modules.csm.domain.player_id import PlayerId


class MongoPlayerModel(typing.TypedDict):
    _id: str
    api_uuid: str


class PlayerMapper(DataMapper[Player, MongoPlayerModel]):
    def model_to_entity(self, instance: MongoPlayerModel) -> Player:
        entity = Player(
            id=PlayerId(instance["_id"]),
            api_uuid=instance["api_uuid"],
        )
        return entity

    def entity_to_model(self, entity: Player) -> MongoPlayerModel:
        model = MongoPlayerModel(
            _id=entity.id,
            api_uuid=entity.api_uuid,
        )
        return model
