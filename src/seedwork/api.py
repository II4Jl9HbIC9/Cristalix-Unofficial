from __future__ import annotations

import dataclasses
import typing

GET: typing.Final[str] = "GET"
POST: typing.Final[str] = "POST"
PATCH: typing.Final[str] = "PATCH"
DELETE: typing.Final[str] = "DELETE"
PUT: typing.Final[str] = "PUT"


@dataclasses.dataclass
class Route:
    method: str
    path_template: str

    def compile(self, **kwargs):
        return CompiledRoute(
            route=self,
            compiled_path=self.path_template.format_map(kwargs),
        )


@dataclasses.dataclass
class CompiledRoute:
    route: Route
    compiled_path: str

    @property
    def method(self):
        return self.route.method

    def create_url(self, base_url: str) -> str:
        return base_url + self.compiled_path
