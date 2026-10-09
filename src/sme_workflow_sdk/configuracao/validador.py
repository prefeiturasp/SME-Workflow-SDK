"""Validação da configuração de workflow."""

from typing import Any

from sme_workflow_sdk.excecoes import (
    ConfiguracaoWorkflowInvalidaError,
)


class ValidadorWorkflow:
    """Responsável por validar a configuração do workflow."""

    def validar(self, configuracao: dict[str, Any]) -> None:
        """Valida a configuração do workflow.

        Args:
            configuracao (dict[str, Any]): Configuração carregada do arquivo
                YAML.

        Raises:
            ConfiguracaoWorkflowInvalidaError: Se a configuração for inválida.
        """
        if not isinstance(configuracao, dict):
            raise ConfiguracaoWorkflowInvalidaError(
                "A configuração fornecida é inválida."
            )
        estados = configuracao.get("estados")

        if not isinstance(estados, dict) or not estados:
            raise ConfiguracaoWorkflowInvalidaError(
                "Campo 'estados' ausente ou inválido."
            )

        for nome_estado, dados_estado in estados.items():
            self._validar_estado(nome_estado, dados_estado)

    def _validar_estado(
        self,
        nome_estado: str,
        dados_estado: Any,
    ) -> None:
        """Valida a estrutura de um estado.

        Verifica se o nome do estado é uma string não vazia, se os dados
        são um dicionário, se o campo 'acoes' está presente e é um
        dicionário, e valida cada ação contida nele.

        Args:
            nome_estado (str): Nome do estado na configuração.
            dados_estado (Any): Dados associados ao estado.

        Raises:
            ConfiguracaoWorkflowInvalida:
                - Se o nome do estado não for uma string não vazia.
                - Se os dados do estado não forem um dicionário.
                - Se o estado não possuir o campo 'acoes'.
                - Se o campo 'acoes' não for um dicionário.
        """
        if not isinstance(nome_estado, str) or not nome_estado.strip():
            raise ConfiguracaoWorkflowInvalidaError(
                "O nome de cada estado deve ser uma string não vazia."
            )

        if not isinstance(dados_estado, dict):
            raise ConfiguracaoWorkflowInvalidaError(
                f"Dados do estado '{nome_estado}' inválidos."
            )

        if "acoes" not in dados_estado:
            raise ConfiguracaoWorkflowInvalidaError(
                f"O estado '{nome_estado}' deve possuir o campo 'acoes'."
            )

        acoes = dados_estado["acoes"]

        if not isinstance(acoes, dict):
            raise ConfiguracaoWorkflowInvalidaError(
                f"As ações do estado '{nome_estado}' estão no formato "
                "inválido."
            )

        for nome_acao, dados_acao in acoes.items():
            self._validar_acao(nome_estado, nome_acao, dados_acao)

    def _validar_acao(
        self,
        nome_estado: str,
        nome_acao: str,
        dados_acao: Any,
    ) -> None:
        """Valida a estrutura de uma ação de um estado.

        Verifica se o nome da ação é uma string não vazia, se os dados
        são um dicionário, se os campos 'proximo_estado' e 'terminal'
        estão presentes e se possuem os tipos esperados.

        Args:
            nome_estado (str): Nome do estado ao qual a ação pertence.
            nome_acao (str): Nome da ação na configuração.
            dados_acao (Any): Dados associados à ação.

        Raises:
            ConfiguracaoWorkflowInvalidaError:
                - Se o nome da ação não for uma string não vazia.
                - Se os dados da ação não forem um dicionário.
                - Se a ação não possuir o campo 'proximo_estado'.
                - Se 'proximo_estado' não for uma string não vazia.
                - Se a ação não possuir o campo 'terminal'.
                - Se o campo 'terminal' não for booleano.
        """
        if not isinstance(nome_acao, str) or not nome_acao.strip():
            raise ConfiguracaoWorkflowInvalidaError(
                f"O estado '{nome_estado}' possui uma ação "
                "com nome inválido."
            )

        if not isinstance(dados_acao, dict):
            raise ConfiguracaoWorkflowInvalidaError(
                f"A ação '{nome_acao}' do estado '{nome_estado}' "
                "está no formato inválido."
            )

        if "proximo_estado" not in dados_acao:
            raise ConfiguracaoWorkflowInvalidaError(
                f"A ação '{nome_acao}' do estado '{nome_estado}' "
                "deve possuir o campo 'proximo_estado'."
            )

        proximo_estado = dados_acao["proximo_estado"]

        if not isinstance(proximo_estado, str) or not proximo_estado.strip():
            raise ConfiguracaoWorkflowInvalidaError(
                f"O próximo estado da ação '{nome_acao}' "
                f"do estado '{nome_estado}' deve ser uma string "
                "não vazia."
            )

        if "terminal" not in dados_acao:
            raise ConfiguracaoWorkflowInvalidaError(
                f"A ação '{nome_acao}' do estado '{nome_estado}' "
                "deve possuir o campo 'terminal'."
            )

        if not isinstance(dados_acao["terminal"], bool):
            raise ConfiguracaoWorkflowInvalidaError(
                f"O campo 'terminal' da ação '{nome_acao}' "
                f"do estado '{nome_estado}' deve ser booleano."
            )
