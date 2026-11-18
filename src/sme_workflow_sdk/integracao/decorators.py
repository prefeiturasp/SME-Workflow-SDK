"""Decorators para declarar ações associadas aos estados do workflow."""

from collections.abc import Callable
from typing import Any, cast

from sme_workflow_sdk.excecoes.integracao import (
    DeclaracaoWorkflowInvalidaError,
)
from sme_workflow_sdk.integracao.registro_acoes import registro_acoes


def workflow[Metodo: Callable[..., Any]](
    *, estado: str, acao: str
) -> Callable[[Metodo], Metodo]:
    """Associa um método da aplicação consumidora a um estado e uma ação.

    O decorator registra a referência do método no registro centralizado
    de ações do workflow, preservando sua implementação e seu comportamento
    original.

    A combinação de estado e ação identifica unicamente o método registrado.
    A validação de duplicidade é realizada pelo :class:`RegistroAcoes
    <sme_workflow_sdk.integracao.registro_acoes.RegistroAcoes>`.

    Args:
        estado (str): Nome do estado do workflow ao qual o método será
            associado.
        acao (str): Nome da ação do workflow executada pelo método.

    Raises:
        DeclaracaoWorkflowInvalidaError: e o estado ou a ação não forem
            strings não vazias ou se o objeto decorado não for chamável.
        AcaoDuplicadaError: Se já existir outro método registrado para
            a mesma combinação de estado e ação.

    Returns:
        Callable[[Metodo], Metodo]: Um decorator que registra e retorna o
            método original, preservando sua tipagem e comportamento.
    """
    if not isinstance(estado, str) or not estado.strip():
        raise DeclaracaoWorkflowInvalidaError(
            "O parâmetro 'estado' deve ser uma string não vazia."
        )

    if not isinstance(acao, str) or not acao.strip():
        raise DeclaracaoWorkflowInvalidaError(
            "O parâmetro 'acao' deve ser uma string não vazia."
        )

    def decorator(metodo: Metodo) -> Metodo:
        if not callable(metodo):
            raise DeclaracaoWorkflowInvalidaError(
                "O decorator @workflow deve ser aplicado a um método ou "
                "função."
            )

        registro_acoes.registrar(
            estado=estado,
            acao=acao,
            metodo=cast(Callable[..., Any], metodo),
        )
        return metodo

    return decorator
