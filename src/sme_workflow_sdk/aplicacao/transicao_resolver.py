"""Resolução e validação das transições do workflow."""

from sme_workflow_sdk.dominio.entidades import Estado
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.excecoes import (
    AcaoInvalidaError,
    EstadoInvalidoError,
)


class TransicaoResolver:
    """Resolve e valida o destino de uma execução do workflow."""

    def __init__(self, estados: dict[str, Estado]) -> None:
        """Inicializa o resolvedor com os estados configurados.

        Args:
            estados: Estados do workflow indexados pelo nome.
        """
        self._estados = estados

    def resolver(self, execucao: ExecucaoValidada) -> ExecucaoValidada:
        """Valida a transição configurada para uma execução.

        Args:
            execucao: Estado atual e ação previamente validados.

        Returns:
            ExecucaoValidada: Execução com a transição validada.

        Raises:
            EstadoInvalidoError: Se o estado de destino não existir.
            AcaoInvalidaError: Se os dados da transição forem inválidos.
        """
        estado_atual = execucao.estado_atual
        acao = execucao.acao
        proximo_estado = acao.proximo_estado

        if not isinstance(proximo_estado, str) or not proximo_estado.strip():
            raise AcaoInvalidaError(
                f"O próximo estado da ação '{acao.nome}' no estado "
                f"'{estado_atual}' é inválido."
            )

        if not isinstance(acao.terminal, bool):
            raise AcaoInvalidaError(
                f"O campo 'terminal' da ação '{acao.nome}' no estado "
                f"'{estado_atual}' deve ser booleano."
            )

        if proximo_estado not in self._estados:
            raise EstadoInvalidoError(
                f"O próximo estado '{proximo_estado}' da ação "
                f"'{acao.nome}' não existe na configuração."
            )

        if not acao.terminal and proximo_estado == estado_atual:
            raise AcaoInvalidaError(
                f"A ação '{acao.nome}' do estado '{estado_atual}' "
                "não pode retornar ao mesmo estado."
            )

        return execucao
