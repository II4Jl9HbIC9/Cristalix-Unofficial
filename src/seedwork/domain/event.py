# Copyright (c) 2024, II4Jl9HbIC9
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""События доменного уровня."""
from __future__ import annotations

__all__: typing.Sequence[str] = ("Event", "EventSourcedEvent")

import dataclasses
import datetime
import typing

from src.seedwork.domain.entity_uuid import EntityId
from src.seedwork.domain.value_object import ValueObject


@dataclasses.dataclass(frozen=True, kw_only=True)
class Event(ValueObject):
    """Основной класс для доменных событий в контексте DDD."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class EventSourcedEvent(Event):
    """Основной класс для доменных событий в контексте Event Sourcing."""

    type: str
    """Тип события, характеризующий его суть (как правило, название класса)."""

    aggregate_uuid: EntityId
    """Уникальный идентификатор агрегата, которому принадлежит событие."""

    occurred_at: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.utcnow)
    """Время, когда событие произошло. По умолчанию равно текущему времени по UTC."""

    @classmethod
    def default(
        cls,
        aggregate_uuid: EntityId,
        occurred_at: typing.Optional[datetime.datetime] = None,
        **kwargs: typing.Any,
    ) -> EventSourcedEvent:
        """Фабричный метод для инициализации события с
        по умолчанию заданными атрибутами.

        Parameters
        ----------
        aggregate_uuid : EntityId
            Уникальный идентификатор агрегата, которому
            пренадлежит событие.
        occurred_at : Optional[datetime]
            Время, когда событие произошло.
            По умолчанию равно текущему времени по UTC.
        kwargs : Any
            Дополнительный набор аргументов для универсального
            использования фабрики в дочерних событиях.
        """
        kwargs = {}
        if occurred_at is not None:
            kwargs["occurred_at"] = occurred_at

        event = cls(type=cls.__name__, aggregate_uuid=aggregate_uuid, **kwargs)

        return event
