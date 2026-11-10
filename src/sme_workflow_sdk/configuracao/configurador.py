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
    """Coordena a leitura e a validação da configuração do workflow.

    Centraliza o acesso aos componentes responsáveis por carregar
    arquivos YAML e validar a configuração resultante.

    A leitura verifica aspectos estruturais do arquivo, enquanto
    a validação verifica as regras de estrutura e consistência
    dos estados, ações e transições do workflow.

    Examples:
        >>> configurador = ConfiguradorWorkflow()
        >>> config = configurador.carregar("workflow.yaml")
        >>> configurador.validar(config)

    """

    def __init__(self) -> None:
        """Inicializa os componentes de leitura e validação.

        Cria uma instância de ``LeitorWorkflow`` e uma de
        ``ValidadorWorkflow``, armazenando ambas para reutilização durante as
        operações de carregamento e validação.
        """
        self._leitor = LeitorWorkflow()
        self._validador = ValidadorWorkflow()

    def carregar(self, caminho: str) -> dict[str, Any]:
        """Carrega a configuração de um arquivo YAML.

        Delega ao ``LeitorWorkflow`` a validação do caminho, a leitura
        do arquivo e a verificação estrutural do conteúdo YAML.

        A validação das regras específicas do workflow deve ser
        realizada separadamente por meio do método :meth:`validar`.

        Args:
            caminho (str): Caminho para o arquivo ``.yaml`` ou
                ``.yml`` a ser carregado.

        Returns:
            dict[str, Any]: Configuração carregada como dicionário,
            com a estrutura de alto nível validada.

        Raises:
            FormatoInvalidoError: Se a extensão não for suportada,
                se o YAML possuir sintaxe inválida, encoding diferente
                de UTF-8 ou mais de um documento.
            ArquivoNaoEncontradoError: Se o caminho não existir ou
                não apontar para um arquivo regular.
            ConfiguracaoInvalidaError: Se o arquivo estiver vazio, contiver
                apenas comentários ou se a raiz do YAML não for um mapeamento.

        Examples:
            >>> configurador = ConfiguradorWorkflow()
            >>> config = configurador.carregar("workflow.yaml")
            >>> "estados" in config
            True

        """
        return self._leitor.carregar(caminho)

    def validar(self, configuracao: dict[str, Any]) -> None:
        """Valida a estrutura e a consistência da configuração do workflow.

        Delega ao ``ValidadorWorkflow`` a verificação dos estados,
        das ações e das transições configuradas.

        Args:
            configuracao (dict[str, Any]): Configuração do workflow,
                normalmente obtida por meio de :meth:`carregar`.

        Raises:
            EstadoInvalidoError:

                - Se a configuração não for um dicionário.
                - Se o campo ``estados`` estiver ausente, não for um
                  dicionário ou estiver vazio.
                - Se algum estado tiver nome ou dados inválidos.
                - Se alguma ação referenciar um estado inexistente.

            AcaoInvalidaError:

                - Se algum estado não possuir o campo ``acoes``.
                - Se ``acoes`` não for um dicionário válido, nem ``None``,
                    ou se for um dicionário vazio.
                - Se alguma ação possuir nome ou estrutura inválida.
                - Se houver campos obrigatórios ausentes ou chaves extras.
                - Se os campos ``proximo_estado`` ou ``terminal``
                    possuírem valores inválidos.
                - Se o valor de ``terminal`` for incompatível com a existência
                    de ações no estado de destino.

        Examples:
            >>> configurador = ConfiguradorWorkflow()
            >>> config = configurador.carregar("workflow.yaml")
            >>> configurador.validar(config)  # levanta erro se inválido
        """
        self._validador.validar(configuracao)
