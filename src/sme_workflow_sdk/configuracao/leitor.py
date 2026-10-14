"""Leitura da configuração de workflow."""

from pathlib import Path
from typing import Any, cast

import yaml

from sme_workflow_sdk.excecoes import (
    ArquivoNaoEncontradoError,
    ConfiguracaoInvalidaError,
    FormatoInvalidoError,
)


class LeitorWorkflow:
    """Responsável por carregar a configuração do workflow."""

    EXTENSOES_VALIDAS = [".yaml", ".yml"]

    def carregar(self, caminho: str) -> dict[str, Any]:
        """Carrega a configuração de um arquivo YAML.

        Args:
            caminho (str): Caminho do arquivo de configuração.

        Returns:
            dict[str, Any]: Configuração do workflow.
        """
        caminho_arquivo = self._validar_caminho(caminho)
        configuracao = self._ler_yaml(caminho_arquivo)
        self._validar_conteudo(configuracao, caminho_arquivo)
        return cast(dict[str, Any], configuracao)

    def _validar_caminho(self, caminho: str | Path) -> Path:
        """Valida extensão e existência do arquivo.

        Args:
            caminho (str | Path): _description_

        Raises:
            FormatoInvalidoError: _description_
            ArquivoNaoEncontradoError: _description_
            ArquivoNaoEncontradoError: _description_

        Returns:
            Path: _description_
        """
        caminho_arquivo = Path(caminho)

        if caminho_arquivo.suffix.lower() not in self.EXTENSOES_VALIDAS:
            mensagem = caminho_arquivo.suffix or "sem extensão"
            raise FormatoInvalidoError(
                f"Somente arquivos '{", ".join(self.EXTENSOES_VALIDAS)}' são "
                f"aceitos. Recebido: '{mensagem}'."
            )
        if not caminho_arquivo.exists():
            raise ArquivoNaoEncontradoError(
                f"Arquivo não encontrado: '{caminho}'."
            )

        if not caminho_arquivo.is_file():
            raise ArquivoNaoEncontradoError(
                f"'{caminho}' não é um arquivo válido."
            )

        return caminho_arquivo

    def _ler_yaml(self, caminho_arquivo: Path) -> dict[str, Any] | None:
        """Lê o arquivo e trata erros de encoding e YAML.

        Args:
            caminho_arquivo (Path): _description_

        Raises:
            FormatoInvalidoError: _description_
            FormatoInvalidoError: _description_
            FormatoInvalidoError: _description_

        Returns:
            dict[str, Any]: _description_
        """
        try:
            with caminho_arquivo.open(encoding="utf-8") as arquivo:
                configuracao: list[dict[str, Any]] = list(
                    yaml.safe_load_all(arquivo)
                )
        except UnicodeDecodeError as erro:
            raise FormatoInvalidoError(
                f"Arquivo '{caminho_arquivo}' não está em UTF-8: {erro}"
            ) from erro
        except yaml.YAMLError as erro:
            raise FormatoInvalidoError(
                f"YAML inválido em '{caminho_arquivo}': {erro}"
            ) from erro

        if not configuracao:
            return None

        if len(configuracao) != 1:
            raise FormatoInvalidoError(
                f"Esperado exatamente 1 documento YAML em '{caminho_arquivo}',"
                f" encontrados: {len(configuracao)}."
            )

        return configuracao[0]

    def _validar_conteudo(
        self, configuracao: Any, caminho_arquivo: Path
    ) -> None:
        """Valida vazio e tipo da raiz.

        Args:
            configuracao (Any): _description_
            caminho_arquivo (Path): _description_

        Raises:
            ConfiguracaoInvalidaError: _description_
            ConfiguracaoInvalidaError: _description_
        """
        if configuracao is None:
            raise ConfiguracaoInvalidaError(
                f"O arquivo '{caminho_arquivo}' está vazio ou só contém "
                "comentários."
            )

        if not isinstance(configuracao, dict):
            raise ConfiguracaoInvalidaError(
                f"Esperado um formato YAML na raiz de '{caminho_arquivo}', "
                f"recebido: '{type(configuracao).__name__}'."
            )
