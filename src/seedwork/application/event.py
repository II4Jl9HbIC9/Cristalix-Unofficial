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

__all__: typing.Sequence[str] = ("IntegrationEvent",)

import typing
import dataclasses

from src.seedwork.domain.event import Event


@dataclasses.dataclass(frozen=True, kw_only=True)
class IntegrationEvent(Event):
    """Основной класс для реализации интеграционных ивентов уровня приложения.

    Интеграционные события используются для общения между модулями/системами
    с использованием шаблона inbox-outbox. Они создаются в обработчике событий
    домена, а затем сохраняются в outbox для последующей доставки. В результате
    интеграционные события обрабатываются асинхронно.
    """
