from __future__ import annotations

from src.seedwork.application.module import ApplicationModule

csm_module = ApplicationModule("Cristalix Statistic Module", 0.1)
csm_module.import_from("src.modules.csm.application.queries")
