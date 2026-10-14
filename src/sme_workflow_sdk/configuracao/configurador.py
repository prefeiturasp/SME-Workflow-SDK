"""Coordenação da leitura e validação da configuração do workflow.

Este módulo expõe :class:`ConfiguradorWorkflow`, o ponto de entrada de alto
nível do pacote de configuração. Ele encapsula a construção de
:class:`~sme_workflow_sdk.configuracao.leitor.LeitorWorkflow` e delega a ele
toda a I/O.
"""

from typing import Any

from sme_workflow_sdk.configuracao.leitor import LeitorWorkflow


class ConfiguradorWorkflow:
    """Coordena o carregamento e a validação de workflows.

    A classe mantém um :class:`LeitorWorkflow` interno, o que permite
    substituir a implementação de leitura em testes (via*monkeypatch*) sem
    alterar a API pública. Futuramente, o  configurador pode acumular etapas
    adicionais de validação semântica e resolução de *includes*, mantendo o
    mesmo contrato.

    Exemplo:
        >>> from sme_workflow_sdk import ConfiguradorWorkflow
        >>> configurador = ConfiguradorWorkflow()
        >>> config = configurador.carregar("workflow.yaml")

    """

    def __init__(self) -> None:
        """Inicializa os componentes de leitura e validação.

        Cria uma instância de
        :class:`~sme_workflow_sdk.configuracao.leitor.LeitorWorkflow` que será
        reutilizada em todas as chamadas a :meth:`carregar`.

        """
        self._leitor = LeitorWorkflow()

    def carregar(self, caminho: str) -> dict[str, Any]:
        """Carrega a configuração de um arquivo YAML.

        Delega toda a validação de caminho, *parsing* e checagem
        estrutural ao :class:`LeitorWorkflow` interno, propagando
        qualquer exceção lançada por ele.

        Args:
            caminho (str): Caminho para o arquivo ``.yaml`` ou
                ``.yml`` a ser carregado.


        Returns:
            dict[str, Any]: Configuração do workflow já validada
            estruturalmente.

        Raises:
            FormatoInvalidoError: Em caso de extensão não suportada,
                YAML inválido, *encoding* incorreto ou múltiplos
                documentos no arquivo.
            ArquivoNaoEncontradoError: Se o caminho não existir ou
                não apontar para um arquivo regular.
            ConfiguracaoInvalidaError: Se o arquivo estiver vazio ou
                se a raiz do YAML não for um mapeamento.

        Examples:
            >>> configurador = ConfiguradorWorkflow()
            >>> config = configurador.carregar("workflow.yaml")
            >>> "estados" in config
            True

        """
        return self._leitor.carregar(caminho)
