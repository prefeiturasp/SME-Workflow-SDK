"""Resultado estruturado de uma execução do workflow.

Este módulo define a entidade responsável por representar o resultado de uma
execução de workflow, registrando a transição realizada, o status da execução,
os horários de início e término, o autor responsável e o contexto associado.
"""

from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Any

from sme_workflow_sdk.dominio.contexto import ContextoExecucao
from sme_workflow_sdk.dominio.validacao import (
    validar_booleano,
    validar_identificador,
    validar_string_nao_vazia,
    validar_tipo,
)
from sme_workflow_sdk.excecoes import ValidacaoDominioError


@dataclass(frozen=True, slots=True)
class ResultadoWorkflow:
    """Representa o resultado de uma execução do workflow.

    Reúne as informações necessárias para identificar uma execução,
    descrever a transição solicitada e registrar seu resultado.

    A entidade é imutável após sua inicialização. Suas validações
    verificam os tipos e valores dos atributos, a compatibilidade
    dos horários e a consistência da transição.

    Uma execução bem-sucedida e não terminal deve indicar um estado
    de destino diferente do estado anterior. Execuções malsucedidas
    podem manter o estado anterior como próximo estado.

    Attributes:
        identificador: Identificador único da execução.
        estado_anterior: Nome do estado em que a ação foi executada.
        acao: Nome da ação executada.
        proximo_estado: Nome do estado resultante da execução.
        terminal: Indica se a transição encerra o workflow.
        sucesso: Indica se a execução foi concluída com sucesso.
        mensagem: Mensagem complementar sobre o resultado.
        inicio: Data e hora de início da execução.
        fim: Data e hora de término da execução.
        autor: Identificação do autor responsável pela execução.
        contexto: Contexto associado à execução, representado por
            uma instância de ContextoExecucao.
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

        Verifica os tipos e valores dos atributos obrigatórios,
        a validade dos identificadores e a consistência dos horários.

        Também verifica se o horário de término não é anterior ao
        horário de início e se uma execução bem-sucedida e não terminal
        aponta para um estado diferente do estado anterior.


        Raises:
            ValidacaoDominioError: Se algum atributo for inválido,
            se os horários forem incompatíveis ou se a transição
            não respeitar as regras de consistência do resultado.
        """
        validar_string_nao_vazia(
            self.identificador, "ResultadoWorkflow.identificador"
        )
        validar_string_nao_vazia(
            self.estado_anterior, "ResultadoWorkflow.estado_anterior"
        )
        validar_identificador(
            self.estado_anterior, "ResultadoWorkflow.estado_anterior"
        )
        validar_string_nao_vazia(self.acao, "ResultadoWorkflow.acao")
        validar_identificador(self.acao, "ResultadoWorkflow.acao")
        validar_string_nao_vazia(
            self.proximo_estado, "ResultadoWorkflow.proximo_estado"
        )
        validar_identificador(
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

    def _converter_para_dict(self, valor: Any) -> Any:
        """Converte recursivamente estruturas de dados em valores simples.

        Converte dataclasses em dicionários, mapeamentos em dicionários
        comuns, listas e tuplas em listas e enums em seus respectivos
        valores.

        A conversão é recursiva, permitindo tratar estruturas aninhadas.
        Tipos não contemplados pelas conversões são preservados,
        incluindo objetos datetime.

        Args:
            valor (Any): Valor a ser convertido.

        Returns:
            Any: Valor convertido conforme seu tipo, preservando os objetos
                que não possuem uma regra específica de conversão.
        """
        if is_dataclass(valor) and not isinstance(valor, type):
            return {
                campo.name: self._converter_para_dict(
                    getattr(valor, campo.name)
                )
                for campo in fields(valor)
            }

        if isinstance(valor, (dict | MappingProxyType)):
            return {
                chave: self._converter_para_dict(item)
                for chave, item in valor.items()
            }

        if isinstance(valor, (list | tuple)):
            return [self._converter_para_dict(item) for item in valor]

        if isinstance(valor, Enum):
            return self._converter_para_dict(valor.value)

        return valor

    def para_dict(self) -> dict[str, Any]:
        """Converte o resultado do workflow em um dicionário.

        Percorre recursivamente os atributos do resultado, convertendo
        dataclasses, mapeamentos, listas, tuplas e enums para estruturas
        equivalentes em tipos básicos.

        Os objetos datetime são preservados, não sendo convertidos
        automaticamente para strings.

        Returns:
            dict[str, Any]: Dicionário contendo os atributos do resultado,
                incluindo os objetos datetime originais e o contexto convertido
                recursivamente.
        """
        dicionario: dict[str, Any] = self._converter_para_dict(self)
        return dicionario
