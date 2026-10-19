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
        """Congela o dicionário de dados em um MappingProxyType.

        Raises:
            ValueError: _description_
            ValueError: _description_
            TypeError: _description_
            ValueError: _description_
        """
        if not isinstance(self.autor, str):
            raise TypeError(
                "Acao.nome deve ser string, recebido "
                f"{type(self.autor).__name__}"
            )
        if not isinstance(self.autor, str) or not self.autor.strip():
            raise ValueError("autor deve ser uma string não vazia")

        if self.dados is None:
            raise ValueError("dados não pode ser None; use {} para vazio")

        if not isinstance(self.dados, Mapping):
            raise TypeError(
                f"dados deve ser Mapping, recebido {type(self.dados).__name__}"
            )

        try:
            MappingProxyType(dict(self.dados))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"dados não pôde ser convertido em mapping: {exc}"
            ) from exc

        object.__setattr__(self, "dados", MappingProxyType(dict(self.dados)))
