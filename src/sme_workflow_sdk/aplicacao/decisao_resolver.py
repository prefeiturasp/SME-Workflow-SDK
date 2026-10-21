"""Validação de estado e ação do workflow."""

from typing import Any

from sme_workflow_sdk.dominio.entidades import Acao, Estado
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
        estado = self._validar_estado(estado_atual)
        acao_configurada = self._validar_acao(estado, acao)

        proximo_estado = acao_configurada.proximo_estado

        if not isinstance(proximo_estado, str) or not proximo_estado.strip():
            raise AcaoInvalidaError(
                f"O próximo estado da ação '{acao}' no estado "
                f"'{estado_atual}' é inválido."
            )

        if proximo_estado not in self._estados:
            raise AcaoInvalidaError(
                f"O próximo estado '{proximo_estado}' da ação '{acao}' "
                "não existe na configuração."
            )

        terminal = acao_configurada.terminal

        if not isinstance(terminal, bool):
            raise AcaoInvalidaError(
                f"O campo 'terminal' da ação '{acao}' no estado "
                f"'{estado_atual}' deve ser booleano."
            )

        if not terminal and proximo_estado == estado_atual:
            raise AcaoInvalidaError(
                f"A ação '{acao}' do estado '{estado_atual}' não pode "
                "retornar ao mesmo estado."
            )

    def _validar_estado(self, estado_atual: str) -> Estado:
        """Verifica se o estado informado existe.

        Args:
            estado_atual (str): _description_

        Raises:
            EstadoInvalidoError: _description_

        Returns:
            Estado: _description_
        """
        estado: Estado = self._estados.get(estado_atual)

        if estado is None:
            raise EstadoInvalidoError(
                f"O estado '{estado_atual}' não existe no arquivo de "
                "configuração."
            )
        return estado

    def _validar_acao(self, estado: Estado, nome_acao: str) -> Acao:
        """Verifica se a ação está disponível no estado informado.

        Args:
            estado (Estado): _description_
            nome_acao (str): _description_

        Raises:
            AcaoInvalidaError: _description_

        Returns:
            Acao: _description_
        """
        acoes = estado.acoes

        if acoes is None or nome_acao not in acoes:
            raise AcaoInvalidaError(
                f"A ação '{nome_acao}' não é permitida "
                f"no estado '{estado.nome}'."
            )

        return acoes[nome_acao]
