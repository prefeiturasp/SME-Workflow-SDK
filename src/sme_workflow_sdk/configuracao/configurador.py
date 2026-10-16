"""Coordenação da leitura e validação da configuração do workflow.

Este módulo expõe :class:`ConfiguradorWorkflow`, o ponto de entrada de alto
nível do pacote de configuração. Ele encapsula a construção de
:class:`~sme_workflow_sdk.configuracao.leitor.LeitorWorkflow` e de
:class:`~sme_workflow_sdk.configuracao.validador.ValidadorWorkflow`, delegando
a eles a leitura do arquivo e a validação da estrutura.
"""

from typing import Any

from sme_workflow_sdk.configuracao.leitor import LeitorWorkflow
from sme_workflow_sdk.configuracao.validador import ValidadorWorkflow


class ConfiguradorWorkflow:
    """Coordena o carregamento e a validação de workflows.

    Reúne leitura e validação em uma única porta de entrada. Manter
    os dois componentes internos permite substituí-los em testes
    (via *monkeypatch*) sem alterar a API pública, e deixa espaço
    para que o configurador acumule etapas adicionais (resolução de
    *includes*, por exemplo) mantendo o mesmo contrato.

    Exemplo:
        >>> from sme_workflow_sdk import ConfiguradorWorkflow
        >>> configurador = ConfiguradorWorkflow()
        >>> config = configurador.carregar("workflow.yaml")
        >>> configurador.validar(config)

    """

    def __init__(self) -> None:
        """Inicializa os componentes de leitura e validação.

        Cria uma instância de
        :class:`~sme_workflow_sdk.configuracao.leitor.LeitorWorkflow` e uma de
        :class:`~sme_workflow_sdk.configuracao.validador.ValidadorWorkflow`,
        ambas reutilizadas em todas as chamadas a :meth:`carregar`.

        """
        self._leitor = LeitorWorkflow()
        self._validador = ValidadorWorkflow()

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

    def validar(self, configuracao: dict[str, Any]) -> None:
        """Valida a estrutura de uma configuração de workflow.

        Delega ao :class:`ValidadorWorkflow` interno, propagando
        qualquer exceção lançada por ele.

        Args:
            configuracao (dict[str, Any]): Configuração a ser validada.
                Normalmente é o retorno de :meth:`carregar`.

        Raises:
            EstadoInvalidoError:
                - Se a configuração não for um dicionário.
                - Se o campo ``estados`` estiver ausente, não for um
                  dicionário ou estiver vazio.
                - Se algum estado tiver nome ou dados inválidos.
                - Se alguma ação referenciar um estado inexistente.
            AcaoInvalidaError:
                - Se algum estado não possuir o campo ``acoes``.
                - Se ``acoes`` não for dicionário nem ``None``.
                - Se alguma ação estiver mal formada.
                - Se houver incoerência entre o campo ``terminal``
                  de uma ação e as ações do estado de destino.

        Examples:
            >>> configurador = ConfiguradorWorkflow()
            >>> config = configurador.carregar("workflow.yaml")
            >>> configurador.validar(config)  # levanta erro se inválido
        """
        self._validador.validar(configuracao)
