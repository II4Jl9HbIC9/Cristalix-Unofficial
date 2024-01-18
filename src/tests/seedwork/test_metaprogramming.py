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

import pytest

from src.seedwork.metaprogramming import get_type_hints


def test_get_type_hints_first() -> None:
    def sample_function(arg1: int, arg2: str) -> float:
        pass

    result = get_type_hints(sample_function, first=True)
    assert result is int  # Проверяем, что возвращается тип первого аргумента


def test_get_type_hints_pop_first() -> None:
    def sample_function(arg1: int, arg2: str, arg3: bool) -> float:
        pass

    result = get_type_hints(sample_function, pop_first=True)
    assert result == {'arg2': str, 'arg3': bool}  # Проверяем, что первый аргумент исключен из результата


def test_get_type_hints_key() -> None:
    def sample_function(arg1: int, arg2: str) -> float:
        pass

    result = get_type_hints(sample_function, key='arg2')
    assert result is str  # Проверяем, что возвращается тип для указанного ключа


def test_get_type_hints_invalid_key() -> None:
    def sample_function(arg1: int, arg2: str) -> float:
        pass

    with pytest.raises(KeyError, match=r"Can't find key 'arg3' in object annotations."):
        # Проверяем, что вызывается исключение при неверном ключе
        get_type_hints(sample_function, key='arg3')


def test_get_type_hints_full() -> None:
    def sample_function(arg1: int, arg2: str, arg3: bool) -> float:
        pass

    result = get_type_hints(sample_function)
    expected_result = {'arg1': int, 'arg2': str, 'arg3': bool}
    assert result == expected_result  # Проверяем полный результат
