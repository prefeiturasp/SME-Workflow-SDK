"""Validação de estado e ação do workflow."""

from typing import Any

from sme_workflow_sdk.excecoes import (
    AcaoInvalidaError,
    EstadoInvalidoError,
)


class DecisaoResolver:
    """Valida se uma ação está disponível no estado informado."""

    def __init__(self, configuracao: dict[str, Any]) -> None:
        """Inicializa o resolvedor com a configuração do workflow."""
        self._estados = configuracao["estados"]

    def validar(self, estado_atual: str, acao: str) -> None:
        """Valida a existência do estado e a disponibilidade da ação."""
        if estado_atual not in self._estados:
            raise EstadoInvalidoError(
                f"O estado '{estado_atual}' não existe na configuração."
            )

        acoes = self._estados[estado_atual]["acoes"]

        if acoes is None or acao not in acoes:
            raise AcaoInvalidaError(
                f"A ação '{acao}' não é permitida no estado '{estado_atual}'."
            )
