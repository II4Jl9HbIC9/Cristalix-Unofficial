from __future__ import annotations

import json
import typing

import bs4
import httpx
import fake_useragent

from src.seedwork.api import Route
from src.seedwork.api import GET
from src.seedwork.api import POST
from src.modules.csm.infrastructure import util
from src.modules.csm.domain.player_stats import PlayerStats
from src.modules.csm.domain.csc import CscStatistic
from src.modules.csm.domain.events import EventsStatistic
from src.modules.csm.application.services.http_service import AsyncHttpService
from src.modules.csm.application.services.http_service import PlayerIdScrappingError
from src.modules.csm.application.services.http_service import ScrappingError

if typing.TYPE_CHECKING:
    from src.seedwork.api import CompiledRoute

PLAYER_PROFILE_URL = "https://statistics.cristalix.gg/profile/"
PLAYER_STATS_URL = "https://testapistatistics.cristalix.gg/graphql"

PLAYER_PROFILE: Route = Route(GET, "{player_nickname}")
PLAYER_STATS: Route = Route(POST, "")


def _build_payloads(raw_payloads: list[typing.Mapping[str, typing.Any]]) -> dict[str, typing.Any]:
    # FIXME: щиткод + SRP
    # NOTE: получает 'statisticsMap': [{'__typename': 'PlayerStatisticsPairSchema', ...]
    processed_payloads = {}
    for raw_payload in raw_payloads:
        processed_payloads[raw_payload["field"]] = raw_payload["value"]

    return processed_payloads


def _build_csc_stats(payloads: list[typing.Mapping[str, typing.Any]]) -> CscStatistic:
    # FIXME: щиткод + SRP
    payloads = _build_payloads(payloads)

    statistic = CscStatistic(
        wins=util.str2int(payloads["wins"]),
        waves=util.str2int(payloads["waves"]),
        player_kills=util.str2int(payloads["killsPlayers"]),
        time_played=util.str2int(payloads["timePlayed"]),
        mob_kills=util.str2int(payloads["killsMobs"]),
        games_played=util.str2int(payloads["gamesPlayed"]),
        rating=util.str2int(payloads["rating"]),
        duel_losses=util.str2int(payloads["duelLosses"]),
        duel_wins=util.str2int(payloads["duelWins"]),
        losses=util.str2int(payloads["losses"]),
        deaths=util.str2int(payloads["deaths"]),
    )
    return statistic


def _build_events_stats(payloads: list[typing.Mapping[str, typing.Any]]) -> EventsStatistic:
    # FIXME: щиткод + SRP
    payloads = _build_payloads(payloads)

    statistic = EventsStatistic(
        wins=util.str2int(payloads["wins"]),
        kills=util.str2int(payloads["kills"]),
        games=util.str2int(payloads["games"]),
        deaths=util.str2int(payloads["deaths"]),
    )
    return statistic


def parse_player_id(response_text: str) -> str:
    # FIXME: щиткод
    soup = bs4.BeautifulSoup(response_text, "lxml")
    payload = json.loads(soup.find("script", id="__NEXT_DATA__").text)

    for value in payload["props"]["pageProps"]["__APOLLO_STATE__"]["ROOT_QUERY"].values():
        if "player" in value:
            player_id = value["player"]["__ref"].split(":")[1]
            return player_id

    else:
        raise PlayerIdScrappingError(
            "Can't find player id in received response."
        )


class HttpxCristalixService(AsyncHttpService):
    __slots__: typing.Sequence[str] = ("_allowed_categories",)

    def __init__(self) -> None:
        self._allowed_categories: typing.Sequence[str] = (
            "csc",
            "events",
        )

    async def _request(
        self,
        route: CompiledRoute,
        route_url: str,
        *,
        params: typing.Optional[typing.Mapping[str, str]] = None,
        data: typing.Optional[typing.Any] = None,
        json: typing.Optional[typing.Any] = None,
        headers: typing.Optional[typing.Mapping[str, str]] = None
    ) -> httpx.Response:
        # TODO: Нужен ли нам условный tenacity для повторного
        #       вызова запросов, в случае неудачи?
        async with httpx.AsyncClient() as client:
            url = route.create_url(route_url)
            try:
                response = await client.request(
                    route.method,
                    url,
                    json=json,
                    headers=headers,
                    params=params,
                    data=data,
                )
            except Exception as exc:
                # FIXME: когда-нибудь надо cделать адекватную
                #  обработку исключений.
                raise Exception() from exc

            return response

    async def request_player_api_uuid(self, player_nickname: str) -> str:
        profile_route = PLAYER_PROFILE.compile(player_nickname=player_nickname)
        profile_response = await self._request(profile_route, PLAYER_PROFILE_URL)
        try:
            html = profile_response.text
            player_api_uuid = parse_player_id(html)
        except PlayerIdScrappingError as exc:
            raise ScrappingError(
                f"Error occurred while scrapping player with nickname {player_nickname!r}"
            ) from exc

        return player_api_uuid

    async def request_player_stats(
        self, player_nickname: str, player_api_id: typing.Optional[str] = None,
    ) -> PlayerStats:
        if player_api_id is None:
            player_api_id = await self.request_player_api_uuid(player_nickname)

        stats_route = PLAYER_STATS.compile()

        stats_response = await self._request(
            stats_route,
            PLAYER_STATS_URL,
            headers={
                "authority": "testapistatistics.cristalix.gg",
                "accept": "*/*",
                "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "content-type": "application/json",
                "origin": "https://statistics.cristalix.gg",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": fake_useragent.UserAgent().random,
            },
            data=json.dumps({
                "operationName": "getProfileCategoriesStatistics",
                "variables": {"uuid": player_api_id},
                "query": """
                    query getProfileCategoriesStatistics($uuid: ID) {
                      feedAllCategoriesStatistics(id: $uuid) {
                        category
                        games {
                          game
                          statisticsMap {
                            field
                            value
                            __typename
                          }
                          __typename
                        }
                        __typename
                      }
                      getGamesCategories {
                        id
                        name
                        displayName
                        games {
                          name
                          displayName
                          modes {
                            name
                            displayName
                            __typename
                          }
                          __typename
                        }
                        translations {
                          fields {
                            field
                            label
                            __typename
                          }
                          __typename
                        }
                        __typename
                      }
                    }
                """
            },
        ))
        payload = stats_response.json()
        return self._build_player_stats(payload)

    def _build_player_stats(self, payload: typing.Mapping[str, typing.Any]) -> PlayerStats:
        # FIXME: щиткод + SRP
        categories = payload["data"]["feedAllCategoriesStatistics"]
        processed_categories = {}
        for category in categories:
            if (name := category["category"]) in self._allowed_categories:
                processed_categories[name] = category["games"][0]["statisticsMap"]

        player_stats = PlayerStats(
            csc_stats=_build_csc_stats(processed_categories["csc"]),
            events_stats=_build_events_stats(processed_categories["events"]),
        )
        return player_stats
