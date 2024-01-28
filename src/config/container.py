from __future__ import annotations

import typing

from dependency_injector import containers
from dependency_injector import providers
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from motor.motor_asyncio import AsyncIOMotorCollection

from src.config.mongo_config import MongoConfig
from src.modules.csm.application.module import csm_module
from src.seedwork.application.module import Application
from src.seedwork.infrastructure.ioc import IocProvider
from src.modules.csm.application.services.query_service import PlayerQueryService
from src.modules.csm.application.services.http_service import AsyncHttpService
from src.modules.csm.domain.player_repository import PlayerRepository
from src.modules.csm.infrastructure.query_service import MongoPlayerQueryService
from src.modules.csm.infrastructure.http_service import HttpxCristalixService
from src.modules.csm.infrastructure.player_repository import MongoPlayerRepository


def csm_engine(config: typing.Mapping[str, typing.Any]) -> AsyncIOMotorClient:
    engine = AsyncIOMotorClient(config["url"])
    return engine


def csm_database(engine: AsyncIOMotorClient, config: typing.Mapping[str, typing.Any]) -> AsyncIOMotorDatabase:
    database = engine[config["csm_database"]]
    return database


def csm_players_collection(
    database: AsyncIOMotorDatabase, config: typing.Mapping[str, typing.Any],
) -> AsyncIOMotorCollection:
    collection = database[config["csm_player_collection"]]
    return collection


def create_application() -> Application:
    csm_container = CsmContainer()
    csm_container.config.from_dict(MongoConfig().model_dump())

    application = Application(
        "CristalixUnofficialBot",
        0.1,
        # Временное решение, пока в боте только один модуль (и один контейнер).
        dependency_provider=IocProvider(csm_container),
    )
    application.include_module(csm_module)

    return application


class CsmContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    engine: AsyncIOMotorClient = providers.Singleton(
        csm_engine, config,
    )

    database: AsyncIOMotorDatabase = providers.Singleton(
        csm_database, engine, config,
    )

    player_collection: AsyncIOMotorCollection = providers.Singleton(
        csm_players_collection, database, config,
    )

    player_repository: PlayerRepository = providers.Factory(
        MongoPlayerRepository, player_collection,
    )

    cristalix_service: AsyncHttpService = providers.Factory(
        HttpxCristalixService,
    )

    player_query_service: PlayerQueryService = providers.Factory(
        MongoPlayerQueryService, player_repository, cristalix_service,
    )


class TopLevelContainer(containers.DeclarativeContainer):
    app: Application = providers.Singleton(create_application)
