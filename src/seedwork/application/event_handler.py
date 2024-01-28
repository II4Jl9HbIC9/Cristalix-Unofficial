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

__all__: typing.Sequence[str] = (
    "EventId",
    "EventResult",
    "EventResultSet",
    "EventHandlerType",
)

import dataclasses
import typing
import sys

from src.seedwork.domain.entity_uuid import EntityId

if typing.TYPE_CHECKING:
    from src.seedwork.domain.event import Event
    from src.seedwork.application.command import Command
    from src.seedwork.hints import ExcInfo

    EventErrors: typing.TypeAlias = tuple[str, typing.Optional[BaseException], ExcInfo]

EventHandlerType: typing.TypeAlias = typing.Callable[..., typing.Awaitable["EventResult"]]


@dataclasses.dataclass(frozen=True)
class EventId(EntityId):
    """Айди определённого события."""


@dataclasses.dataclass
class EventResult:
    """Результат выполнения события (успех или провал) его обработчика."""

    event_id: typing.Optional[EventId] = dataclasses.field(default=None)
    """Айди обработанного события."""

    payload: typing.Any = dataclasses.field(default=None)
    """Дополнительная информация, полученная при обработке события."""

    command: Command = dataclasses.field(default=None)
    """Команда которая будет выполнена, как результат выполнения
    этого ивента (эксперементально).
    """

    events: list[Event] = dataclasses.field(default_factory=list)
    """События, возникшие в результате обработки данного события."""

    errors: list[EventErrors] = dataclasses.field(default_factory=list)
    """Ошибки, возникшие в результате обработки данного события."""

    def __post_init__(self) -> None:
        if self.event_id is None:
            self.event_id = EventId.next_id()

    def has_errors(self) -> bool:
        """Вернёт True, если результат исполнения события содержит ошибки."""
        return len(self.errors) > 0

    def is_success(self) -> bool:
        """Вернёт True, если результат исполнения события не содержит ошибок."""
        return not self.has_errors()

    def __hash__(self) -> int:
        return id(self)

    @classmethod
    def failure(cls, message: str = "Failure", exception: typing.Optional[BaseException] = None) -> EventResult:
        """Фабричный метод для создания респонса при возникновении
        ошибок в результате обработки события.

        Parameters
        ----------
        message: str
            Сообщение о проишествии, возникшем в результате выполнения
            указанного события.
        exception : Optional[BaseException]
            Исключение, возникшее в результате выполнения указанного
            события.
        """
        exception_info = sys.exc_info()
        errors = [(message, exception, exception_info)]
        result = cls(errors=errors)
        return result

    @classmethod
    def success(
        cls,
        event_id: typing.Optional[EventId] = None,
        payload: typing.Optional[typing.Any] = None,
        command: typing.Optional[Command] = None,
        event: typing.Optional[Event] = None,
        events: typing.Optional[list[Event]] = None,
    ) -> EventResult:
        """Фабричный метод для создания респонса при успешном выполнении
        указанного события.

        Parameters
        ----------
        event_id: Optional[EventId]
            Айди обработанного события.
        payload: Optional[Any]
            Дополнительная информация, полученная при обработке события.
        command: Optional[Command]
            Команда которая будет выполнена, как результат выполнения
            этого ивента (эксперементально).
        event: Optional[Event]
            События, возникшие в результате обработки данного события.
        events: Optional[list[Event]]
            Ошибки, возникшие в результате обработки данного события.
        """
        if events is None:
            events = []
        if event:
            events.append(event)

        return cls(
            event_id=event_id,
            payload=payload,
            command=command,
            events=events,
        )


class EventResultSet(set[EventResult]):
    """На данный момент просто красивое название для множества."""

    def is_success(self) -> bool:
        """Вернёт True, если все результаты исполнения событий
        данного множества являются успешными.
        """
        return all(r.is_success() for r in self)

    @property
    def events(self) -> list[Event]:
        """Возвращает события всех респонсов данного множества."""
        all_events = []
        for event in self:
            all_events.extend(event.events)
        return all_events

    @property
    def commands(self) -> list[Command]:
        """Возвращает команды всех респонсов данного множества."""
        all_commands = [event.command for event in self if event.command]
        return all_commands
