"""Leitura e parsing de arquivos YAML de configuração de workflow.

Este módulo expõe :class:`LeitorWorkflow`, responsável por:

1. Validar que o caminho informado tem extensão suportada
   (``.yaml`` ou ``.yml``) e aponta para um arquivo real.
2. Ler o conteúdo tratando erros de *encoding* e de sintaxe YAML.
3. Garantir que existe exatamente um documento YAML e que sua
   raiz é um mapeamento (``dict``).

O leitor **não** conhece o esquema semântico do workflow — apenas
garante que a estrutura de alto nível é coerente.
"""

from pathlib import Path
from typing import Any, cast

import yaml

from sme_workflow_sdk.excecoes import (
    ArquivoNaoEncontradoError,
    ConfiguracaoInvalidaError,
    FormatoInvalidoError,
)


class LeitorWorkflow:
    """Carrega e valida a estrutura de alto nível de um workflow YAML.

    A classe concentra toda a lógica de I/O e de checagem estrutural,
    delegando a validação semântica (chaves obrigatórias, tipos de
    ação, etc.) para etapas posteriores do SDK.

    Examples:
        leitor = LeitorWorkflow()
        configuracao = leitor.carregar("workflows/pedido.yaml")
        print(configuracao["estados"])

    Attributes:
        EXTENSOES_VALIDAS (list[str]): Extensões aceitas pelo leitor.
            Atualmente ``[".yaml", ".yml"]``.

    """

    EXTENSOES_VALIDAS = [".yaml", ".yml"]

    def carregar(self, caminho: str) -> dict[str, Any]:
        """Carrega e valida a configuração de um arquivo YAML.

        Executa, em ordem, as três etapas internas de validação:
        :meth:`_validar_caminho`, :meth:`_ler_yaml` e
        :meth:`_validar_conteudo`.

        Args:
            caminho (str): Caminho para o arquivo ``.yaml`` ou ``.yml``.

        Returns:
            dict[str, Any]: Dicionário Python correspondente ao único
                documento YAML presente no arquivo.

        Raises:
            FormatoInvalidoError: Se a extensão do arquivo não estiver
                em :attr:`EXTENSOES_VALIDAS`, se o YAML tiver sintaxe
                inválida, se o *encoding* não for UTF-8, ou se houver
                mais de um documento no arquivo.
            ArquivoNaoEncontradoError: Se o caminho não existir ou não
                apontar para um arquivo regular (ex.: diretório).
            ConfiguracaoInvalidaError: Se o arquivo estiver vazio, só
                contiver comentários, ou se a raiz do YAML não for um
                mapeamento.

        Examples:
            >>> leitor = LeitorWorkflow()
            >>> config = leitor.carregar("workflow.yaml")
            >>> "estados" in config
            True
        """
        caminho_arquivo = self._validar_caminho(caminho)
        configuracao = self._ler_yaml(caminho_arquivo)
        self._validar_conteudo(configuracao, caminho_arquivo)
        return cast(dict[str, Any], configuracao)

    def _validar_caminho(self, caminho: str | Path) -> Path:
        """Valida extensão, existência e tipo do caminho informado.

        Args:
            caminho (str | Path): Caminho a ser validado.

        Raises:
            FormatoInvalidoError: Se a extensão do arquivo não estiver
                entre as suportadas.
            ArquivoNaoEncontradoError:
                - Se o caminho não existir no sistema de arquivos.
                - Se o caminho existir, mas não for um arquivo regular (por
                    exemplo, um diretório).

        Returns:
            Path: Objeto :class:`pathlib.Path` correspondente ao
            caminho validado.
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

    def _ler_yaml(self, caminho_arquivo: Path) -> Any:
        """Lê o arquivo YAML e valida o número de documentos.

        Arquivos vazios ou que só contêm comentários são sinalizados
        retornando ``None``; cabe a :meth:`_validar_conteudo` decidir
        se isso é um erro de negócio.

        Args:
            caminho_arquivo (Path): Caminho já validado do arquivo.

        Raises:
            FormatoInvalidoError:
                - Se o arquivo não estiver em UTF-8.
                - Se o YAML tiver sintaxe inválida.
                - Se houver mais de um documento YAML no mesmo arquivo.

        Returns:
            Any: Conteúdo carregado do YAML, ainda sujeito à validação
            estrutural e semântica.

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
        """Valida se o conteúdo carregado é um mapeamento não vazio.

        Args:
            configuracao (Any): Objeto retornado por :meth:`_ler_yaml`. Pode
                ser ``None`` (arquivo vazio), um ``dict`` (caso esperado) ou
                qualquer outro tipo (ex.: ``list``, ``str``).
            caminho_arquivo (Path): Caminho do arquivo, usado apenas para
                compor mensagens de erro.

        Raises:
            ConfiguracaoInvalidaError: Se ``configuracao`` for ``None``,
                indicando arquivo vazio ou só com comentários.
            ConfiguracaoInvalidaError: Se ``configuracao`` não for um
                ``dict``, indicando que a raiz do YAML não é um
                mapeamento.
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
