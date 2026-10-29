"""Validação de estado e ação do workflow."""

from sme_workflow_sdk.dominio.entidades import Acao, Estado
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.excecoes import (
    AcaoInvalidaError,
    EstadoInvalidoError,
)


class DecisaoResolver:
    """Resolve e valida as decisões permitidas em um workflow.

    Verifica se o estado atual está configurado e se a ação solicitada
    está disponível para esse estado. Retorna os dados validados para
    que o fluxo de execução possa prosseguir com a validação da transição.

    A validação do próximo estado, do campo ``terminal`` e das regras
    específicas da transição é responsabilidade do TransicaoResolver.
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
        """Valida se uma ação está disponível no estado atual do workflow.

        Verifica a existência do estado informado e se ele permite a ação
        solicitada. Caso as validações sejam bem-sucedidas, retorna os dados
        necessários para a etapa seguinte do processamento do workflow.

        Args:
            estado_atual (str): Nome do estado atual do workflow.
            acao (str): Nome da ação solicitada.

        Raises:
            EstadoInvalidoError: Se o estado informado não existir
                na configuração.
            AcaoInvalidaError: Se a ação não estiver disponível no estado
                ou se os dados da transição forem inválidos.

        Returns:
            ExecucaoValidada: Dados validados para a execução da ação.
        """
        estado = self._validar_estado(estado_atual)
        acao_configurada = self._validar_acao(estado, acao)
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
