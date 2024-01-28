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

__all__: typing.Sequence[str] = ("Event",)

import dataclasses
import typing

from src.seedwork.domain.value_object import ValueObject


@dataclasses.dataclass(frozen=True, kw_only=True)
class Event(ValueObject):
    """Основной класс для доменных событий в контексте DDD."""

    @classmethod
    def from_dict(cls, mapping: dict[str, typing.Any]) -> Event:
        pass

    def as_dict(self) -> dict[str, typing.Any]:
        pass
