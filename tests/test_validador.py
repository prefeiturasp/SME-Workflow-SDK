from typing import Any

import pytest

from sme_workflow_sdk.configuracao.validador import ValidadorWorkflow
from sme_workflow_sdk.excecoes import ConfiguracaoYamlError


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
        ConfiguracaoYamlError,
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
        ConfiguracaoYamlError,
        match="Campo 'estados' ausente ou inválido.",
    ):
        validador.validar(configuracao)


def test_deve_rejeitar_estado_sem_acoes(
    validador: ValidadorWorkflow,
) -> None:
    """Rejeita estados sem o campo acoes."""
    configuracao: dict[str, Any] = {"estados": {"aberto": {}}}

    with pytest.raises(
        ConfiguracaoYamlError,
        match="O estado 'aberto' deve possuir o campo 'acoes'.",
    ):
        validador.validar(configuracao)


def test_deve_rejeitar_acoes_em_formato_invalido(
    validador: ValidadorWorkflow,
) -> None:
    """Rejeita o campo 'acoes' quando não é um dicionário nem None"""
    configuracao: dict[str, Any] = {"estados": {"aberto": {"acoes": []}}}

    with pytest.raises(
        ConfiguracaoYamlError,
        match="As ações do estado 'aberto' estão no formato inválido",
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
        ConfiguracaoYamlError,
        match="O nome de cada estado deve ser uma string não vazia.",
    ):
        validador.validar(configuracao)


@pytest.mark.parametrize(
    "acoes",
    [[], (), "nao_e_dict", 42],
)
def test_deve_rejeitar_acoes_que_nao_e_dicionario_ou_none(
    validador: ValidadorWorkflow,
    acoes: Any,
) -> None:
    """Rejeita estados cujo campo 'acoes' não é um dicionário."""

    configuracao = {"estados": {"aberto": {"acoes": acoes}}}
    with pytest.raises(
        ConfiguracaoYamlError,
        match="As ações do estado 'aberto' estão no formato inválido",
    ):
        validador.validar(configuracao)


def test_deve_aceitar_estado_sem_acoes(
    validador: ValidadorWorkflow,
) -> None:
    """Aceita estados sem ações representados por None."""
    configuracao: dict[str, Any] = {
        "estados": {
            "aberto": {
                "acoes": {
                    "rejeitar": {
                        "proximo_estado": "rejeitado",
                        "terminal": True,
                    }
                }
            },
            "rejeitado": {"acoes": None},
        }
    }

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
        ConfiguracaoYamlError,
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
        ConfiguracaoYamlError,
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
        ConfiguracaoYamlError,
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
        ConfiguracaoYamlError,
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
        ConfiguracaoYamlError,
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
        ConfiguracaoYamlError,
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
                        "terminal": True,
                    }
                }
            },
            "aprovado": {"acoes": None},
        }
    }

    validador.validar(configuracao)


def test_deve_rejeitar_referencia_a_estado_inexistente(
    validador: ValidadorWorkflow,
) -> None:
    """Rejeita transições para estados não declarados."""
    configuracao = {
        "estados": {
            "aberto": {
                "acoes": {
                    "aprovar": {
                        "proximo_estado": "aprovado",
                        "terminal": True,
                    }
                }
            }
        }
    }

    with pytest.raises(
        ConfiguracaoYamlError,
        match="A ação 'aprovar' do estado 'aberto' referencia o estado "
        "inexistente 'aprovado'.",
    ):
        validador.validar(configuracao)


def test_deve_rejeitar_destino_terminal_com_acoes(
    validador: ValidadorWorkflow,
) -> None:
    """Rejeita estado terminal que possui ações configuradas."""
    configuracao = {
        "estados": {
            "aberto": {
                "acoes": {
                    "finalizar": {
                        "proximo_estado": "concluido",
                        "terminal": True,
                    }
                }
            },
            "concluido": {
                "acoes": {
                    "reabrir": {
                        "proximo_estado": "aberto",
                        "terminal": False,
                    }
                }
            },
        }
    }

    with pytest.raises(
        ConfiguracaoYamlError,
        match="A ação 'finalizar' do estado 'aberto' é terminal, mas "
        "o estado de destino 'concluido' possui ações configuradas.",
    ):
        validador.validar(configuracao)


def test_deve_rejeitar_destino_sem_acoes_em_transicao_nao_terminal(
    validador: ValidadorWorkflow,
) -> None:
    """Rejeita destino sem ações em transição não terminal."""
    configuracao = {
        "estados": {
            "aberto": {
                "acoes": {
                    "avancar": {
                        "proximo_estado": "finalizado",
                        "terminal": False,
                    }
                }
            },
            "finalizado": {"acoes": None},
        }
    }

    with pytest.raises(
        ConfiguracaoYamlError,
        match="A ação 'avancar' do estado 'aberto' não é terminal, mas o "
        "estado de destino 'finalizado' não possui ações configuradas.",
    ):
        validador.validar(configuracao)


@pytest.mark.parametrize("dados_estado", [None, [], "invalido", 123])
def test_deve_rejeitar_dados_de_estado_que_nao_e_dicionario(
    validador: ValidadorWorkflow,
    dados_estado: Any,
) -> None:
    """Rejeita estados cujos dados não são um dicionário."""
    configuracao = {
        "estados": {
            "aberto": dados_estado,
        },
    }

    with pytest.raises(
        ConfiguracaoYamlError,
        match="Dados do estado 'aberto' inválidos.",
    ):
        validador.validar(configuracao)


def test_deve_rejeitar_acao_com_chaves_nao_permitidas(
    validador: ValidadorWorkflow,
) -> None:
    """Rejeita ações que possuem campos não permitidos."""
    configuracao = {
        "estados": {
            "aberto": {
                "acoes": {
                    "aprovar": {
                        "proximo_estado": "aprovado",
                        "terminal": True,
                        "handler": "aprovar_solicitacao",
                    },
                },
            },
            "aprovado": {"acoes": None},
        },
    }

    with pytest.raises(
        ConfiguracaoYamlError,
        match="A ação 'aprovar' do estado 'aberto' possui chaves não "
        "permitidas: handler. Permitidas: proximo_estado, terminal.",
    ):
        validador.validar(configuracao)


@pytest.mark.parametrize("nome_estado", ["", "   ", None, 123])
def test_deve_rejeitar_nome_invalido_de_estado_sem_acoes(
    validador: ValidadorWorkflow,
    nome_estado: Any,
) -> None:
    """Rejeita nomes inválidos mesmo em estados sem ações."""
    configuracao = {
        "estados": {
            nome_estado: {"acoes": None},
        },
    }

    with pytest.raises(
        ConfiguracaoYamlError,
        match="O nome de cada estado deve ser uma string não vazia.",
    ):
        validador.validar(configuracao)
