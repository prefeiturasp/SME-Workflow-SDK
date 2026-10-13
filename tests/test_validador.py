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
        match="A configuração fornecida é inválida.",
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
    with pytest.raises(
        ConfiguracaoWorkflowInvalidaError,
        match="Campo 'estados' ausente ou inválido.",
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
        match="Dados do estado 'aberto' inválidos.",
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


@pytest.mark.parametrize(
    "acoes",
    [[], (), None, "nao_e_dict", 42],
)
def test_deve_rejeitar_acoes_que_nao_e_dicionario(
    validador: ValidadorWorkflow,
    acoes: Any,
) -> None:
    """Rejeita estados cujo campo 'acoes' não é um dicionário."""

    configuracao = {"estados": {"aberto": {"acoes": acoes}}}
    with pytest.raises(
        ConfiguracaoWorkflowInvalidaError,
        match="As ações do estado 'aberto' estão no formato inválido",
    ):
        validador.validar(configuracao)


def test_deve_aceitar_estado_sem_acoes(
    validador: ValidadorWorkflow,
) -> None:
    """Aceita um estado cujo 'acoes' é um dicionário vazio."""
    configuracao: dict[str, Any] = {"estados": {"rejeitado": {"acoes": {}}}}

    validador.validar(configuracao)


@pytest.mark.parametrize("acao", ["", "   ", None, 123, 1.5, True])
def test_deve_rejeitar_nome_de_acao_invalido(
    validador: ValidadorWorkflow,
    acao: Any,
) -> None:
    """Rejeita ações cujo nome não é uma string não vazia."""
    configuracao = {
        "estados": {
            "aberto": {
                "acoes": {acao: {"proximo_estado": "x", "terminal": False}}
            }
        }
    }
    with pytest.raises(
        ConfiguracaoWorkflowInvalidaError,
        match="O estado 'aberto' possui uma ação com nome inválido",
    ):
        validador.validar(configuracao)


@pytest.mark.parametrize("dados", ["nao_e_dict", [], None, 42])
def test_deve_rejeitar_dados_de_acao_que_nao_e_dicionario(
    validador: ValidadorWorkflow,
    dados: Any,
) -> None:
    """Rejeita ações cujos dados não são um dicionário."""
    configuracao = {"estados": {"aberto": {"acoes": {"aprovar": dados}}}}
    with pytest.raises(
        ConfiguracaoWorkflowInvalidaError,
        match="A ação 'aprovar' do estado 'aberto' está no formato inválido",
    ):
        validador.validar(configuracao)


@pytest.mark.parametrize("dados", [{}, {"terminal": False}])
def test_deve_rejeitar_acao_sem_campo_proximo_estado(
    validador: ValidadorWorkflow,
    dados: Any,
) -> None:
    """Rejeita ações que não possuem o campo 'proximo_estado'."""
    configuracao = {"estados": {"aberto": {"acoes": {"aprovar": dados}}}}
    with pytest.raises(
        ConfiguracaoWorkflowInvalidaError,
        match="A ação 'aprovar' do estado 'aberto' deve possuir o campo "
        "'proximo_estado'",
    ):
        validador.validar(configuracao)


@pytest.mark.parametrize(
    "proximo_estado",
    ["", "   ", None, 123, []],
)
def test_deve_rejeitar_proximo_estado_invalido(
    validador: ValidadorWorkflow,
    proximo_estado: Any,
) -> None:
    """Rejeita ações cujo 'proximo_estado' não é string não vazia."""
    configuracao = {
        "estados": {
            "aberto": {
                "acoes": {"aprovar": {"proximo_estado": proximo_estado}}
            }
        }
    }
    with pytest.raises(
        ConfiguracaoWorkflowInvalidaError,
        match="O próximo estado da ação 'aprovar' do estado 'aberto' deve ser "
        "uma string não vazia",
    ):
        validador.validar(configuracao)


def test_deve_rejeitar_acao_sem_campo_terminal(
    validador: ValidadorWorkflow,
) -> None:
    """Rejeita ações que não possuem o campo 'terminal'."""
    configuracao = {
        "estados": {
            "aberto": {"acoes": {"aprovar": {"proximo_estado": "aprovado"}}}
        }
    }

    with pytest.raises(
        ConfiguracaoWorkflowInvalidaError,
        match="A ação 'aprovar' do estado 'aberto' deve possuir o campo "
        "'terminal'",
    ):
        validador.validar(configuracao)


@pytest.mark.parametrize("terminal", ["sim", 1, 0, None, [], ()])
def test_deve_rejeitar_terminal_que_nao_e_booleano(
    validador: ValidadorWorkflow,
    terminal: Any,
) -> None:
    """Rejeita ações cujo 'terminal' não é booleano."""

    configuracao = {
        "estados": {
            "aberto": {
                "acoes": {
                    "aprovar": {
                        "proximo_estado": "aprovado",
                        "terminal": terminal,
                    }
                }
            },
            "aprovado": {"acoes": {}},
        }
    }
    with pytest.raises(
        ConfiguracaoWorkflowInvalidaError,
        match="O campo 'terminal' da ação 'aprovar' do estado 'aberto' deve "
        "ser booleano.",
    ):
        validador.validar(configuracao)


def test_deve_aceitar_acao_valida(
    validador: ValidadorWorkflow,
) -> None:
    """Aceita uma ação com todos os campos válidos."""
    configuracao = {
        "estados": {
            "aberto": {
                "acoes": {
                    "aprovar": {
                        "proximo_estado": "aprovado",
                        "terminal": False,
                    }
                }
            }
        }
    }

    validador.validar(configuracao)
