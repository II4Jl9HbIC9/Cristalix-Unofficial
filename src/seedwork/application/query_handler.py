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

__all__: typing.Sequence[str] = ("QueryResult", "QueryHandlerType",)

import dataclasses
import typing
import sys

if typing.TYPE_CHECKING:
    from src.seedwork.hints import OptExcInfo

    QueryErrors: typing.TypeAlias = tuple[str, typing.Optional[BaseException], OptExcInfo]


QueryHandlerType: typing.TypeAlias = typing.Callable[..., typing.Awaitable["QueryResult[typing.Any]"]]
"""Сокращённый алиас к типу обработчика запросов."""

_T = typing.TypeVar("_T")


@dataclasses.dataclass
class QueryResult(typing.Generic[_T]):
    """Респонс поискового запроса.

    Подход реализован для безопасной и более удобной обработки исключений.
    """

    payload: typing.Optional[_T] = dataclasses.field(default=None)
    """Результат поискового запроса."""

    errors: list[QueryErrors] = dataclasses.field(default_factory=list)
    """Ошибки, возникшие в результате выполнения поискового запроса."""

    def has_errors(self) -> bool:
        """Вернёт True, если результат выполнения поискового запроса
        содержит ошибки.
        """
        return len(self.errors) > 0

    def is_success(self) -> bool:
        """Вернёт True, если результат выполнения поискового запроса
        не содержит ошибок.
        """
        return not self.has_errors()

    @classmethod
    def failure(
        cls,
        message: str = "Failure",
        exception: typing.Optional[BaseException] = None,
    ) -> QueryResult[_T]:
        """Фабричный метод для создания респонса при возникновении
        ошибок в результате поискового запроса.

        Parameters
        ----------
        message: str
            Сообщение о проишествии, возникшем в результате выполнения
            поискового запроса.
        exception : Optional[BaseException]
            Исключение, возникшее в результате выполнения поискового
            запроса.
        """
        exception_info = sys.exc_info()
        errors = [(message, exception, exception_info)]
        result = cls(errors=errors)
        return result

    @classmethod
    def success(cls, payload: typing.Optional[_T] = None) -> QueryResult[_T]:
        """Фабричный метод для создания респонса при успешном выполнении
        поискового запроса.

        Parameters
        ----------
        payload : Optional[_T]
            Результат поискового запроса.
        """
        return cls(payload=payload)
