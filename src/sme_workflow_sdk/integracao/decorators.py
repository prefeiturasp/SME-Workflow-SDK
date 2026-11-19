"""Decorators para declarar ações associadas aos estados do workflow."""

from collections.abc import Callable
from functools import wraps
from typing import Any, cast

from sme_workflow_sdk.excecoes.integracao import (
    DeclaracaoWorkflowInvalidaError,
)
from sme_workflow_sdk.integracao.registro_acoes import registro_acoes


def workflow[Retorno](
    *, estado: str, acao: str
) -> Callable[[Callable[..., Retorno]], Callable[..., Retorno]]:
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

    estado_declarado = estado

    def decorator(metodo: Callable[..., Retorno]) -> Callable[..., Retorno]:
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

        @wraps(metodo)
        def wrapper(
            *args: Any,
            estado: str,
            **kwargs: Any,
        ) -> Retorno:
            # Importação local para evitar acoplamento/ciclo de importação
            # durante a declaração dos métodos decorados.
            from sme_workflow_sdk.runtime import get_workflow

            if estado != estado_declarado:
                raise TypeError

            motor = get_workflow()
            motor.validar(estado_atual=estado, acao=acao)

            return metodo(*args, **kwargs)

        return wrapper

    return decorator
