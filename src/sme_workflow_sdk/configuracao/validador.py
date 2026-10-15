"""Validação da configuração de workflow."""

from typing import Any


class ValidadorWorkflow:
    """Responsável por validar a configuração do workflow."""

    def validar(self, configuracao: dict[str, Any]) -> None:
        """Valida a configuração do workflow.

        Args:
            configuracao (dict[str, Any]): Configuração carregada do arquivo
                YAML.

        Raises:
            ValueError: Se a configuração for inválida.
        """
        if "estados" not in configuracao:
            raise ValueError("A configuração deve possuir o campo 'estados'.")
