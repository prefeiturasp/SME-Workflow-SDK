"""Resultado estruturado de uma execução do workflow.

Este módulo define a entidade responsável por representar o resultado de uma
execução de workflow, registrando a transição realizada, o status da execução,
os horários de início e término, o autor responsável e o contexto associado.
"""

from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime
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
        """Converte recursivamente um valor para uma estrutura em JSON.

        Converte dataclasses em dicionários, mapeamentos em dicionários comuns,
        listas e tuplas em listas e enums em seus respectivos valores. Valores
        que não exigem conversão são retornados sem alterações.

        Args:
            valor (Any): Valor a ser convertido, que pode ser uma dataclass,
                um mapeamento, uma coleção ou um tipo primitivo.

        Returns:
            Any:  Valor convertido para uma estrutura compatível com JSON.
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

        return valor

    def para_dict(self) -> dict[str, Any]:
        """Converte o resultado do workflow em um dicionário.

        Utiliza a conversão recursiva para transformar os campos do resultado,
        incluindo objetos aninhados e valores imutáveis, em uma estrutura
        compatível com a serialização JSON.

        Returns:
            dict[str, Any]: Dicionário com os dados do resultado do workflow.
        """
        diconario: dict[str, Any] = self._converter_para_dict(self)
        return diconario
