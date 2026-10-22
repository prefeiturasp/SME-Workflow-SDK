"""Contrato de uma execução de workflow validada."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from sme_workflow_sdk.dominio.entidades import Acao
from sme_workflow_sdk.dominio.validacao import (
    validar_identificador,
    validar_string_nao_vazia,
)
from sme_workflow_sdk.excecoes import ValidacaoDominioError


@dataclass(frozen=True, slots=True)
class ExecucaoValidada:
    """Representa uma ação validada, aguardando execução.

    Armazena o estado de origem, a ação configurada e o instante em que a
    transição foi iniciada.
    """

    estado_atual: str
    acao: Acao
    inicio_transicao: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    def __post_init__(self) -> None:
        """Valida os atributos da execução.

        Verifica se o estado atual é uma string não vazia, se a ação é
        uma instância de Acao e se o horário de início é um datetime
        com fuso horário definido.

        Raises:
            ValidacaoDominioError: Se algum atributo não respeitar
                o contrato da execução validada.
        """
        validar_string_nao_vazia(
            self.estado_atual, "ExecucaoValidada.estado_atual"
        )
        validar_identificador(
            self.estado_atual, "ExecucaoValidada.estado_atual"
        )

        if not isinstance(self.acao, Acao):
            raise ValidacaoDominioError(
                "ExecucaoValidada.acao deve ser uma instância de Acao."
            )

        if not isinstance(self.inicio_transicao, datetime):
            raise ValidacaoDominioError(
                "ExecucaoValidada.inicio_transicao deve ser uma instância de "
                "datetime."
            )
        if (
            self.inicio_transicao.tzinfo is None
            or self.inicio_transicao.utcoffset() is None
        ):
            raise ValidacaoDominioError(
                "ExecucaoValidada.inicio_transicao deve possuir fuso horário "
                "definido."
            )
