from typing import Any

import pytest

from sme_workflow_sdk.configuracao.validador import ValidadorWorkflow
from sme_workflow_sdk.excecoes import ConfiguracaoWorkflowInvalidaError


def test_deve_validar_configuracao_valida(
    validador: ValidadorWorkflow,
    configuracao_valida: dict[str, Any],
) -> None:
    """Aceita uma configuração válida."""
    validador.validar(configuracao_valida)


@pytest.mark.parametrize("configuracao", [None, []])
def test_deve_rejeitar_configuracao_que_nao_e_dicionario(
    validador: ValidadorWorkflow,
    configuracao: Any,
) -> None:
    """Rejeita configuração que não é um dicionário."""
    with pytest.raises(
        ConfiguracaoWorkflowInvalidaError,
        match="A configuração deve ser um dicionário.",
    ):
        validador.validar(configuracao)


@pytest.mark.parametrize(
    "configuracao",
    [
        {},
        {"estados": {}},
        {"estados": []},
        {"estados": None},
        {"ESTADOS": {"acao": "aprovado"}},
    ],
)
def test_deve_rejeitar_configuracao_sem_estados_validos(
    validador: ValidadorWorkflow,
    configuracao: Any,
) -> None:
    """Rejeita configurações sem um dicionário de estados válido."""
    mensagem = (
        "A configuração deve possuir um dicionário não vazio no campo "
        "'estados'."
    )
    with pytest.raises(
        ConfiguracaoWorkflowInvalidaError,
        match=mensagem,
    ):
        validador.validar(configuracao)


def test_deve_rejeitar_estado_sem_acoes(
    validador: ValidadorWorkflow,
) -> None:
    """Rejeita estados sem o campo acoes."""
    configuracao: dict[str, Any] = {"estados": {"aberto": {}}}

    with pytest.raises(
        ConfiguracaoWorkflowInvalidaError,
        match="O estado 'aberto' deve possuir o campo 'acoes'.",
    ):
        validador.validar(configuracao)


def test_deve_rejeitar_acoes_em_formato_invalido(
    validador: ValidadorWorkflow,
) -> None:
    """Rejeita ações que não sejam um dicionário."""
    configuracao: dict[str, Any] = {"estados": {"aberto": []}}

    with pytest.raises(
        ConfiguracaoWorkflowInvalidaError,
        match="O estado 'aberto' deve ser um dicionário.",
    ):
        validador.validar(configuracao)


@pytest.mark.parametrize(
    "configuracao",
    [
        {"estados": {"": {"acoes": {}}}},
        {"estados": {"   ": {"acoes": {}}}},
        {"estados": {None: {"acoes": {}}}},
        {"estados": {123: {"acoes": {}}}},
        {"estados": {1.5: {"acoes": {}}}},
        {"estados": {True: {"acoes": {}}}},
    ],
)
def test_deve_rejeitar_nome_de_estado_invalido(
    validador: ValidadorWorkflow,
    configuracao: Any,
) -> None:
    """Rejeita estados cujo nome não é uma string não vazia."""
    with pytest.raises(
        ConfiguracaoWorkflowInvalidaError,
        match="O nome de cada estado deve ser uma string não vazia.",
    ):
        validador.validar(configuracao)
