"""Define o contexto associado à execução de um workflow.

Este módulo disponibiliza a entidade ContextoExecucao, responsável por
armazenar informações complementares de uma execução, como o autor,
o identificador e os dados adicionais fornecidos pela aplicação consumidora.

O contexto utiliza uma dataclass imutável e protege o mapeamento de dados
por meio de MappingProxyType. A proteção impede alterações diretas nas
chaves e nos valores do mapeamento, mas não garante a imutabilidade
profunda dos objetos armazenados nele.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any
from uuid import uuid4

from sme_workflow_sdk.dominio.validacao import (
    validar_mapping,
    validar_string_nao_vazia,
)
from sme_workflow_sdk.excecoes.base import ValidacaoDominioError


@dataclass(frozen=True, slots=True)
class ContextoExecucao:
    """Representa o contexto associado a uma execução do workflow.

    Armazena a identificação do autor, um identificador único da execução
    e dados adicionais fornecidos pela aplicação consumidora.

    Quando não informado, o identificador é gerado automaticamente
    utilizando UUID4. A aplicação consumidora também pode fornecer
    seu próprio identificador, desde que seja uma string não vazia.

    A instância é imutável após sua criação. O atributo ``dados`` é
    copiado e convertido em MappingProxyType, impedindo alterações
    diretas no mapeamento armazenado.

    A cópia dos dados é superficial: objetos mutáveis armazenados como
    valores não são copiados recursivamente e podem continuar sendo
    modificados por referências externas.

    Attributes:
        autor: Identificação do autor responsável pela execução. Deve ser uma
            string não vazia.
        identificador: Identificador único da execução. Caso não seja
            informado, um UUID é gerado automaticamente.
        dados: Mapeamento com informações adicionais da execução.
            Por padrão, é inicializado com um dicionário vazio.
    """

    autor: str
    identificador: str = field(default_factory=lambda: str(uuid4()))
    dados: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Valida os atributos e protege o mapeamento de dados.

        Valida se ``autor`` e ``identificador`` são strings não vazias
        e se ``dados`` implementa a interface ``Mapping``.

        Após as validações, cria uma cópia superficial do mapeamento
        informado e o converte em MappingProxyType, impedindo alterações
        diretas nas chaves e nos valores do mapeamento armazenado.

        Raises:
            ValidacaoDominioError: Se algum atributo não atender às regras
                de validação ou se os dados não puderem ser convertidos
                em um dicionário.
        """
        validar_string_nao_vazia(self.autor, "ContextoExecucao.autor")
        validar_string_nao_vazia(
            self.identificador, "ContextoExecucao.identificador"
        )
        validar_mapping(self.dados, "ContextoExecucao.dados")

        try:
            dados_copiados = dict(self.dados)
        except (TypeError, ValueError) as exc:
            raise ValidacaoDominioError(
                f"ContextoExecucao.dados não pôde ser convertido: {exc}"
            ) from exc

        object.__setattr__(self, "dados", MappingProxyType(dados_copiados))
