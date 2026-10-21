"""Motor responsável por coordenar a execução do workflow."""

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from sme_workflow_sdk.aplicacao.decisao_resolver import DecisaoResolver
from sme_workflow_sdk.dominio import ContextoExecucao, ResultadoWorkflow
from sme_workflow_sdk.dominio.entidades import Acao, Estado


class MotorWorkflow:
    """Coordena a validação e a resolução das transições do workflow."""

    def __init__(self, configuracao: dict[str, Any]) -> None:
        """Inicializa o motor com uma configuração previamente validada."""
        self._configuracao = configuracao
        self._estados = self._converter_estados(configuracao)
        self._decisao_resolver = DecisaoResolver({"estados": self._estados})

    @staticmethod
    def _converter_estados(
        configuracao: dict[str, Any],
    ) -> dict[str, Estado]:
        """Converte a configuração YAML em entidades do domínio."""
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

    def validar_estado(self, estado_atual: str, acao: str) -> None:
        """Valida se a ação está disponível no estado atual."""
        self._decisao_resolver.validar(estado_atual, acao)

    def executar(
        self,
        estado_atual: str,
        acao: str,
        contexto: ContextoExecucao,
        inicio: datetime | None = None,
    ) -> ResultadoWorkflow:
        """Resolve a transição após a aplicação confirmar a regra de negócio.

        Este método deve ser chamado somente após a aplicação consumidora
        concluir com sucesso sua regra de negócio.

        Args:
            estado_atual: Estado atual do processo.
            acao: Ação executada.
            contexto: Contexto da execução.
            inicio: Instante inicial da execução. Se omitido, usa o instante
                atual em UTC.

        Returns:
            ResultadoWorkflow: Resultado da transição configurada.
        """
        self.validar_estado(estado_atual, acao)

        instante_fim = datetime.now(UTC)
        instante_inicio = inicio or instante_fim

        dados_acao: Mapping[str, Any] = self._configuracao["estados"][
            estado_atual
        ]["acoes"][acao]

        return ResultadoWorkflow(
            identificador=contexto.identificador,
            estado_anterior=estado_atual,
            acao=acao,
            proximo_estado=dados_acao["proximo_estado"],
            terminal=dados_acao["terminal"],
            sucesso=True,
            inicio=instante_inicio,
            fim=instante_fim,
            autor=contexto.autor,
            contexto=contexto,
            mensagem="OK",
        )
