"""Resultado estruturado de uma execução do workflow.

Este módulo define a entidade responsável por representar o resultado de uma
execução de workflow, registrando a transição realizada, o status da execução,
os horários de início e término, o autor responsável e o contexto associado.
"""

from dataclasses import dataclass
from datetime import datetime

from sme_workflow_sdk.dominio import ContextoExecucao
from sme_workflow_sdk.dominio.validacao import (
    validar_booleano,
    validar_string_nao_vazia,
    validar_tipo,
)
from sme_workflow_sdk.excecoes import ValidacaoDominioError


@dataclass(frozen=True, slots=True)
class ResultadoWorkflow:
    """Representa o resultado da execução de uma ação do workflow.

    A entidade reúne as informações necessárias para identificar uma execução,
    descrever a transição de estado realizada e registrar seu resultado.

    A classe é imutável após sua inicialização. As validações garantem que
    os atributos obrigatórios tenham os tipos e valores esperados, que os
    horários sejam compatíveis e que transições não terminais não retornem
    ao mesmo estado.

    Attributes:
        identificador: Identificador único da execução do workflow.
        estado_anterior: Nome do estado em que a ação foi executada.
        acao: Nome da ação executada.
        proximo_estado: Nome do estado resultante da execução da ação.
        terminal: Indica se a transição corresponde ao encerramento
            do workflow.
        sucesso: Indica se a execução da ação foi concluída com sucesso.
        mensagem: Mensagem complementar de sucesso ou falha da execução.
        inicio: Data e hora em que a execução foi iniciada.
        fim: Data e hora em que a execução foi finalizada.
        autor: Identificação do autor responsável pela execução.
        contexto: Contexto associado à execução, representado por
            uma instância de ``ContextoExecucao``.
    """

    identificador: str
    estado_anterior: str
    acao: str
    proximo_estado: str
    terminal: bool
    sucesso: bool
    mensagem: str
    inicio: datetime
    fim: datetime
    autor: str
    contexto: ContextoExecucao

    def __post_init__(self) -> None:
        """Valida os atributos e a consistência do resultado.

        Verifica se os campos textuais são strings não vazias, se os campos
        booleanos são do tipo ``bool`` e se os horários e o contexto possuem
        os tipos esperados.

        Também verifica se o horário de término não é anterior ao horário
        de início e se uma transição não terminal aponta para um estado
        diferente do estado anterior.


        Raises:
            ValidacaoDominioError: Se algum atributo for inválido, se o
                horário de término for anterior ao início, se os horários
                possuírem fusos incompatíveis ou se uma transição não
                terminal apontar para o próprio estado de origem.
        """
        validar_string_nao_vazia(
            self.identificador, "ResultadoWorkflow.identificador"
        )
        validar_string_nao_vazia(
            self.estado_anterior, "ResultadoWorkflow.estado_anterior"
        )
        validar_string_nao_vazia(self.acao, "ResultadoWorkflow.acao")
        validar_string_nao_vazia(
            self.proximo_estado, "ResultadoWorkflow.proximo_estado"
        )
        validar_string_nao_vazia(self.autor, "ResultadoWorkflow.autor")
        validar_booleano(self.terminal, "ResultadoWorkflow.terminal")
        validar_booleano(self.sucesso, "ResultadoWorkflow.sucesso")
        validar_tipo(self.inicio, datetime, "ResultadoWorkflow.inicio")
        validar_tipo(self.fim, datetime, "ResultadoWorkflow.fim")
        validar_tipo(
            self.contexto, ContextoExecucao, "ResultadoWorkflow.contexto"
        )
        validar_string_nao_vazia(
            self.mensagem,
            "ResultadoWorkflow.mensagem",
        )

        try:
            if self.fim < self.inicio:
                raise ValidacaoDominioError(
                    "ResultadoWorkflow.fim não pode ser anterior a inicio"
                )
        except TypeError as exc:
            raise ValidacaoDominioError(
                "ResultadoWorkflow.inicio e fim devem ter fusos horários "
                "compatíveis"
            ) from exc

        if (
            self.sucesso
            and not self.terminal
            and self.proximo_estado == self.estado_anterior
        ):
            raise ValidacaoDominioError(
                f"Ação {self.acao} em {self.estado_anterior} aponta para "
                f"{self.proximo_estado}. Uma execução bem-sucedida e não "
                "terminal deve indicar um estado de destino diferente do "
                "estado anterior."
            )
