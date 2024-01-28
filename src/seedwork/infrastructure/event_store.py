from __future__ import annotations

import abc
import dataclasses

import typing

from src.seedwork.domain.aggregate import Aggregate

if typing.TYPE_CHECKING:
    from src.seedwork.domain.entity_uuid import EntityId
    from src.seedwork.domain.event_stream import EventStream

AggregateT = typing.TypeVar("AggregateT", bound=Aggregate)


class ConcurrentStreamWriteError(RuntimeError):
    pass


class EventStore(typing.Generic[AggregateT], abc.ABC):
    __slots__ = ()

    @abc.abstractmethod
    async def load_all(self) -> typing.Sequence[EventStream]:
        ...

    @abc.abstractmethod
    async def load_stream(self, aggregate_uuid: EntityId) -> EventStream:
        ...

    @abc.abstractmethod
    async def delete_stream(self, aggregate_uuid: EntityId) -> None:
        ...

    @abc.abstractmethod
    async def append_to_stream(self, aggregate: AggregateT) -> None:
        ...
