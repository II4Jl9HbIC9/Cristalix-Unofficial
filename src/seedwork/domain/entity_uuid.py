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

__all__: typing.Sequence[str] = ("EntityId",)

import dataclasses
import typing
import uuid

from src.seedwork.domain.value_object import ValueObject


@dataclasses.dataclass(frozen=True)
class EntityId(ValueObject):
    """Основной класс для реализации идентификаторов
    сущностей/агрегатов в контексте DDD.
    """

    integer: int
    """Числовое представление айди."""

    string: str
    """Строковое представление айди."""

    hex: str
    """Айди в формате hex."""

    @classmethod
    def next_id(cls) -> EntityId:
        """Фабричный метод для создания случайного айди в формате uuid4."""
        identifier = uuid.uuid4()
        return cls(integer=identifier.int, string=str(identifier), hex=identifier.hex)
