"""Motor responsável por coordenar a execução do workflow."""

from datetime import UTC, datetime
from typing import Any

from sme_workflow_sdk.aplicacao.decisao_resolver import DecisaoResolver
from sme_workflow_sdk.dominio.contexto import ContextoExecucao
from sme_workflow_sdk.dominio.entidades import Acao, Estado
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.dominio.resultado import ResultadoWorkflow


class MotorWorkflow:
    """Coordena a validação e a resolução das transições do workflow."""

    def __init__(self, configuracao: dict[str, Any]) -> None:
        """Inicializa o motor com uma configuração previamente validada.

        Args:
            configuracao (dict[str, Any]): Configuração do workflow carregada
                do YAML e validada pelo ConfiguradorWorkflow.
        """
        self._configuracao = configuracao
        self._estados = self._converter_estados(configuracao)
        self._decisao_resolver = DecisaoResolver(self._estados)

    @staticmethod
    def _converter_estados(
        configuracao: dict[str, Any],
    ) -> dict[str, Estado]:
        """Converte os estados da configuração em entidades do domínio.

        Transforma os dados de estados e ações da configuração em
        instâncias de Estado e Acao.

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
        """Valida uma ação do workflow.

        Delega ao DecisaoResolver a validação do estado, da ação e da
        consistência da transição configurada.

        Args:
            estado_atual (str): Nome do estado atual do workflow.
            acao (str): Nome da ação que se deseja executar.

        Raises:
            EstadoInvalidoError: Se o estado não estiver configurado.
            AcaoInvalidaError: Se a ação não for permitida ou se os dados
                da transição forem inválidos.

        Returns:
            ExecucaoValidada: Dados validados para a execução.
        """
        return self._decisao_resolver.validar(estado_atual, acao)

    def executar(
        self,
        dados_transicao: ExecucaoValidada,
        contexto: ContextoExecucao,
    ) -> ResultadoWorkflow:
        """Produz o resultado de uma execução validada do workflow.

        Deve ser chamado após a aplicação consumidora concluir com sucesso
        a regra de negócio associada à ação. Não executa regras de negócio
        nem persiste alterações.

        Args:
            dados_transicao (ExecucaoValidada): Dados da ação previamente
                validados.
            contexto (ContextoExecucao): Contexto da execução, incluindo
                identificador, autor e dados adicionais.

        Returns:
            ResultadoWorkflow: Resultado da transição, contendo os estados,
                a ação executada, os horários e o contexto da execução.
        """
        estado_atual = dados_transicao.estado_atual
        acao = dados_transicao.acao
        return ResultadoWorkflow(
            identificador=contexto.identificador,
            estado_anterior=estado_atual,
            acao=acao.nome,
            proximo_estado=acao.proximo_estado,
            terminal=acao.terminal,
            sucesso=True,
            inicio=dados_transicao.inicio_transicao,
            fim=datetime.now(UTC),
            autor=contexto.autor,
            contexto=contexto,
            mensagem="Transicao executada com sucesso!",
        )
