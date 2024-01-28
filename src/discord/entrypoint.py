from __future__ import annotations

import pathlib
import os
import typing

import hikari
import tanjun

from src.seedwork.infrastructure.ioc import Provide
from src.seedwork.infrastructure.ioc import inject
from src.seedwork.application.module import Application
from src.config.container import TopLevelContainer
from src.config.container import CsmContainer

TEST_GUILD_ID: typing.Final[int] = 1190739228053749790


def walk_to_src() -> pathlib.Path:
    path = pathlib.Path(__file__)
    while path.stem != "src":
        path = path.parent

    return path


async def on_error(event: hikari.ExceptionEvent) -> None:
    # Временная реализация обработчика ошибок для бота,
    # в данном случае исключения ничего из себя не представляют,
    # только засоряют логи.
    if type(event.exception) in (hikari.BadRequestError, hikari.NotFoundError):
        return
    else:
        raise event.exception


@inject
def run(
    application: Application = Provide[TopLevelContainer.app],
    test_mode: bool = False,
) -> None:
    bot = hikari.GatewayBot(token=os.environ["BOT_TOKEN"])
    client = tanjun.Client.from_gateway_bot(
        bot,
        declare_global_commands=TEST_GUILD_ID if test_mode else True,
        mention_prefix=True,
    )
    client.load_modules(
        *filter(
            lambda x: not x.stem.startswith("_"),
            list((walk_to_src() / "discord" / "components").iterdir())
        )
    )
    client.set_type_dependency(Application, application)

    bot.run()


if __name__ == "__main__":
    csm_container = CsmContainer()
    csm_container.wire([__name__])

    app_container = TopLevelContainer()
    app_container.wire([__name__])

    # `test_mode=True` при локальном тестировании
    # команд, чтоб не пушить команды глобально,
    # что при злоупотреблении может привести к
    # дублированию команд и рейт лимитам.
    run()
