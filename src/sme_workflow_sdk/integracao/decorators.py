"""Decorators para declarar ações associadas aos estados do workflow."""

from collections.abc import Callable
from typing import Any, TypeVar, cast

from sme_workflow_sdk.integracao.registro_acoes import registro_acoes

Metodo = TypeVar("Metodo", bound=Callable[..., Any])


def workflow(*, estado: str, acao: str) -> Callable[[Metodo], Metodo]:
    """Associa um método da aplicação consumidora a um estado e uma ação.

    Args:
        estado (str): _description_
        acao (str): _description_

    Raises:
        TypeError: _description_
        TypeError: _description_
        TypeError: _description_

    Returns:
        Callable[[Metodo], Metodo]: _description_
    """
    if not isinstance(estado, str) or not estado.strip():
        raise TypeError

    if not isinstance(acao, str) or not acao.strip():
        raise TypeError

    def decorator(metodo: Metodo) -> Metodo:
        if not callable(metodo):
            raise TypeError

        registro_acoes.registrar(
            estado=estado,
            acao=acao,
            metodo=cast(Callable[..., Any], metodo),
        )
        return metodo

    return decorator
