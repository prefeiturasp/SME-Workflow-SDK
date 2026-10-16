"""Resultado estruturado de uma execução do workflow."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class WorkflowResult:
    """Representa o resultado da execução de uma ação do workflow."""

    identificador: str
    estado_anterior: str
    acao: str
    proximo_estado: str
    terminal: bool
    sucesso: bool
    inicio: datetime
    fim: datetime
    ator: str | None = None
    contexto: Mapping[str, Any] | None = None
