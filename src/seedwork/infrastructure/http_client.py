from __future__ import annotations

import abc
import typing

import aiohttp

if typing.TYPE_CHECKING:
    from src.seedwork.api import CompiledRoute

ResponseT = typing.TypeVar("ResponseT")


class AsyncHttpClient(typing.Generic[ResponseT], abc.ABC):
    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    async def request(
        self,
        route: CompiledRoute,
        *,
        params: typing.Optional[typing.Mapping[str, str]] = None,
        data: typing.Optional[typing.Any] = None,
        json: typing.Optional[typing.Any] = None,
        headers: typing.Optional[typing.Mapping[str, str]] = None
    ) -> ResponseT:
        ...


class AiohttpClient(AsyncHttpClient[aiohttp.ClientResponse]):
    def __init__(self, rest_url: str) -> None:
        self._rest_url = rest_url

    @property
    def rest_url(self) -> str:
        return self._rest_url

    async def request(
        self,
        route: CompiledRoute,
        *,
        params: typing.Optional[typing.Mapping[str, str]] = None,
        data: typing.Optional[typing.Any] = None,
        json: typing.Optional[typing.Any] = None,
        headers: typing.Optional[typing.Mapping[str, str]] = None
    ) -> aiohttp.ClientResponse:
        # TODO: Нужен ли нам условный tenacity для повторного
        #       вызова запросов, в случае неудачи?
        async with aiohttp.ClientSession() as session:
            url = route.create_url(self.rest_url)
            try:
                response = await session.request(
                    route.method,
                    url,
                    headers=headers,
                    params=params,
                    data=data,
                )
            except Exception as exc:
                # FIXME: когда-нибудь надо cделать адекватную
                #  обработку исключений.
                raise Exception() from exc

            return response
