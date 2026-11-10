"""Resolve e valida as decisões disponíveis no workflow.

Este módulo disponibiliza a classe DecisaoResolver, responsável por
verificar se o estado informado existe na configuração e se a ação
solicitada está disponível para esse estado.

Após validar a decisão, retorna uma instância de ExecucaoValidada,
que será utilizada pelo TransicaoResolver para verificar a consistência
da transição configurada.
"""

from sme_workflow_sdk.dominio.entidades import Acao, Estado
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.excecoes import (
    AcaoInvalidaError,
    EstadoInvalidoError,
)


class DecisaoResolver:
    """Resolve e valida as decisões permitidas em um workflow.

    Recebe os estados previamente convertidos em entidades de domínio
    pelo MotorWorkflow e verifica se o estado informado existe e se
    a ação solicitada está disponível para esse estado.

    Quando as validações são concluídas, retorna uma instância de
    ExecucaoValidada para processamento pelo TransicaoResolver.

    A validação do próximo estado, do campo ``terminal`` e das regras
    de consistência da transição não é responsabilidade desta classe.

    O resolvedor não executa regras de negócio nem realiza persistência.
    """

    def __init__(self, estados: dict[str, Estado]) -> None:
        """Inicializa o resolvedor com os estados do workflow.

        Armazena o mapeamento de estados previamente convertido em
        entidades de domínio, que será utilizado durante as validações.

        Args:
            estados (dict[str, Estado]): Dicionário de estados indexados por
                seus nomes.
        """
        self._estados = estados

    def validar(self, estado_atual: str, acao: str) -> ExecucaoValidada:
        """Valida a disponibilidade de uma ação no estado atual.

        Verifica se o estado informado existe na configuração e se
        disponibiliza a ação solicitada.

        Quando as validações são concluídas, cria e retorna uma instância
        de ExecucaoValidada contendo o estado atual, a ação correspondente
        e o horário de início da transição.

        A validação da consistência da transição é realizada posteriormente
        pelo TransicaoResolver.

        Args:
            estado_atual (str): Nome do estado atual do workflow.
            acao (str): Nome da ação solicitada.

        Raises:
            EstadoInvalidoError: Se o estado informado não existir
                na configuração.
            AcaoInvalidaError: Se o estado não possuir ações configuradas
            ou se a ação solicitada não estiver disponível nele.

        Returns:
            ExecucaoValidada: Dados da execução necessários para a etapa
                seguinte do processamento do workflow.
        """
        estado = self._validar_estado(estado_atual)
        acao_configurada = self._validar_acao(estado, acao)
        return ExecucaoValidada(
            estado_atual=estado_atual, acao=acao_configurada
        )

    def _validar_estado(self, estado_atual: str) -> Estado:
        """Obtém o estado informado na configuração do workflow.

        Consulta o mapeamento de estados utilizando o nome informado

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
        """Obtém a ação disponível no estado informado.

        Verifica se o estado possui ações configuradas e se a ação
        solicitada está disponível no mapeamento de ações do estado.

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
