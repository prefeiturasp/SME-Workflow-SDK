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

    def __post_init__(self) -> None:
        """Valida os campos obrigatórios.

        Raises:
            ValueError: _description_
            ValueError: _description_
            TypeError: _description_
        """
        if not isinstance(self.nome, str):
            raise TypeError(
                "Acao.nome deve ser string, recebido "
                f"{type(self.nome).__name__}"
            )
        if not self.nome or not self.nome.strip():
            raise ValueError("Acao.nome não pode ser vazio")

        if not isinstance(self.proximo_estado, str):
            raise TypeError(
                "Acao.proximo_estado deve ser string, recebido "
                f"{type(self.proximo_estado).__name__}"
            )
        if not self.proximo_estado or not self.proximo_estado.strip():
            raise ValueError("Acao.proximo_estado não pode ser vazio")

        if not isinstance(self.terminal, bool):
            raise TypeError(
                "Acao.terminal deve ser bool, recebido "
                f"{type(self.terminal).__name__}"
            )


@dataclass(frozen=True, slots=True)
class Estado:
    """Representa um estado do workflow."""

    nome: str
    acoes: Mapping[str, Acao] | None

    def __post_init__(self) -> None:
        """_summary_.

        Raises:
            ValueError: _description_
            TypeError: _description_
            ValueError: _description_
        """
        if not isinstance(self.nome, str):
            raise TypeError(
                "Acao.nome deve ser string, recebido "
                f"{type(self.nome).__name__}"
            )
        if not self.nome or not self.nome.strip():
            raise ValueError("nome do estado não pode ser vazio")

        if not isinstance(self.acoes, Mapping):
            raise TypeError(
                "acoes deve ser Mapping | None, recebido "
                f"{type(self.acoes).__name__}"
            )

        try:
            MappingProxyType(dict(self.acoes))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"acoes inválidas: {exc}") from exc

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

    def __post_init__(self) -> None:
        """Valida os campos obrigatórios da transição.

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            TypeError: _description_
        """
        if not isinstance(self.estado_anterior, str):
            raise TypeError(
                "Acao.estado_anterior deve ser string, recebido "
                f"{type(self.estado_anterior).__name__}"
            )
        if not self.estado_anterior or not self.estado_anterior.strip():
            raise ValueError("Transicao.estado_anterior não pode ser vazio")

        if not isinstance(self.acao, str):
            raise TypeError(
                "Acao.acao deve ser string, recebido "
                f"{type(self.acao).__name__}"
            )
        if not self.acao or not self.acao.strip():
            raise ValueError("Transicao.acao não pode ser vazia")

        if not isinstance(self.proximo_estado, str):
            raise TypeError(
                "Acao.proximo_estado deve ser string, recebido "
                f"{type(self.proximo_estado).__name__}"
            )
        if not self.proximo_estado or not self.proximo_estado.strip():
            raise ValueError("Transicao.proximo_estado não pode ser vazio")
        if not isinstance(self.terminal, bool):
            raise TypeError(
                f"Transicao.terminal deve ser bool, "
                f"recebido {type(self.terminal).__name__}"
            )
