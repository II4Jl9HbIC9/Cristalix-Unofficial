from __future__ import annotations

import typing

import alluka
import tanjun

from src.modules.csm.application.queries.get_player import GetPlayer
from src.seedwork.application.module import Application
from src.discord import util
from src.modules.csm.infrastructure import util as csm_util

if typing.TYPE_CHECKING:
    from src.modules.csm.domain.player import Player
    from src.seedwork.application.query_handler import QueryResult
    from src.modules.csm.domain.events import EventsStatistic
    from src.modules.csm.domain.csc import CscStatistic

component = tanjun.Component()


def _build_events_message(events_stats: EventsStatistic) -> str:
    # FIXME: это так быть не должно
    message = (
        f"**Cristalix Events**\n"
        f"Ивентов сыграно: {events_stats.games}\n"
        f"Побед: {events_stats.wins} (КД {round(events_stats.wins / (events_stats.games - events_stats.wins), 3)})\n"
        f"Убийств: {events_stats.kills}\n"
        f"Смертей: {events_stats.deaths} (КД {round(events_stats.kills / events_stats.deaths, 3)})\n"
    )
    return message


def _build_csc_message(csc_stats: CscStatistic) -> str:
    # FIXME: это так быть не должно
    message = (
        f"**Custom Steve Chaos**\n"
        f"Времени проведено: {csm_util.seconds2hours(csc_stats.time_played)}\n"
        f"Рейтинг: {csc_stats.rating}\n"
        f"Игр сыграно: {csc_stats.games_played}\n"
        f"Побед: {csc_stats.wins}\n"
        f"Поражений: {csc_stats.losses} (КД {round(csc_stats.wins / csc_stats.losses, 3)})\n"
        f"Побед в дуэли: {csc_stats.duel_wins}\n"
        f"Поражений в дуэли: {csc_stats.duel_losses} (КД {round(csc_stats.duel_wins / csc_stats.duel_losses, 3)})\n"
        f"Убийств игроков: {csc_stats.player_kills}\n"
        f"Смертей: {csc_stats.deaths}\n"
        f"Волн пройдено: {csc_stats.waves}\n"
        f"Мобов убито: {csc_stats.mob_kills}\n"
    )
    return message


@component.with_slash_command
@tanjun.with_str_slash_option("nickname", "Никнейм пользователя, статистику которого необходимо узнать.")
@tanjun.as_slash_command("статы", "Показывает статистику пользователя сервере мини-игр.")
async def get_active_scrims(ctx: tanjun.abc.Context, nickname: str, app: alluka.Injected[Application]) -> None:
    try:
        query_result: QueryResult[Player] = await app.execute_query(GetPlayer(nickname))
        if not query_result.has_errors():
            embed = util.success_message(
                title=f"Статистика игрока {query_result.payload.id}",
                message=(
                    _build_events_message(query_result.payload.stats.events_stats)
                    + "\n"
                    + _build_csc_message(query_result.payload.stats.csc_stats)
                ),
            )
            await ctx.respond(embed=embed)
            return

        embed = util.fail_command_message(query_result)
        await ctx.respond(embed=embed)

    except:
        # FIXME: Временная обработка всех на свете ошибок
        await ctx.respond(
            "Чёт пошло не так, обработку ошибок я ещё не сделал...\n"
            "Ну скорее всего ник указан некорректно. А мб и кулдаун..."
        )


@tanjun.as_loader
def load_components(client):
    client.add_component(component.copy())
