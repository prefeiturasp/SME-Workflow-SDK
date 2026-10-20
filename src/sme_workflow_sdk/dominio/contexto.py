"""Contexto genérico de execução do workflow."""

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
    """Armazena informações da execução do workflow.

    O contexto identifica o autor da execução, gera um identificador único
    por padrão e permite armazenar dados adicionais relacionados ao processo.

    A classe é imutável após sua inicialização. O atributo ``dados`` é
    copiado e convertido em ``MappingProxyType``, impedindo alterações
    diretas no mapeamento por meio da instância.

    Attributes:
        autor: Identificação do autor responsável pela execução.
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

        Em seguida, cria uma cópia do mapeamento e a converte em
        ``MappingProxyType``, impedindo alterações diretas em suas chaves
        e valores por meio do mapeamento armazenado na instância.

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
