from __future__ import annotations

import secrets
import typing

import hikari

if typing.TYPE_CHECKING:
    from src.seedwork.application.command_handler import CommandResult


def random_hex(length: int = 6) -> int:
    hex_value = secrets.token_hex(length // 2)
    return int('0x' + hex_value, 16)


def fail_command_message(result: CommandResult) -> hikari.Embed:
    embed = hikari.Embed(color=0xA52A2A)
    for error in result.errors:
        err_msg, err, _ = error
        embed.add_field(name=str(err), value=err_msg)

    return embed


def success_message(title: str, message: str) -> hikari.Embed:
    embed = hikari.Embed(color=random_hex(), title=title, description=message)
    return embed
