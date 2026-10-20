"""Entidades de domínio do workflow.

Este módulo define as entidades que representam ações, estados e transições
de um workflow, garantindo a validação dos atributos e a imutabilidade
dos objetos após sua inicialização.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from sme_workflow_sdk.dominio.validacao import (
    validar_booleano,
    validar_mapping,
    validar_string_nao_vazia,
    validar_tipo,
)


@dataclass(frozen=True, slots=True)
class Acao:
    """Representa uma ação configurada para um estado do workflow.

    Uma ação define o nome da operação disponível, o estado de destino
    após sua execução e indica se esse estado representa o encerramento
    do workflow.

    Attributes:
        nome: Nome da ação disponibilizada no estado atual.
        proximo_estado: Nome do estado para o qual a execução deve avançar.
        terminal: Indica se a transição corresponde a um estado terminal.
    """

    nome: str
    proximo_estado: str
    terminal: bool

    def __post_init__(self) -> None:
        """Valida os atributos da ação após sua inicialização.

        Verifica se ``nome`` e ``proximo_estado`` são strings não vazias
        e se ``terminal`` é estritamente do tipo booleano.

        Raises:
            ValidacaoDominioError: Se algum atributo não atender às regras
                de validação definidas para a ação.
        """
        validar_string_nao_vazia(self.nome, "Acao.nome")
        validar_string_nao_vazia(self.proximo_estado, "Acao.proximo_estado")
        validar_booleano(self.terminal, "Acao.terminal")


@dataclass(frozen=True, slots=True)
class Estado:
    """Representa um estado do workflow.

    Um estado identifica uma etapa do processo e define as ações disponíveis
    para avançar a execução. Quando ``acoes`` é ``None``, o estado não
    possui ações configuradas, podendo representar um estado terminal.

    O mapeamento de ações é copiado e convertido em ``MappingProxyType``
    para impedir alterações diretas após a criação da entidade.

    Attributes:
        nome: Nome que identifica o estado do workflow.
        acoes: Mapeamento entre os nomes das ações e suas respectivas
            entidades ``Acao``. Pode ser ``None`` quando não houver ações.
    """

    nome: str
    acoes: Mapping[str, Acao] | None

    def __post_init__(self) -> None:
        """Valida os atributos do estado e protege suas ações.

        Verifica se ``nome`` é uma string não vazia e se ``acoes`` é um
        objeto que implementa ``Mapping`` ou é ``None``.

        Quando o mapeamento está presente, valida os nomes das ações e
        verifica se cada valor é uma instância de ``Acao``. Em seguida,
        copia o mapeamento e o torna somente leitura.

        Raises:
            ValidacaoDominioError: Se o nome do estado, o mapeamento,
                algum nome de ação ou alguma entidade de ação for inválido.
        """
        validar_string_nao_vazia(self.nome, "Estado.nome")
        validar_mapping(self.acoes, "Estado.acoes", permitir_none=True)

        if self.acoes is not None:
            acoes = dict(self.acoes)
            for nome_acao, acao in acoes.items():
                validar_string_nao_vazia(
                    nome_acao, "Estado.acoes: nome da ação"
                )
                validar_tipo(acao, Acao, f"Estado.acoes[{nome_acao}]")
            object.__setattr__(self, "acoes", MappingProxyType(acoes))


@dataclass(frozen=True, slots=True)
class Transicao:
    """Representa a transição entre dois estados do workflow.

    Registra o estado de origem, a ação executada, o estado de destino
    e a indicação de que a transição leva ao encerramento do workflow.

    Attributes:
        estado_anterior: Nome do estado em que a ação está disponível.
        acao: Nome da ação responsável pela transição.
        proximo_estado: Nome do estado de destino.
        terminal: Indica se a transição leva ao encerramento do workflow.
    """

    estado_anterior: str
    acao: str
    proximo_estado: str
    terminal: bool

    def __post_init__(self) -> None:
        """Valida os campos obrigatórios da transição.

        Verifica se ``estado_anterior``, ``acao`` e ``proximo_estado``
        são strings não vazias e se ``terminal`` é estritamente booleano.

        Raises:
            ValidacaoDominioError: Se algum atributo não atender às regras
                de validação definidas para a transição.
        """
        validar_string_nao_vazia(
            self.estado_anterior, "Transicao.estado_anterior"
        )
        validar_string_nao_vazia(self.acao, "Transicao.acao")
        validar_string_nao_vazia(
            self.proximo_estado, "Transicao.proximo_estado"
        )
        validar_booleano(self.terminal, "Transicao.terminal")
