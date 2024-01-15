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
    "EventRepository",
    "EventlessRepository",
    "EntityT_co",
    "EntityIdT",
)

import abc
import typing

from seedwork.domain.entity import Entity
from seedwork.domain.entity_uuid import EntityId

if typing.TYPE_CHECKING:
    from src.seedwork.domain.event import Event

EntityT_co = typing.TypeVar("EntityT_co", bound=Entity, covariant=True)
EntityIdT = typing.TypeVar("EntityIdT", bound=EntityId)


class EventlessRepository(typing.Generic[EntityIdT, EntityT_co], abc.ABC):
    """
    Интерфейс для стандартных реализаций репозиториев,
    которые не нуждаются в использовании ивентов.
    """

    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    async def get_by_id(self, entity_id: EntityIdT) -> typing.Optional[EntityT_co]:
        """Получает обьект сущности/агрегата по его айди.

        Parameters
        ----------
        entity_id : EntityIdT
            Уникальный идентификатор сущности/агрегата.

        Returns
        -------
        Optional[EntityT_co]
            Сущность/агрегат, None, в случае если по результату
            запроса ничего не найдено.
        """
        ...

    @abc.abstractmethod
    async def insert(self, entity: EntityT_co) -> None:
        """Заносит обьект в хранилище.

        Метод реализован отдельно от логики сохранения уже
        существующих, чтобы поддержать SRP и разгрузить
        инфраструктуру в целом.

        Parameters
        ----------
        entity : EntityT_co
            Сущность/агрегат для засенения в хранилище.
        """
        ...

    @abc.abstractmethod
    async def save(self, entity: EntityT_co) -> None:
        """Обновляет состояние уже существующего обьекта.

        Raises
        ------
        KeyError
            Если обновляемый обьект не находится в хранилище.
        """
        ...

    @abc.abstractmethod
    async def delete_by_id(self, entity_id: EntityIdT) -> None:
        """Удаляет агрегат/сущность из хранилища.

        Parameters
        ----------
        entity_id : EntityIdT
            Уникальный идентификатор обьекта, который нужно
            удалить из хранилища.
        """
        ...


class EventRepository(EventlessRepository[EntityIdT, EntityT_co], abc.ABC):
    """Реализация репозитория, взаимодействующего с архитектурой ивентов."""

    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    def collect_events(self) -> typing.Sequence[Event]:
        """Собирает все актуальные ивенты агрегатов/сущностей."""
        ...
