"""Define as entidades de domínio do workflow.

Este módulo disponibiliza as entidades :class:`Acao`, :class:`Estado` e
:class:`Transicao`, responsáveis por representar as regras e os elementos que
compõem um workflow.

As entidades validam seus atributos durante a inicialização, garantindo a
consistência dos dados e a utilização de identificadores válidos para estados
e ações.

As classes utilizam dataclasses imutáveis. Quando aplicável, os mapeamentos
são protegidos por :py:class:`types.MappingProxyType` para impedir alterações
diretas após a criação das entidades.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from sme_workflow_sdk.dominio.validacao import (
    validar_booleano,
    validar_identificador,
    validar_mapping,
    validar_string_nao_vazia,
    validar_tipo,
)


@dataclass(frozen=True, slots=True)
class Acao:
    """Representa uma ação configurada para um estado do workflow.

    Uma ação define uma operação disponível em determinado estado,
    especificando seu nome, o estado de destino após sua execução
    e se a transição representa o encerramento do workflow.

    Os nomes da ação e do estado de destino devem seguir o padrão
    de identificadores do domínio, contendo letras
    `ASCII <https://www.asciitable.com/>`_ e palavras separadas por
    sublinhados.

    A entidade é imutável após sua criação.

    Attributes:
        nome: Nome da ação disponibilizada no estado atual.
        proximo_estado: Nome do estado para o qual a execução deve avançar.
        terminal: Indica se a transição representa o encerramento
            do workflow.
    """

    nome: str
    proximo_estado: str
    terminal: bool

    def __post_init__(self) -> None:
        """Valida os atributos da ação após sua inicialização.

        Verifica se ``nome`` e ``proximo_estado`` são strings não vazias
        e se seguem o padrão de identificadores definido pelo domínio.

        Também verifica se ``terminal`` é estritamente do tipo booleano,
        não aceitando valores inteiros como 0 e 1.

        Raises:
            ValidacaoDominioError: Se algum atributo não atender às regras
                de validação definidas para a ação.
        """
        validar_string_nao_vazia(self.nome, "Acao.nome")
        validar_identificador(self.nome, "Acao.nome")
        validar_string_nao_vazia(self.proximo_estado, "Acao.proximo_estado")
        validar_identificador(self.proximo_estado, "Acao.proximo_estado")
        validar_booleano(self.terminal, "Acao.terminal")


@dataclass(frozen=True, slots=True)
class Estado:
    """Representa um estado do workflow.

    Um estado identifica uma etapa do processo e define as ações
    disponíveis para avançar a execução.

    O atributo ``acoes`` pode receber um mapeamento entre os nomes
    das ações e suas respectivas entidades Acao, ou ``None`` quando
    não houver ações associadas ao estado.

    O mapeamento informado é copiado e convertido em
    :py:class:`types.MappingProxyType`, impedindo alterações diretas nas
    chaves e nos valores armazenados. Essa proteção é superficial e não
    garante a imutabilidade profunda dos objetos internos.

    A entidade é imutável após sua criação.

    Attributes:
        nome: Identificador do estado do workflow.
        acoes: Mapeamento entre os nomes das ações e suas respectivas
            entidades Acao. Pode ser None quando não houver ações.
    """

    nome: str
    acoes: Mapping[str, Acao] | None

    def __post_init__(self) -> None:
        """Valida os atributos do estado e protege suas ações.

        Verifica se ``nome`` é uma string não vazia e segue o padrão
        de identificadores definido pelo domínio.

        Verifica se ``acoes`` implementa :py:class:`collections.abc.Mapping`
        ou é None.

        Quando o mapeamento está presente, valida os nomes das ações,
        verifica se cada valor é uma instância de Acao e cria uma cópia
        protegida por :py:class:`types.MappingProxyType`.

        Raises:
            ValidacaoDominioError: Se o nome do estado, o mapeamento,
                algum nome de ação ou alguma entidade de ação for inválido.
        """
        validar_string_nao_vazia(self.nome, "Estado.nome")
        validar_identificador(self.nome, "Estado.nome")
        validar_mapping(self.acoes, "Estado.acoes", permitir_none=True)

        if self.acoes is not None:
            acoes = dict(self.acoes)
            for nome_acao, acao in acoes.items():
                validar_string_nao_vazia(
                    nome_acao, "Estado.acoes: nome da ação"
                )
                validar_identificador(nome_acao, f"Estado.acoes[{nome_acao}]")
                validar_tipo(acao, Acao, f"Estado.acoes[{nome_acao}]")
            object.__setattr__(self, "acoes", MappingProxyType(acoes))


@dataclass(frozen=True, slots=True)
class Transicao:
    """Representa uma transição entre dois estados do workflow.

    Registra a relação entre o estado de origem, a ação executada
    e o estado de destino, indicando também se a transição encerra
    o workflow.

    Os nomes dos estados e da ação devem seguir o padrão de
    identificadores definido pelo domínio.

    A entidade é imutável após sua criação.

    Attributes:
        estado_anterior: Identificador do estado em que a ação
            está disponível.
        acao: Identificador da ação responsável pela transição.
        proximo_estado: Identificador do estado de destino.
        terminal: Indica se a transição leva ao encerramento
            do workflow.
    """

    estado_anterior: str
    acao: str
    proximo_estado: str
    terminal: bool

    def __post_init__(self) -> None:
        """Valida os atributos da transição.

        Verifica se ``estado_anterior``, ``acao`` e ``proximo_estado``
        são strings não vazias e seguem o padrão de identificadores
        definido pelo domínio.

        Também verifica se ``terminal`` é estritamente do tipo booleano.

        Raises:
            ValidacaoDominioError: Se algum atributo não atender às regras
                de validação definidas para a transição.
        """
        validar_string_nao_vazia(
            self.estado_anterior, "Transicao.estado_anterior"
        )
        validar_identificador(
            self.estado_anterior, "Transicao.estado_anterior"
        )

        validar_string_nao_vazia(self.acao, "Transicao.acao")
        validar_identificador(self.acao, "Transicao.acao")

        validar_string_nao_vazia(
            self.proximo_estado, "Transicao.proximo_estado"
        )
        validar_identificador(self.proximo_estado, "Transicao.proximo_estado")
        validar_booleano(self.terminal, "Transicao.terminal")
