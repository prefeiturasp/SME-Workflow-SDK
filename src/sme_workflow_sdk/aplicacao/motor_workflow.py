"""Motor responsável por coordenar a execução do workflow."""

from datetime import UTC, datetime
from typing import Any

from sme_workflow_sdk.aplicacao.decisao_resolver import DecisaoResolver
from sme_workflow_sdk.aplicacao.transicao_resolver import TransicaoResolver
from sme_workflow_sdk.dominio.contexto import ContextoExecucao
from sme_workflow_sdk.dominio.entidades import Acao, Estado
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.dominio.resultado import ResultadoWorkflow
from sme_workflow_sdk.excecoes.workflow import TransicaoInvalidaError


class MotorWorkflow:
    """Coordena a validação e a resolução das transições do workflow.

    Recebe uma configuração previamente carregada e validada pelo
    :class:`~sme_workflow_sdk.configuracao.configurador.ConfiguradorWorkflow`,
    converte seus estados e ações em entidades de domínio e delega a
    validação das decisões ao :class:`DecisaoResolver`.

    Após a aplicação consumidora executar com sucesso as regras de negócio
    associadas à ação, o motor retorna um dicionário com os dados da
    transição, os horários e o contexto da execução.

    O motor não executa regras de negócio específicas da aplicação
    consumidora nem persiste alterações.

    Exemplo:
        >>> from sme_workflow_sdk import ConfiguradorWorkflow, MotorWorkflow
        >>> configurador = ConfiguradorWorkflow()
        >>> configuracao = configurador.carregar("workflow.yaml")
        >>> configurador.validar(configuracao)
        >>> motor = MotorWorkflow(configuracao)
        >>> execucao = motor.validar("pendente", "aprovar")
    """

    def __init__(self, configuracao: dict[str, Any]) -> None:
        """Inicializa o motor com uma configuração previamente validada.

        Converte os estados e as ações da configuração em entidades de
        domínio e inicializa o resolvedor responsável pela validação
        das decisões. A configuração não é relida do arquivo YAML.

        Args:
            configuracao (dict[str, Any]): Configuração do workflow,
                previamente carregada e validada pelo ConfiguradorWorkflow.
        """
        self._configuracao = configuracao
        self._estados = self._converter_estados(configuracao)
        self._decisao_resolver = DecisaoResolver(self._estados)
        self._transicao_resolver = TransicaoResolver(self._estados)

    @staticmethod
    def _converter_estados(
        configuracao: dict[str, Any],
    ) -> dict[str, Estado]:
        """Converte os estados da configuração em entidades do domínio.

        Cria instâncias de :class:`Estado` e :class:`Acao` a partir dos
        estados e das ações declarados na configuração. Estados com
        ``acoes: null`` são representados com ``acoes=None``.

        Este método pressupõe que a configuração já foi validada pelo
        configurador.


        Args:
            configuracao (dict[str, Any]): Configuração validada contendo os
                estados e suas respectivas ações.

        Returns:
            dict[str, Estado]: Estados indexados por seus nomes.
        """
        estados: dict[str, Estado] = {}

        for nome_estado, dados_estado in configuracao["estados"].items():
            dados_acoes = dados_estado["acoes"]
            acoes: dict[str, Acao] | None = None

            if dados_acoes is not None:
                acoes = {
                    nome_acao: Acao(
                        nome=nome_acao,
                        proximo_estado=dados_acao["proximo_estado"],
                        terminal=dados_acao["terminal"],
                    )
                    for nome_acao, dados_acao in dados_acoes.items()
                }
            estados[nome_estado] = Estado(
                nome=nome_estado,
                acoes=acoes,
            )

        return estados

    def validar(self, estado_atual: str, acao: str) -> ExecucaoValidada:
        """Valida a ação solicitada e a transição correspondente.

        Verifica se o estado existe, se a ação está disponível e se a
        transição configurada é válida. Essa validação deve ocorrer antes
        de a aplicação consumidora executar a regra de negócio associada
        à ação.

        Args:
            estado_atual (str): Nome do estado atual do workflow.
            acao (str): Nome da ação solicitada.

        Raises:
            EstadoInvalidoError: Se o estado não estiver configurado.
            AcaoInvalidaError: Se a ação não estiver disponível para o
                estado ou se os dados da transição forem inválidos.
            TransicaoInvalidaError: Se a transição configurada for inválida.

        Returns:
            ExecucaoValidada: Dados validados para a execução.

        Examples:
            >>> execucao = motor.validar("pendente", "aprovar")
            >>> execucao.estado_atual
            'pendente'
        """
        execucao = self._decisao_resolver.validar(estado_atual, acao)
        return self._transicao_resolver.resolver(execucao)

    def executar(
        self,
        dados_transicao: ExecucaoValidada,
        contexto: ContextoExecucao,
    ) -> dict[str, Any]:
        """Produz o resultado de uma execução validada do workflow.

        Deve ser chamado após a aplicação consumidora concluir com sucesso
        a regra de negócio associada à ação. Utiliza os dados validados e o
        contexto recebido para montar o resultado da execução.

        Este método não executa regras de negócio, não altera o estado
        persistido da entidade de negócio e não realiza operações de
        persistência.

        Args:
            dados_transicao (ExecucaoValidada): Dados da transição
                previamente validados pelo motor.
            contexto (ContextoExecucao): Contexto da execução, incluindo
                identificador, autor e dados adicionais.

        Returns:
            dict[str, Any]: Dicionário com o resultado da execução, incluindo
                estado anterior, ação, próximo estado, terminalidade, sucesso,
                horários e contexto.

        Examples:
            >>> execucao = motor.validar("pendente", "aprovar")
            >>> resultado = motor.executar(execucao, contexto)
            >>> resultado["sucesso"]
            True
        """
        try:
            execucao = self._transicao_resolver.resolver(dados_transicao)
            sucesso = True
            mensagem = "Transição executada com sucesso!"
            acao = execucao.acao
            resultado = ResultadoWorkflow(
                identificador=contexto.identificador,
                estado_anterior=execucao.estado_atual,
                acao=acao.nome,
                proximo_estado=acao.proximo_estado,
                terminal=acao.terminal,
                sucesso=sucesso,
                inicio=execucao.inicio_transicao,
                fim=datetime.now(UTC),
                autor=contexto.autor,
                contexto=contexto,
                mensagem=mensagem,
            )
        except TransicaoInvalidaError as exc:
            estado_atual = dados_transicao.estado_atual
            resultado = ResultadoWorkflow(
                identificador=contexto.identificador,
                estado_anterior=estado_atual,
                acao=dados_transicao.acao.nome,
                proximo_estado=estado_atual,
                terminal=False,
                sucesso=False,
                inicio=dados_transicao.inicio_transicao,
                fim=datetime.now(UTC),
                autor=contexto.autor,
                contexto=contexto,
                mensagem=f"Transição não executada! {str(exc)}",
            )

        return resultado.para_dict()
