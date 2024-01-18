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

__all__: typing.Sequence[str] = ("CommandResult", "CommandHandlerType",)

import dataclasses
import typing
import sys

from src.seedwork.domain.event import Event
from src.seedwork.domain.entity_uuid import EntityId

if typing.TYPE_CHECKING:
    from src.seedwork.hints import ExcInfo
    from src.seedwork.hints import OptExcInfo

    CommandErrors: typing.TypeAlias = tuple[str, typing.Optional[BaseException], ExcInfo]

CommandHandlerType: typing.TypeAlias = typing.Callable[..., typing.Awaitable["CommandResult"]]


@dataclasses.dataclass
class CommandResult:
    """Результат выполнения определённой команды."""

    entity_id: typing.Optional[EntityId] = dataclasses.field(default=None)
    """Айди сущности/агрегата, связанное с выполнением команды."""

    payload: typing.Any = dataclasses.field(default=None)
    """Дополнительная информация, полученная в результате выполнения команды."""

    events: list[Event] = dataclasses.field(default_factory=list)
    """События, полученные в результате выполнения команды."""

    errors: list[CommandErrors] = dataclasses.field(default_factory=list)
    """Ошибки, возникшие в результате выполнения команды."""

    def has_errors(self) -> bool:
        """Вернёт True, если результат выполнения команды содержит ошибки."""
        return len(self.errors) > 0

    def is_success(self) -> bool:
        """Вернёт True, если результат выполнения команды не содержит ошибок."""
        return not self.has_errors()

    def add_error(
        self, message: str, exception: typing.Optional[BaseException], exception_info: OptExcInfo,
    ) -> None:
        """Добавляет ошибку к текущему результату исполнения команды.

        Parameters
        ----------
        message : str
            Сообщение об ошибке, произошедшей в результате
            выполнения команды.
        exception : Optional[BaseException]
            Инстанс ошибки, возникшей в результате выполнения
            указанной команды.
        exception_info : OptExcInfo
            Опциональная информация о произошедшей ошибке.
        """
        self.errors.append((message, exception, exception_info))

    @classmethod
    def failure(cls, message: str = "Failure", exception: typing.Optional[BaseException] = None) -> CommandResult:
        """Фабричный метод для создания респонса при возникновении
        ошибок в результате выполнения команды.

        Parameters
        ----------
        message: str
            Сообщение о проишествии, возникшем в результате выполнения
            указанной команды.
        exception : Optional[BaseException]
            Исключение, возникшее в результате выполнения команды
        """
        exception_info = sys.exc_info()
        result = cls()
        result.add_error(message, exception, exception_info)
        return result

    @classmethod
    def success(
        cls,
        entity_id: typing.Optional[EntityId] = None,
        payload: typing.Optional[typing.Any] = None,
        event: typing.Optional[Event] = None,
        events: typing.Optional[list[Event]] = None,
    ) -> CommandResult:
        """Фабричный метод для создания респонса при успешном выполнении
        поискового запроса.

        Parameters
        ----------
        entity_id : Optional[EntityId]
            Айди сущности/агрегата, связанное с выполнением команды.
        payload : Optional[Any]
            Дополнительная информация, полученная в результате выполнения команды.
        event : Optional[Event]
            События, полученные в результате выполнения команды.
        events : Optional[list[Event]]
            Ошибки, возникшие в результате выполнения команды.
        """
        if events is None:
            events = []

        if event:
            events.append(event)
            
        return cls(
            entity_id=entity_id,
            payload=payload,
            events=events,
        )
