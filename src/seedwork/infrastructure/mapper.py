from __future__ import annotations

import abc
import typing

MapperEntityT = typing.TypeVar("MapperEntityT")
MapperModelT = typing.TypeVar("MapperModelT")


class DataMapper(typing.Generic[MapperEntityT, MapperModelT], abc.ABC):
    @abc.abstractmethod
    def model_to_entity(self, instance: MapperModelT) -> MapperEntityT:
        ...

    @abc.abstractmethod
    def entity_to_model(self, entity: MapperEntityT) -> MapperModelT:
        ...
