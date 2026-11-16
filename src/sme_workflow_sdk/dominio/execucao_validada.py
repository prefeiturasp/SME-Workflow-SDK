"""Define a entidade que representa uma execução validada do workflow.

Este módulo disponibiliza a classe ExecucaoValidada, responsável por
armazenar os dados de uma transição após a validação do estado atual,
da ação solicitada e das regras de consistência do workflow.

A entidade contém o estado de origem, a ação correspondente e o horário
de início da transição, sendo utilizada pelo motor durante a execução
do workflow.
"""

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
    """Representa uma transição de workflow previamente validada.

    Armazena os dados necessários para identificar uma transição
    autorizada pela configuração do workflow, incluindo o estado atual,
    a ação correspondente e o horário de início.

    A instância é imutável após sua criação. Quando o horário de início
    não é informado, ele é gerado automaticamente utilizando UTC.

    Attributes:
        estado_atual: Nome do estado em que a transição será executada.
            Deve ser um identificador válido.
        acao: Instância de :class:`Acao
            <sme_workflow_sdk.dominio.entidades.Acao>` contendo as informações
            da ação validada e seu próximo estado.
        inicio_transicao: Data e hora de início da transição, com fuso
            horário definido. Por padrão, utiliza o horário atual em UTC.
    """

    estado_atual: str
    acao: Acao
    inicio_transicao: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    def __post_init__(self) -> None:
        """Valida os atributos da execução.

        Verifica se o estado atual é uma string não vazia e corresponde
        ao padrão de identificadores aceito pelo domínio.

        Também verifica se a ação é uma instância de :class:`Acao
        <sme_workflow_sdk.dominio.entidades.Acao>` e se o horário de início é
        um objeto datetime com fuso horário definido.

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
