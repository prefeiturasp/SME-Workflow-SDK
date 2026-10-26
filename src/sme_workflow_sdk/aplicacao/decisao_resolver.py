"""Validação de estado e ação do workflow."""

from sme_workflow_sdk.dominio.entidades import Acao, Estado
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.excecoes import (
    AcaoInvalidaError,
    EstadoInvalidoError,
)


class DecisaoResolver:
    """Valida estados, ações e consistência das transições do workflow.

    Recebe os estados convertidos em entidades de domínio pelo
    :class:`~sme_workflow_sdk.aplicacao.motor_workflow.MotorWorkflow`
    e verifica se a ação solicitada pode ser realizada no estado atual.

    A validação contempla a existência do estado, a disponibilidade da
    ação, a existência do estado de destino, o tipo do campo ``terminal``
    e a restrição de transições não terminais para o mesmo estado.

    O resolvedor não executa regras de negócio nem realiza persistência.
    Quando a validação é concluída, retorna uma instância de
    :class:`~sme_workflow_sdk.dominio.execucao_validada.ExecucaoValidada`.

    Exemplo:
        >>> execucao = resolver.validar("pendente", "aprovar")
        >>> execucao.estado_atual
        'pendente'
    """

    def __init__(self, estados: dict[str, Estado]) -> None:
        """Inicializa o resolvedor com os estados do workflow.

        Recebe o mapeamento de estados previamente convertido em entidades
        de domínio e o reutiliza nas validações das ações e transições.

        Args:
            estados (dict[str, Estado]): Dicionário de estados indexados por
                seus nomes.
        """
        self._estados = estados

    def validar(self, estado_atual: str, acao: str) -> ExecucaoValidada:
        """Valida uma ação e retorna os dados da execução validada.

        Executa, nesta ordem, a validação do estado atual, a verificação
        da ação disponível nesse estado e a validação da consistência
        dos dados da transição.

        Args:
            estado_atual (str): Nome do estado atual do workflow.
            acao (str): Nome da ação solicitada.

        Raises:
            EstadoInvalidoError: Se o estado informado não existir
                na configuração.
            AcaoInvalidaError: Se a ação não estiver disponível no estado
                ou se os dados da transição forem inválidos.

        Returns:
            ExecucaoValidada: ados validados para a execução, incluindo
                o estado atual, a ação configurada e o horário de início.

        Examples:
            >>> execucao = resolver.validar("pendente", "aprovar")
            >>> execucao.acao.nome
            'aprovar'
        """
        estado = self._validar_estado(estado_atual)
        acao_configurada = self._validar_acao(estado, acao)
        self._validar_transicao(estado_atual, acao_configurada)
        return ExecucaoValidada(
            estado_atual=estado_atual, acao=acao_configurada
        )

    def _validar_estado(self, estado_atual: str) -> Estado:
        """Obtém o estado informado ou lança uma exceção.

        Args:
            estado_atual (str): Nome do estado que será localizado.

        Raises:
            EstadoInvalidoError: Se o estado não estiver configurado.

        Returns:
            Estado: Entidade correspondente ao estado informado.
        """
        estado = self._estados.get(estado_atual)

        if estado is None:
            raise EstadoInvalidoError(
                f"O estado '{estado_atual}' não existe no arquivo de "
                "configuração."
            )
        return estado

    def _validar_acao(self, estado: Estado, nome_acao: str) -> Acao:
        """Obtém a ação configurada para o estado informado.

        Verifica se o estado possui ações configuradas e se a ação
        solicitada está disponível nesse estado.

        Args:
            estado (Estado): Estado em que a ação será procurada.
            nome_acao (str): Nome da ação solicitada.

        Raises:
            AcaoInvalidaError: Se o estado não possuir ações configuradas
                ou se a ação solicitada não estiver disponível nele.

        Returns:
            Acao:  Entidade correspondente à ação configurada.
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
        """Valida a consistência dos dados da transição.

        Verifica se o próximo estado está preenchido e existe na
        configuração, se o campo ``terminal`` é booleano e se uma
        transição não terminal evita retornar ao mesmo estado.

        Args:
            estado_atual (str):  Nome do estado de origem da transição.
            acao (Acao): Entidade que contém os dados da ação e da transição.

        Raises:
            AcaoInvalidaError:
                - Se o próximo estado for inválido ou não estiver configurado
                - se terminal não for booleano
                - se a transição não terminal retornar ao estado de origem.

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
