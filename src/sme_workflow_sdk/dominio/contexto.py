"""Contexto genérico de execução do workflow."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ContextoExecucao:
    """Armazena informações da execução do workflow."""

    identificador: str
    ator: str | None = None
    dados: Mapping[str, Any] = field(default_factory=dict)
