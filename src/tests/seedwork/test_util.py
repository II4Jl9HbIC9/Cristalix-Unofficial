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

from unittest import mock

from src.seedwork.util import collect_domain_events


def test_collect_domain_events() -> None:
    mock_repository_1 = mock.MagicMock()
    mock_repository_2 = mock.MagicMock()

    mock_repository_1.collect_events.return_value = ["Event1", "Event2"]
    mock_repository_2.collect_events.return_value = ["Event3"]

    handler_kwargs = {"repo1": mock_repository_1, "repo2": mock_repository_2}
    result = mock.MagicMock()

    # Заменяем filter для возврата моков EventRepository
    with mock.patch("builtins.filter", side_effect=lambda *args: [mock_repository_1, mock_repository_2]):
        # Вызываем функцию, которую тестируем
        collect_domain_events(result, handler_kwargs)

    # Проверяем, что collect_events() был вызван для каждого мока
    mock_repository_1.collect_events.assert_called_once()
    mock_repository_2.collect_events.assert_called_once()

    # Проверяем, что результат функции содержит ожидаемые события
    result.events.extend.assert_called_once_with(["Event1", "Event2", "Event3"])
