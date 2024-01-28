from __future__ import annotations

import abc
import inspect
import typing

from src.seedwork import metaprogramming

_KeyT = typing.TypeVar("_KeyT")
_ValueT = typing.TypeVar("_ValueT")


class DependencyProvider(abc.ABC, typing.Generic[_KeyT, _ValueT]):
    """Интерфейс для менеджмента зависимостями."""

    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    def register_dependency(self, identifier: _KeyT, dependency: _ValueT) -> None:
        """Регистрирует зависимость в хранилище.

        Parameters
        ----------
        identifier : _KeyT
            Ключ, по которому будет записана зависимость.
        dependency : _ValueT
            Инстанс зависимости, которую нужно зарегистрировать.
        """
        ...

    @abc.abstractmethod
    def get_dependency(self, identifier: _KeyT) -> _ValueT:
        """Получает зависимость по ключу.

        Parameters
        ----------
        identifier : _KeyT
            Ключ, по которому необходимо получить зависимость.

        Returns
        -------
        _ValueT
            Зависимость, если такова присутствует.

        Raises
        ------
        KeyError
            Возбуждается в случае, если зависимость по указанному
            ключу не найдена.
        """
        ...

    def _resolve_arguments(
        self, callable_parameters: typing.Mapping[str, typing.Any],
    ) -> typing.MutableMapping[str, typing.Any]:
        kwargs = {}
        for param_name, param_type in callable_parameters.items():
            if param_type is inspect.Parameter.empty:
                raise KeyError(f"No type hints found for param {param_type!r}.")

            kwargs[param_name] = self.get_dependency(param_type)  # KeyError

        return kwargs

    def dependencies_from_callable(
        self, callable_: typing.Callable[..., typing.Any], **overrides: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Получает зависимости от типов аннотаций вызываемого обьекта.

        Parameters
        ----------
        callable_ : Callable[..., Any]
            Вызываемый обьект, для которого нужно получить зависимости.
        overrides : Any
            Переопределение старых/определение новых зависимостей для
            получения зависимостей вызываемого обьекта.

        Returns
        -------
        Mapping[str, Any]
            Полученные зависимости вызываемого обьекта.
        """
        handler_type_hints = metaprogramming.get_type_hints(callable_, pop_first=True)
        dependencies = self._resolve_arguments(handler_type_hints)
        dependencies.update(**overrides)
        return dependencies

