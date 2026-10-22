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
            configuracao (dict[str, Any]): _description_
        """
        self._configuracao = configuracao
        self._estados = self._converter_estados(configuracao)
        self._decisao_resolver = DecisaoResolver(self._estados)

    @staticmethod
    def _converter_estados(
        configuracao: dict[str, Any],
    ) -> dict[str, Estado]:
        """Converte a configuração YAML em entidades do domínio.

        Args:
            configuracao (dict[str, Any]): _description_

        Returns:
            dict[str, Estado]: _description_
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
        """Valida se a ação está disponível no estado atual.

        Args:
            estado_atual (str): _description_
            acao (str): _description_

        Returns:
            ExecucaoValidada: _description_
        """
        return self._decisao_resolver.validar(estado_atual, acao)

    def executar(
        self,
        dados_transicao: ExecucaoValidada,
        contexto: ContextoExecucao,
    ) -> ResultadoWorkflow:
        """Resolve a transição após a aplicação confirmar a regra de negócio.

        Este método deve ser chamado somente após a aplicação consumidora
        concluir com sucesso sua regra de negócio.

        Args:
            dados_transicao (ExecucaoValidada): _description_
            contexto (ContextoExecucao): _description_

        Returns:
            ResultadoWorkflow: Resultado da transição configurada.
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
