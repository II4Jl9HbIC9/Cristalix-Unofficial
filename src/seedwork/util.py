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

import typing

__all__: typing.Sequence[str] = ("collect_domain_events",)

from src.seedwork.application.command_handler import CommandResult
from src.seedwork.application.event_handler import EventResult
from src.seedwork.domain.repository import EventRepository

_ResultT = typing.TypeVar("_ResultT", CommandResult, EventResult)


def collect_domain_events(
    result: _ResultT, handler_kwargs: typing.Mapping[str, typing.Any],
) -> _ResultT:
    """Собирает новые события из репозиториев, которые используются
    обработчиком, добавляет в полученный респонс.

    Parameters
    ----------
    result : _ResultT
        Респонс, в который будут добавлены новые события, если таковы
        присутствуют.
    handler_kwargs : Mapping[str, Any]
        Параметры обработчика, из которых будут взяты лишь все
        дочерние классы `EventRepository` для дальнейшей обработки
        событий.
    """
    domain_events = []
    repositories = filter(
        lambda x: isinstance(x, EventRepository), handler_kwargs.values()
    )
    for repository in repositories:
        domain_events.extend(repository.collect_events())

    result.events.extend(domain_events)
    return result
