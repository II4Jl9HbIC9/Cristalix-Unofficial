from __future__ import annotations

import inspect
import typing

from dependency_injector.providers import Provider
from dependency_injector.providers import Factory
from dependency_injector.providers import Singleton
from dependency_injector.providers import Dependency
from dependency_injector.containers import Container
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from dependency_injector import providers

from src.seedwork.application.ioc import DependencyProvider

Provide = Provide
inject = inject


def resolve_provider_by_type(container: Container, cls: type) -> typing.Optional[Provider]:
    def inspect_provider(provider: Provider) -> bool:
        if isinstance(provider, (Factory, Singleton)):
            return inspect.isclass(provider.cls) and issubclass(provider.cls, cls)
        elif isinstance(provider, Dependency):
            return issubclass(provider.instance_of, cls)

        return False

    matching_providers = inspect.getmembers(
        container,
        inspect_provider,
    )
    if matching_providers:
        if len(matching_providers) > 1:
            raise ValueError(
                f"Cannot uniquely resolve {cls}. Found IDK matching resources."
            )
        return matching_providers[0][1]

    return None


class IocProvider(DependencyProvider):
    def __init__(self, container):
        self.container = container

    def register_dependency(self, identifier, dependency_instance):
        setattr(self.container, identifier, providers.Object(dependency_instance))

    def get_dependency(self, identifier):
        provider = resolve_provider_by_type(self.container, identifier)
        instance = provider()
        return instance
