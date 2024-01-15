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
from __future__ import annotations

__all__: typing.Sequence[str] = ("Aggregate", "EventSourcedAggregate")

import abc
import functools
import typing

from src.seedwork.domain.business_rule import BusinessRuleValidationMixin
from src.seedwork.domain.entity import Entity

if typing.TYPE_CHECKING:
    from src.seedwork.domain.event import EventSourcedEvent


class Aggregate(Entity, BusinessRuleValidationMixin):
    """Основной класс для реализации агрегатов в контексте DDD."""


class EventSourcedAggregate(Aggregate, abc.ABC):
    """Основной класс для реализации подхода Event Sourcing в DDD агрегатах."""

    def __init__(self) -> None:
        self._events = []

    @property
    @typing.final
    def uncommitted_events(self) -> typing.Sequence[EventSourcedEvent]:
        """Последовательность ещё не обработанных событий."""
        uncommitted_events = self._events
        return tuple(uncommitted_events)

    @typing.final
    def register_event(self, event: EventSourcedEvent) -> None:
        """Регистрирует событие в агрегате.

        Parameters
        ----------
        event : EventSourcedEvent
            Событие, которое должно быть зарегистрировано.
        """
        self._events.append(event)

    @typing.final
    def _clear_events(self) -> None:
        """Очищает все неприменённые события агрегата."""
        self._events.clear()

    @typing.final
    def collect_events(self) -> typing.Sequence[EventSourcedEvent]:
        """Собирает все неприменённые события, делает копию и очищает очередь."""
        events = self._events[:]
        self._clear_events()
        return events

    @typing.final
    def _record_that(self, event: EventSourcedEvent) -> None:
        """Регистрирует событие и применяет его к текущему состоянию агрегата."""
        self._reconstruct_from_event(event)
        self.register_event(event)

    @typing.final
    def _reconstruct_from_event(self, event: EventSourcedEvent) -> None:
        """Применяет событие к текущему состоянию агрегата."""
        self._aggregate(event)

    @functools.singledispatchmethod
    @abc.abstractmethod
    def _aggregate(self, event: EventSourcedEvent) -> None:
        """Применяет событие к текущему агрегату.

        В дочерних классах переопределяется и регистрирует
        обработчики событий внутри агрегата.
        """
        raise ValueError(f"Unknown event {event!r}")
