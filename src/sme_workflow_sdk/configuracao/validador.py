"""Validação da configuração de workflow."""

from typing import Any

from sme_workflow_sdk.excecoes.configuracao import EstadoInvalidoError


class ValidadorWorkflow:
    """Responsável por validar a configuração do workflow."""

    def validar(self, configuracao: dict[str, Any]) -> None:
        """Valida a configuração do workflow.

        Args:
            configuracao (dict[str, Any]): Configuração carregada do arquivo
                YAML.

        Raises:
            EstadoInvalidoError: Se a configuração for inválida.
        """
        if not isinstance(configuracao, dict):
            raise EstadoInvalidoError("A configuração deve ser um dicionário.")
        estados = configuracao.get("estados")

        if not isinstance(estados, dict) or not estados:
            raise EstadoInvalidoError(
                "A configuração deve possuir um dicionário "
                "não vazio no campo 'estados'."
            )

        for nome_estado, dados_estado in estados.items():
            self._validar_estado(nome_estado, dados_estado)

    def _validar_estado(
        self,
        nome_estado: str,
        dados_estado: Any,
    ) -> None:
        """Valida a estrutura de um estado.

        Args:
            nome_estado (str): _description_
            dados_estado (Any): _description_

        Raises:
            EstadoInvalidoError: _description_
            EstadoInvalidoError: _description_
            EstadoInvalidoError: _description_
            EstadoInvalidoError: _description_
        """
        if not isinstance(nome_estado, str) or not nome_estado.strip():
            raise EstadoInvalidoError(
                "O nome de cada estado deve ser uma string não vazia."
            )

        if not isinstance(dados_estado, dict):
            raise EstadoInvalidoError(
                f"O estado '{nome_estado}' deve ser um dicionário."
            )

        if "acoes" not in dados_estado:
            raise EstadoInvalidoError(
                f"O estado '{nome_estado}' deve possuir o campo 'acoes'."
            )
