"""Leitura da configuração de workflow."""

from pathlib import Path
from typing import Any

import yaml


class LeitorWorkflow:
    """Responsável por carregar a configuração do workflow."""

    def carregar(self, caminho: str) -> dict[str, Any]:
        """Carrega a configuração de um arquivo YAML.

        Args:
            caminho (str): Caminho do arquivo de configuração.

        Returns:
            dict[str, Any]: Configuração do workflow.
        """
        with Path(caminho).open(encoding="utf-8") as arquivo:
            configuracao: dict[str, Any] = yaml.safe_load(arquivo)

        return configuracao
