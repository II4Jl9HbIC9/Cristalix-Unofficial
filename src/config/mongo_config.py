from __future__ import annotations

import pydantic_settings
import pydantic


class MongoConfig(pydantic_settings.BaseSettings):
    url: str = pydantic.Field(default="localhost:27017")
    csm_database: str = pydantic.Field(default="csm")
    csm_player_collection: str = pydantic.Field(default="players")
