from __future__ import annotations

import dataclasses

from src.seedwork.domain.value_object import ValueObject


@dataclasses.dataclass(frozen=True)
class CscStatistic(ValueObject):
    wins: int  #
    waves: int
    player_kills: int  #
    time_played: int  #
    mob_kills: int
    games_played: int  #
    rating: int
    duel_losses: int  #
    duel_wins: int  #
    losses: int  #
    deaths: int  #
