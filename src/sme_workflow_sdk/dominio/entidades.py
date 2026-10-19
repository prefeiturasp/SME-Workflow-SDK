"""Entidades de domínio do workflow."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True, slots=True)
class Acao:
    """Representa uma ação configurada para um estado."""

    nome: str
    proximo_estado: str
    terminal: bool


@dataclass(frozen=True, slots=True)
class Estado:
    """Representa um estado do workflow."""

    nome: str
    acoes: Mapping[str, Acao] | None

    def __post_init__(self) -> None:
        """_summary_."""
        if self.acoes is not None:
            object.__setattr__(
                self, "acoes", MappingProxyType(dict(self.acoes))
            )


@dataclass(frozen=True, slots=True)
class Transicao:
    """Representa a transição entre dois estados do workflow."""

    estado_anterior: str
    acao: str
    proximo_estado: str
    terminal: bool
