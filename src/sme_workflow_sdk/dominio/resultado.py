"""Resultado estruturado de uma execução do workflow."""

from dataclasses import dataclass
from datetime import datetime

from sme_workflow_sdk.dominio import ContextoExecucao


@dataclass(frozen=True, slots=True)
class ResultadoWorkflow:
    """Representa o resultado da execução de uma ação do workflow."""

    identificador: str
    estado_anterior: str
    acao: str
    proximo_estado: str
    terminal: bool
    sucesso: bool
    inicio: datetime
    fim: datetime
    autor: str
    contexto: ContextoExecucao

    def __post_init__(self) -> None:
        """_summary_.

        Raises:
            TypeError: _description_
            ValueError: _description_
            ValueError: _description_
        """
        if not isinstance(self.contexto, ContextoExecucao):
            raise TypeError(
                "contexto deve ser ContextoExecucao, recebido "
                f"{type(self.contexto).__name__}"
            )
        if self.fim < self.inicio:
            raise ValueError(
                f"fim ({self.fim.isoformat()}) não pode ser anterior a inicio "
                f"({self.inicio.isoformat()})"
            )
        if not self.terminal and self.proximo_estado == self.estado_anterior:
            raise ValueError(
                "transição não-terminal não pode levar ao mesmo estado"
            )
