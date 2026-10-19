"""Contexto genérico de execução do workflow."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class ContextoExecucao:
    """Armazena informações da execução do workflow."""

    autor: str
    identificador: str = field(default_factory=lambda: str(uuid4()))
    dados: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Congela o dicionário de dados em um MappingProxyType."""
        object.__setattr__(self, "dados", MappingProxyType(dict(self.dados)))
