from __future__ import annotations

import typing

import nox

BASE_REQUIREMENTS: typing.Final[tuple[str, ...]] = ("-r", "requirements.txt")
DEV_REQUIREMENTS: typing.Final[tuple[str, ...]] = ("-r", "dev-requirements.txt")


@nox.session
def pytest(session: nox.Session) -> None:
    session.install(*DEV_REQUIREMENTS)
    session.install(*BASE_REQUIREMENTS)

    session.run("pytest")
