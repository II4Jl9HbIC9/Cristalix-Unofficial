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
    "ApplicationModule",
    "Application",
    "TransactionContext",
)

import importlib
import typing
import types
import collections

from src.seedwork import metaprogramming
from src.seedwork import util
from src.seedwork.domain.event import Event
from src.seedwork.application.event import IntegrationEvent
from src.seedwork.application.event_handler import EventResult
from src.seedwork.application.event_handler import EventResultSet
from src.seedwork.application.query_handler import QueryResult
from src.seedwork.application.command_handler import CommandResult
from src.seedwork.application.ioc import DependencyProvider

if typing.TYPE_CHECKING:
    from src.seedwork.application.command import Command
    from src.seedwork.application.query import Query
    from src.seedwork.application.event_handler import EventHandlerType
    from src.seedwork.application.query_handler import QueryHandlerType
    from src.seedwork.application.command_handler import CommandHandlerType

    _QueryHandlerT = typing.TypeVar("_QueryHandlerT", bound=QueryHandlerType)
    _EventHandlerT = typing.TypeVar("_EventHandlerT", bound=EventHandlerType)
    _CommandHandlerT = typing.TypeVar("_CommandHandlerT", bound=CommandHandlerType)

_CallableT = typing.TypeVar("_CallableT", bound=typing.Callable[..., typing.Any])


class TransactionContext:
    """Основной контекст для обработки транзакций (команд, запросов, событий).

    Parameters
    ----------
    application : Application
        Приложение, которое будет инициировать транзакции.
    overrides : Any
        Переопределение старых/определение новых зависимостей для
        получения зависимостей для обработчиков транзакций.
    """

    __slots__: typing.Sequence[str] = (
        "_task",
        "_overrides",
        "_application",
        "_next_commands",
        "_integration_events",
        "_dependency_provider",
    )

    def __init__(self, application: Application, **overrides: typing.Any) -> None:
        self._application = application
        self._overrides = overrides
        self._dependency_provider = application.dependency_provider
        self._task = None
        self._next_commands: list[Command] = []
        self._integration_events: list[IntegrationEvent] = []

    @typing.no_type_check
    def __enter__(self) -> typing.Self:
        self._application._on_enter_transaction_context(self)
        return self

    @typing.overload
    def __exit__(self, exc_type: None, exc_val: None, exc_tb: None) -> None:
        ...

    @typing.overload
    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: types.TracebackType,
    ) -> None:
        ...

    @typing.no_type_check
    def __exit__(
        self,
        exc_type: typing.Optional[type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[types.TracebackType],
    ) -> None:
        self._application._on_exit_transaction_context(self, exc_type, exc_val, exc_tb)

    async def execute_query(self, query: Query) -> QueryResult:
        """Получает обработчик для данного запроса и выполняет его.

        Parameters
        ----------
        query : Query
            Инстанс поискового запроса, который нужно выполнить.

        Returns
        -------
        QueryResult
            Результат, полученный по исполнению поискового запроса.

        Raises
        ------
        RuntimeError
            Возбуждается в случае, если в данном контексте уже
            выполняется другая задача.
        AssertionError
            В случае, если полученный результат не является QueryResult.
        """
        if self._task is not None:
            raise RuntimeError(
                "Cannot execute query while another task is being executed"
            )

        self._task = query

        handler_func = self._application.get_query_handler(query)
        dependencies = self._dependency_provider.dependencies_from_callable(
            handler_func, **self._overrides,
        )
        result = await handler_func(query, **dependencies)

        assert isinstance(
            result, QueryResult
        ), f"Got {result} instead of QueryResult from {handler_func}"
        return result

    async def execute_command(self, command: Command) -> CommandResult:
        """Получает обработчик для данной команды и выполняет его.

        Parameters
        ----------
        command : Command
            Инстанс команды, которую нужно выполнить.

        Returns
        -------
        CommandResult
            Результат, полученный по исполнению команды.

        Raises
        ------
        RuntimeError
            Возбуждается в случае, если в данном контексте уже
            выполняется другая задача.
        AssertionError
            В случае, если полученный результат не является CommandResult.
        """
        if self._task is not None:
            raise RuntimeError(
                "Cannot execute command while another task is being executed"
            )

        self._task = command

        handler_func = self._application.get_command_handler(command)
        dependencies = self._dependency_provider.dependencies_from_callable(
            handler_func, **self._overrides,
        )

        command_result = await handler_func(command, **dependencies) or CommandResult.success()
        assert isinstance(
            command_result, CommandResult
        ), f"Got {command_result} instead of CommandResult from {handler_func}"
        command_result = util.collect_domain_events(command_result, dependencies)

        self._next_commands = []
        self._integration_events = []
        event_queue = command_result.events.copy()
        while len(event_queue) > 0:
            event = event_queue.pop(0)
            if isinstance(event, IntegrationEvent):
                self.collect_integration_event(event)

            elif isinstance(event, Event):
                event_results = await self.handle_domain_event(event)
                self._next_commands.extend(event_results.commands)
                event_queue.extend(event_results.events)

        return CommandResult.success(payload=command_result.payload)

    async def handle_domain_event(self, event: Event) -> EventResultSet:
        """Получает все обработчики для данного события и выполняет их.

        Parameters
        ----------
        event : Event
            Инстанс поискового запроса, который нужно выполнить.

        Returns
        -------
        EventResultSet
            Результат, полученный по исполнению всех обработчиков события.

        Raises
        ------
        AssertionError
            В случае, если полученный результат не является EventResultSet.
        """
        event_results = []
        print(self._application.get_event_handlers(event))
        print(self._application._event_handlers)
        for handler_func in self._application.get_event_handlers(event):
            dependencies = self._dependency_provider.dependencies_from_callable(
                handler_func, **self._overrides,
            )
            event_result = await handler_func(event, **dependencies) or EventResult.success()
            assert isinstance(
                event_result, EventResult
            ), f"Got {event_result} instead of EventResult from {handler_func}"

            event_result = util.collect_domain_events(event_result, dependencies)
            event_results.append(event_result)

        return EventResultSet(event_results)

    def collect_integration_event(self, event: IntegrationEvent) -> None:
        """Добавляет интеграционный ивент в текущий контекст."""
        self._integration_events.append(event)

    def get_service(self, service_cls: typing.Any) -> typing.Any:
        """Получает сервис из текущего менеджера зависимостей."""
        return self._dependency_provider.get_dependency(service_cls)


class ApplicationModule:
    """Модуль приложения для транспортировки всей
    логики ограниченного контекста.

    Parameters
    ----------
    name : str
        Название модуля.
    version : float
        Текущая версия модуля.
    """

    __slots__: typing.Sequence[str] = (
        "_name",
        "_version",
        "_command_handlers",
        "_event_handlers",
        "_query_handlers",
    )

    def __init__(self, name: str, version: float) -> None:
        self._name = name
        self._version = version
        self._command_handlers: dict[type[Command], CommandHandlerType] = {}
        self._event_handlers: dict[type[Event], list[EventHandlerType]] = collections.defaultdict(list)
        self._query_handlers: dict[type[Query], QueryHandlerType] = {}

    @property
    def name(self) -> str:
        """Название модуля."""
        return self._name

    @property
    def version(self) -> float:
        """Текущая версия модуля."""
        return self._version

    def import_from(self, path: str) -> None:
        importlib.import_module(path)

    def register_query_handler(
        self,
        handler: QueryHandlerType,
        query_cls: typing.Optional[type[Query]] = None,
    ) -> None:
        """Регистрирует обработчик для конкретного запроса.

        Parameters
        ----------
        handler : QueryHandlerType
            Обработчик для указанного поискового запроса.
        query_cls : Optional[type[Query]]
            Тип поискового запроса, обработчик для которого
            нужно зарегистрировать.
        """
        if (query := query_cls) is None:
            query = metaprogramming.get_type_hints(handler, first=True)
        self._query_handlers[query] = handler

    def register_command_handler(
        self,
        handler: CommandHandlerType,
        command_cls: typing.Optional[type[Command]] = None,
    ) -> None:
        """Регистрирует обработчик для указанной команды.

        Parameters
        ----------
        handler : CommandHandlerType
            Обработчик для указанной команды.
        command_cls : Optional[type[Command]]
            Тип команды, обработчик для которой нужно
            зарегистрировать.
        """
        if (command := command_cls) is None:
            command = metaprogramming.get_type_hints(handler, first=True)
        self._command_handlers[command] = handler

    def register_event_handler(
        self,
        handler: EventHandlerType,
        event_cls: typing.Optional[type[Event]] = None,
    ) -> None:
        """Регистрирует обработчик для указанного события.

        Parameters
        ----------
        handler : EventHandlerType
            Обработчик для указанного события.
        event_cls : Optional[type[Event]]
            Тип события, обработчик для которого нужно
            зарегистрировать.
        """
        if (event := event_cls) is None:
            event = metaprogramming.get_type_hints(handler, first=True)
        self._event_handlers[event].append(handler)

    def query_handler(
        self, query_cls: typing.Optional[type[Query]] = None,
    ) -> typing.Callable[[_QueryHandlerT], _QueryHandlerT]:
        """Позволяет регистрировать обработчик для указанного поискового
        запроса, используя синтаксис декоратора.

        Parameters
        ----------
        query_cls : Optional[type[Query]]
            Тип поискового запроса, обработчик для которого
            нужно зарегистрировать.

        Returns
        -------
        Callable[[_QueryHandlerT], _QueryHandlerT]
            Декоратор обработчика для указанного поискового запроса.
        """
        def decorator(handler: _QueryHandlerT) -> _QueryHandlerT:
            self.register_query_handler(handler, query_cls)
            return handler

        return decorator

    def event_handler(
        self, event_cls: typing.Optional[type[Event]] = None,
    ) -> typing.Callable[[_EventHandlerT], _EventHandlerT]:
        """Позволяет регистрировать обработчик для указанного события,
        используя синтаксис декоратора.

        Parameters
        ----------
        event_cls : Optional[type[Event]]
            Тип события, обработчик для которого нужно
            зарегистрировать.

        Returns
        -------
        Callable[[_EventHandlerT], _EventHandlerT]
            Декоратор обработчика для указанного события.
        """
        def decorator(handler: _EventHandlerT) -> _EventHandlerT:
            self.register_event_handler(handler, event_cls)
            return handler

        return decorator

    def command_handler(
        self, command_cls: typing.Optional[type[Command]] = None,
    ) -> typing.Callable[[_CommandHandlerT], _CommandHandlerT]:
        """Позволяет регистрировать обработчик для указанной команды,
        используя синтаксис декоратора.

        Parameters
        ----------
        command_cls : Optional[type[Command]]
            Тип команды, обработчик для которой нужно
            зарегистрировать.

        Returns
        -------
        Callable[[_EventHandlerT], _EventHandlerT]
            Декоратор обработчика для указанной команды.
        """
        def decorator(handler: _CommandHandlerT) -> _CommandHandlerT:
            self.register_command_handler(handler, command_cls)
            return handler

        return decorator


class Application(ApplicationModule):
    """Приложение для обработки всех транзакций проекта.

    Parameters
    ----------
    name : str
        Название приложения.
    version : float
        Текущая версия приложения.
    """

    __slots__: typing.Sequence[str] = (
        "_modules",
        "_dependency_provider",
        "_on_exit_transaction_context",
        "_on_enter_transaction_context",
    )

    def __init__(
        self,
        name: str,
        version: float,
        dependency_provider: DependencyProvider[typing.Any, typing.Any],
    ) -> None:
        super().__init__(name, version)
        self._dependency_provider = dependency_provider
        self._on_enter_transaction_context = lambda ctx: None
        self._on_exit_transaction_context = lambda ctx, exc_type, exc_val, exc_tb: None
        self._modules: typing.Set[ApplicationModule] = {self}

    @property
    def dependency_provider(self) -> DependencyProvider[typing.Any, typing.Any]:
        """Возвращает инстанс текущего менеджера зависимостей."""
        return self._dependency_provider

    def configure_dependency_provider(self, instance: DependencyProvider[typing.Any, typing.Any]) -> None:
        """Устанавливает новый менеджер зависимостей.

        Parameters
        ----------
        instance : DependencyProvider[Any, Any]
            Инстанс нового менеджера зависимостей.

        Raises
        ------
        TypeError
            Возбуждается в случае, если переданный менеджер зависимостей
            не реализовывает интерфейс DependencyProvider.
        """
        if not isinstance(instance, DependencyProvider):
            raise TypeError(
                f"Expected instance of {DependencyProvider!r}"
            )
        self._dependency_provider = instance

    def include_module(self, module: ApplicationModule) -> None:
        """Добавляет новый модуль в приложение.

        Parameters
        ----------
        module : ApplicationModule
            Модуль, который необходимо добавить.

        Raises
        ------
        TypeError
            Возбуждается в случае, если указанный модуль не наследует
            класс ApplicationModule.
        """
        if not isinstance(module, ApplicationModule):
            raise TypeError(
                "Can only include ApplicationModule instances"
            )
        self._modules.add(module)

    def on_enter_transaction_context(self, callable_: _CallableT) -> _CallableT:
        """Добавляет хук, который будет триггериться каждый раз при
        инициализации транзакционного контекста.

        Parameters
        ----------
        callable_ : _CallableT
            Хук, который будет триггериться каждый раз при инициализации
            транзакционного контекста.
        """
        self._on_enter_transaction_context = callable_
        return callable_

    def on_exit_transaction_context(self, callable_: _CallableT) -> _CallableT:
        """Добавляет хук, который будет триггериться каждый раз при
        завершении транзакционного контекста.

        Parameters
        ----------
        callable_ : _CallableT
            Хук, который будет триггериться каждый раз при завершении
            транзакционного контекста.
        """
        self._on_exit_transaction_context = callable_
        return callable_

    def get_query_handler(self, query: Query) -> QueryHandlerType:
        """Возвращает обработчик указанного поискового запроса.

        Parameters
        ----------
        query : Query
            Тип поискового запроса, обработчик для которого
            необходимо получить.

        Raises
        ------
        KeyError
            Возбуждается в случае, если для указанного типа
            поискового запроса не было найдено обработчиков.

        Returns
        -------
        QueryHandlerType
            Обработчик для указанного поискового запроса.
        """
        query_cls = type(query)
        for app_module in self._modules:
            handler_func = app_module._query_handlers.get(query_cls)
            if handler_func is not None:
                return handler_func

        raise KeyError(f"No query handler found for command {query_cls}")

    def get_command_handler(self, command: Command) -> CommandHandlerType:
        """Возвращает обработчик указанной команды.

        Parameters
        ----------
        command : Command
            Тип команды, обработчик для которой
            необходимо получить.

        Raises
        ------
        KeyError
           Возбуждается в случае, если для указанного типа
           команды не было найдено обработчиков.

        Returns
        -------
        CommandHandlerType
            Обработчик для указанной команды.
        """
        command_cls = type(command)
        for app_module in self._modules:
            handler_func = app_module._command_handlers.get(command_cls)
            if handler_func is not None:
                return handler_func

        raise KeyError(f"No command handler found for command {command_cls}")

    def get_event_handlers(self, event: Event) -> list[EventHandlerType]:
        """Возвращает обработчик указанной команды.

        Parameters
        ----------
        event : Event
            Тип события, обработчики для которого
            необходимо получить.

        Returns
        -------
        list[EventHandlerType]
            Список обработчиков для указанного события.
        """
        event_cls = type(event)
        event_handlers = []
        for app_module in self._modules:
            event_handlers.extend(
                app_module._event_handlers.get(event_cls, [])
            )

        return event_handlers

    def transaction_context(self, **dependencies: typing.Any) -> TransactionContext:
        """Создаёт транзакционный контекст для текущего приложения.

        Parameters
        ----------
        dependencies : Any
            Зависимости для менеджера зависимостей транзакционного
            контекста, которые будут использованы при обработке
            запросов приложения (команд, событий, поисковых запросов).

        Returns
        -------
        TransactionContext
            Транзакционный контекст для текущего приложения.
        """
        return TransactionContext(self, **dependencies)

    async def execute_command(self, command: Command, **dependencies: typing.Any) -> CommandResult:
        """Выполняет указанную команду.

        Parameters
        ----------
        command : Command
            Тип команды, которую нужно выполнить.
        dependencies : Any
            Зависимости, которые будут использованы для выполнения
            указанной команды.

        Returns
        -------
        CommandResult
            Результат выполнения указанной команды.
        """
        with self.transaction_context(**dependencies) as ctx:
            return await ctx.execute_command(command)

    async def execute_query(self, query: Query, **dependencies: typing.Any) -> QueryResult[typing.Any]:
        """Выполняет указанный поисковый запрос.

        Parameters
        ----------
        query : Query
            Тип поискового запроса, который нужно выполнить.
        dependencies : Any
            Зависимости, которые будут использованы для выполнения
            указанного поискового запроса.

        Returns
        -------
        QueryResult[Any]
            Результат выполнения указанного поискового запроса.
        """
        with self.transaction_context(**dependencies) as ctx:
            return await ctx.execute_query(query)
