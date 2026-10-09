"""Coordenação da leitura e validação da configuração do workflow."""

from typing import Any

from sme_workflow_sdk.configuracao.leitor import LeitorWorkflow
from sme_workflow_sdk.configuracao.validador import ValidadorWorkflow


class ConfiguradorWorkflow:
    """Coordena o carregamento e a validação de workflows."""

    def __init__(self) -> None:
        """Inicializa os componentes de leitura e validação."""
        self._leitor = LeitorWorkflow()
        self._validador = ValidadorWorkflow()

    def carregar(self, caminho: str) -> dict[str, Any]:
        """Carrega a configuração de um arquivo YAML.

        Args:
            caminho (str): Caminho do arquivo de configuração.

        Returns:
            dict[str, Any]: Configuração carregada.
        """
        return self._leitor.carregar(caminho)

    def validar(self, configuracao: dict[str, Any]) -> None:
        """Valida a configuração do workflow.

        Args:
            configuracao (dict[str, Any]): Configuração a ser validada.
        """
        self._validador.validar(configuracao)
