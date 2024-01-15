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
"""Модуль, содержащий логику валидации в контексте DDD."""
from __future__ import annotations

__all__: typing.Sequence[str] = (
    "BusinessRule",
    "BusinessRuleValidationMixin",
    "BusinessRuleValidationError",
    "MessageCode",
)

import abc
import dataclasses
import typing

from src.seedwork.domain.value_object import ValueObject

MessageCode = typing.NewType("MessageCode", str)
"""Тип используется для выделения обычной строки в код сообщения, 
который в дальнейшем может быть использован в системе локализации 
приложения.

(В данном проекте может быть использован и для обычных сообщений, 
я разрешаю. Ибо вряд ли тут нужна будет локализация, но на перспективу 
пусть остаётся как есть).
"""


@dataclasses.dataclass(frozen=True)
class BusinessRule(ValueObject, abc.ABC):
    """Основной класс для реализации бизнес правил в контексте DDD."""

    @abc.abstractmethod
    def is_broken(self) -> bool:
        """True, если правило нарушено, в ином случае False."""
        ...

    @abc.abstractmethod
    def render_broken_rule(self) -> MessageCode:
        """Возвращает обработанный результат, который содержит
        сообщение о проблеме или ссылку на него.
        """
        ...


class BusinessRuleValidationMixin:
    """Миксин, содержащий логику проверки целости инвариантов в агрегате/сущности."""

    __slots__: typing.Sequence[str] = ()

    def assert_invariants(self, *rules: typing.Unpack[BusinessRule]) -> None:
        """Проверяет, соблюдены ли все указанные инварианты.

        Parameters
        ----------
        *rules : Unpack[BusinessRule]
            Бизнес правила (инварианты), которые должны быть соблюдены.

        Raises
        ------
        BusinessRuleValidationError
            В случае, если какое-то из бизнес правил нарушено.
        """
        violated_rules = []
        for rule in rules:
            if rule.is_broken():
                violated_rules.append(rule)

        if violated_rules:
            raise BusinessRuleValidationError(*violated_rules)


class BusinessRuleValidationError(Exception):
    """Возбуждается в случае, если какой-то инвариант был нарушен.

    Parameters
    ----------
    *rules : Unpack[BusinessRule]
        Бизнес правила (инварианты), которые должны быть соблюдены.
    """

    __slots__: typing.Sequence[str] = ("_rules",)

    def __init__(self, *rules: typing.Unpack[BusinessRule]) -> None:
        self._rules = rules
        super().__init__(self._render_broken_rules())

    def _render_broken_rules(self) -> str:
        broken_rules = ",".join(type(rule).__name__ for rule in self._rules)
        return f"Rules {broken_rules!r} are broken."
