"""Validação de estado e ação do workflow."""

from sme_workflow_sdk.dominio.entidades import Acao, Estado
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.excecoes import (
    AcaoInvalidaError,
    EstadoInvalidoError,
)


class DecisaoResolver:
    """Valida se uma ação está disponível no estado informado."""

    def __init__(self, estados: dict[str, Estado]) -> None:
        """Inicializa o resolvedor com a configuração do workflow.

        Args:
            estados (dict[str, Estado]): _description_
        """
        self._estados = estados

    def validar(self, estado_atual: str, acao: str) -> ExecucaoValidada:
        """Valida a existência do estado e a disponibilidade da ação.

        Args:
            estado_atual (str): _description_
            acao (str): _description_

        Returns:
            ExecucaoValidada: _description_
        """
        estado = self._validar_estado(estado_atual)
        acao_configurada = self._validar_acao(estado, acao)
        self._validar_transicao(estado_atual, acao_configurada)
        return ExecucaoValidada(
            estado_atual=estado_atual,
            acao=acao_configurada,
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
        estado = self._estados.get(estado_atual)

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

    def _validar_transicao(
        self,
        estado_atual: str,
        acao: Acao,
    ) -> None:
        """Verifica a consistência dos dados da transição.

        Args:
            estado_atual (str): _description_
            acao (Acao): _description_

        Raises:
            AcaoInvalidaError: _description_
            AcaoInvalidaError: _description_
            AcaoInvalidaError: _description_
            AcaoInvalidaError: _description_
        """
        proximo_estado = acao.proximo_estado

        if not isinstance(proximo_estado, str) or not proximo_estado.strip():
            raise AcaoInvalidaError(
                f"O próximo estado da ação '{acao.nome}' no estado "
                f"'{estado_atual}' é inválido."
            )

        if proximo_estado not in self._estados:
            raise AcaoInvalidaError(
                f"O próximo estado '{proximo_estado}' da ação "
                f"'{acao.nome}' não existe na configuração."
            )

        if not isinstance(acao.terminal, bool):
            raise AcaoInvalidaError(
                f"O campo 'terminal' da ação '{acao.nome}' no estado "
                f"'{estado_atual}' deve ser booleano."
            )

        if not acao.terminal and proximo_estado == estado_atual:
            raise AcaoInvalidaError(
                f"A ação '{acao.nome}' do estado '{estado_atual}' "
                "não pode retornar ao mesmo estado."
            )
