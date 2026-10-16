"""Entidades de domínio do workflow."""

from dataclasses import dataclass


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
    acoes: tuple[Acao, ...] | None


@dataclass(frozen=True, slots=True)
class Transicao:
    """Representa a transição entre dois estados do workflow."""

    estado_anterior: str
    acao: str
    proximo_estado: str
    terminal: bool
