from __future__ import annotations


def str2int(s: str) -> int:
    if "." in s:
        s = s.split(".")[0]
    return int(s)


def seconds2hours(seconds: int) -> str:
    # FIXME щиткод
    hours = str(seconds // 3600)
    minutes = str((seconds % 3600) // 60)
    seconds = str((seconds % 3600) % 60)
    return f"{hours} ч. {minutes} мин. {seconds} сек."
