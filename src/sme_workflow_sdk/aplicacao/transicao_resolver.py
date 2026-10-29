"""Resolução e validação das transições do workflow."""

from sme_workflow_sdk.dominio.entidades import Estado
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.excecoes.workflow import TransicaoInvalidaError


class TransicaoResolver:
    """Valida as transições de estado configuradas no workflow.

    Verifica se o próximo estado da ação existe na configuração, se o
    campo ``terminal`` possui um valor booleano e se a transição respeita
    as regras de consistência do workflow.

    Não executa regras de negócio nem realiza a persistência do estado.
    """

    def __init__(self, estados: dict[str, Estado]) -> None:
        """Inicializa o resolvedor com os estados configurados.

        Args:
            estados: Estados do workflow indexados pelo nome.
        """
        self._estados = estados

    def resolver(self, execucao: ExecucaoValidada) -> ExecucaoValidada:
        """Valida a transição associada a uma execução previamente validada.

        Verifica se o próximo estado está configurado, se o campo ``terminal``
        é booleano e se uma transição não terminal não aponta para o próprio
        estado atual.

        Após a validação, retorna a mesma instância de ``ExecucaoValidada``
        recebida, sem modificar seus dados.


        Args:
            execucao (ExecucaoValidada): Dados da execução previamente
                validados pelo DecisaoResolver.

        Returns:
            ExecucaoValidada: A própria instância recebida, após a validação.

        Raises:
            TransicaoInvalidaError: Se o próximo estado for inválido, não
            estiver configurado, se o campo ``terminal`` não for booleano ou
            se a transição não terminal retornar ao estado atual.
        """
        estado_atual = execucao.estado_atual
        acao = execucao.acao
        proximo_estado = acao.proximo_estado

        if not isinstance(proximo_estado, str) or not proximo_estado.strip():
            raise TransicaoInvalidaError(
                f"O próximo estado da ação '{acao.nome}' no estado "
                f"'{estado_atual}' é inválido."
            )

        if not isinstance(acao.terminal, bool):
            raise TransicaoInvalidaError(
                f"O campo 'terminal' da ação '{acao.nome}' no estado "
                f"'{estado_atual}' deve ser booleano."
            )

        if proximo_estado not in self._estados:
            raise TransicaoInvalidaError(
                f"O próximo estado '{proximo_estado}' da ação "
                f"'{acao.nome}' não existe na configuração."
            )

        if not acao.terminal and proximo_estado == estado_atual:
            raise TransicaoInvalidaError(
                f"A ação '{acao.nome}' do estado '{estado_atual}' "
                "não pode retornar ao mesmo estado."
            )

        return execucao
