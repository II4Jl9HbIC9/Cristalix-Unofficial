from __future__ import annotations

import typing

from motor.motor_asyncio import AsyncIOMotorCollection

from src.modules.csm.domain.player_repository import PlayerRepository
from src.modules.csm.domain.player import Player
from src.modules.csm.domain.player_id import PlayerId
from src.modules.csm.infrastructure.player_mapper import PlayerMapper

if typing.TYPE_CHECKING:
    from src.seedwork.infrastructure.mapper import DataMapper


class MongoPlayerRepository(PlayerRepository):
    __slots__: typing.Sequence[str] = ("_collection", "_mapper",)

    mapper_class: typing.ClassVar[type[DataMapper[Player, typing.Any]]] = PlayerMapper

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self._collection = collection
        self._mapper = self.mapper_class()

    async def get_all(self) -> typing.Sequence[Player]:
        documents = self._collection.find({})
        players = [self._mapper.model_to_entity(doc) for doc in documents]
        return players

    async def get_by_id(self, entity_id: PlayerId) -> typing.Optional[Player]:
        document = await self._collection.find_one({"_id": entity_id})
        if document is not None:
            player = self._mapper.model_to_entity(document)
            return player

    async def insert(self, entity: Player) -> None:
        model = self._mapper.entity_to_model(entity)
        await self._collection.insert_one(model)

    async def save(self, entity: Player) -> None:
        model = dict(self._mapper.entity_to_model(entity))
        _id = model.pop("_id")
        await self._collection.update_one({"_id": _id}, model)

    async def delete_by_id(self, entity_id: PlayerId) -> None:
        await self._collection.delete_one({"_id": entity_id})
