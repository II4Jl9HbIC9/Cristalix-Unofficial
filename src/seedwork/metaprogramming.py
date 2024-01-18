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
"""Модуль, который содержит функционал выполняющий неочевидные задачи,
вроде эзотерики.
"""
from __future__ import annotations

__all__: typing.Sequence[str] = ("get_type_hints",)

import inspect
import typing

if typing.TYPE_CHECKING:
    AnyType: typing.TypeAlias = typing.Type[typing.Any]


@typing.overload
def get_type_hints(
    obj: typing.Callable[[], typing.Any],
    first: bool = False,
    pop_first: bool = False
) -> typing.Mapping[str, AnyType]:
    ...

@typing.overload
def get_type_hints(
    obj: typing.Callable[[], typing.Any],
    key: str,
    first: bool = False,
    pop_first: bool = False
) -> AnyType:
    ...

@typing.overload
def get_type_hints(
    obj: typing.Callable[[], typing.Any],
    first: bool = True,
    pop_first: bool = False
) -> AnyType:
    ...

@typing.overload
def get_type_hints(
    obj: typing.Callable[[], typing.Any],
    pop_first: bool = True
) -> typing.Mapping[str, AnyType]:
    ...


def get_type_hints(
    obj: typing.Callable[[], typing.Any],
    key: typing.Optional[str] = None,
    first: bool = False,
    pop_first: bool = False,
) -> typing.Union[AnyType, typing.Mapping[str, AnyType]]:
    """Получает типы аннотаций аргументов функции.

    Parameters
    ----------
    obj : Callable[[], Any]
        Обьект типы аннотации которого нужно получить.
    key : Optional[str]
        Если указан, то будет возвращен тип аноотации
        конкретного аргумента, названия которого будет
        соответствовать ключу.
    first : bool
        Если True, вернёт тип аннотации первого аргумента.
    pop_first : bool
        Если True, вернёт все параметры, исключив первый.

    Raises
    ------
    KeyError
        Если key is not None и аргумент с соответствующим
        названием найти не удалось.

    Returns
    -------
    Union[AnyType, Mapping[str, AnyType]]
        Тип аннотации если first=True, в ином случае словарь,
        в котором ключом является название аргумента, а
        значением тип его аннотации.
    """
    sig = inspect.Signature.from_callable(obj, eval_str=True)
    types_ = {k: v.annotation for k, v in sig.parameters.items()}

    if first:
        first_value = types_[list(types_.keys())[0]]
        return first_value

    if pop_first:
        types_.pop(list(types_.keys())[0])
        return types_

    if key is not None:
        value = types_.get(key)
        if value is None:
            raise KeyError(f"Can't find key {key!r} in object annotations.")

        return value

    return types_
