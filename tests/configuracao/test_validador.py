"""Testes unitários para o ValidadorWorkflow."""

from typing import Any

import pytest

from sme_workflow_sdk.configuracao.validador import ValidadorWorkflow
from sme_workflow_sdk.excecoes import AcaoInvalidaError, EstadoInvalidoError


class TestConfiguracaoRaiz:
    """Erros na raiz da configuração (fora dos estados)."""

    @pytest.mark.parametrize("configuracao", [None, []])
    def test_deve_rejeitar_configuracao_nao_dicionario(
        self, validador: ValidadorWorkflow, configuracao: Any
    ) -> None:
        """Deve rejeitar configuração que não é dicionário."""
        with pytest.raises(EstadoInvalidoError) as exc:
            validador.validar(configuracao)

        assert "A configuração fornecida é inválida" in str(exc.value)

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
        self, validador: ValidadorWorkflow, configuracao: Any
    ) -> None:
        """Deve rejeitar configurações sem dicionário de estados."""
        with pytest.raises(EstadoInvalidoError) as exc:
            validador.validar(configuracao)
        assert "Campo 'estados' ausente ou inválido" in str(exc.value)


class TestNomeDoEstado:
    """Erros relacionados ao nome do estado."""

    @pytest.mark.parametrize("nome_estado", ["", "   ", None, 123])
    def test_deve_rejeitar_nome_invalido_em_estado_sem_acoes(
        self, validador: ValidadorWorkflow, nome_estado: Any
    ) -> None:
        """Deve rejeitar nome inválido mesmo em estado sem ações."""
        configuracao = {"estados": {nome_estado: {"acoes": None}}}

        with pytest.raises(EstadoInvalidoError) as exc:
            validador.validar(configuracao)

        assert "O nome de cada estado deve ser uma string não vazia" in str(
            exc.value
        )

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
    def test_deve_rejeitar_nome_invalido_em_estado_com_acoes(
        self, validador: ValidadorWorkflow, configuracao: Any
    ) -> None:
        """Deve rejeitar nome inválido em estado com ações."""
        with pytest.raises(EstadoInvalidoError) as exc:
            validador.validar(configuracao)
        assert "O nome de cada estado deve ser uma string não vazia" in str(
            exc.value
        )


class TestDadosDoEstado:
    """Erros relacionados aos dados do estado."""

    def test_deve_rejeitar_dados_que_nao_sao_dicionario(
        self, validador: ValidadorWorkflow
    ) -> None:
        """Deve rejeitar estado cujos dados não são dicionário."""
        configuracao: dict[str, Any] = {"estados": {"aberto": []}}

        with pytest.raises(EstadoInvalidoError) as exc:
            validador.validar(configuracao)
        assert "Dados do estado 'aberto' inválidos" in str(exc.value)

    def test_deve_rejeitar_estado_sem_campo_acoes(
        self, validador: ValidadorWorkflow
    ) -> None:
        """Deve rejeitar estado sem o campo 'acoes'."""
        configuracao: dict[str, Any] = {"estados": {"aberto": {}}}

        with pytest.raises(AcaoInvalidaError) as exc:
            validador.validar(configuracao)
        assert "O estado 'aberto' deve possuir o campo 'acoes'" in str(
            exc.value
        )


class TestCampoAcoes:
    """Erros relacionados ao campo 'acoes' do estado."""

    def test_deve_aceitar_estado_sem_acoes(
        self, validador: ValidadorWorkflow
    ) -> None:
        """Deve aceitar estado com 'acoes' igual a None."""
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

    @pytest.mark.parametrize("acoes", [[], (), "nao_e_dict", 42])
    def test_deve_rejeitar_acoes_em_formato_invalido(
        self, validador: ValidadorWorkflow, acoes: Any
    ) -> None:
        """Deve rejeitar 'acoes' que não é dicionário nem None."""
        configuracao: dict[str, Any] = {
            "estados": {"aberto": {"acoes": acoes}},
        }

        with pytest.raises(AcaoInvalidaError) as exc:
            validador.validar(configuracao)
        assert "As ações do estado 'aberto' estão no formato inválido" in str(
            exc.value
        )


class TestConfiguracaoValida:
    """Casos de configuração que devem ser aceitos."""

    def test_deve_validar_configuracao_valida(
        self,
        validador: ValidadorWorkflow,
        workflow_exemplo_dict: dict[str, Any],
    ) -> None:
        """Deve aceitar uma configuração completa e válida."""
        validador.validar(workflow_exemplo_dict)


class TestAcaoValida:
    """Casos de ações que devem ser aceitas."""

    def test_deve_aceitar_acao_valida(
        self, validador: ValidadorWorkflow
    ) -> None:
        """Deve aceitar ação com todos os campos válidos."""
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


class TestNomeDaAcao:
    """Erros relacionados ao nome da ação."""

    @pytest.mark.parametrize("acao", ["", "   ", None, 123, 1.5, True])
    def test_deve_rejeitar_nome_invalido(
        self, validador: ValidadorWorkflow, acao: Any
    ) -> None:
        """Deve rejeitar ação cujo nome não é string não vazia."""
        configuracao = {
            "estados": {
                "aberto": {
                    "acoes": {
                        acao: {
                            "proximo_estado": "x",
                            "terminal": False,
                        }
                    }
                }
            }
        }

        with pytest.raises(AcaoInvalidaError) as exc:
            validador.validar(configuracao)
        assert "O estado 'aberto' possui uma ação com nome inválido" in str(
            exc.value
        )


class TestDadosDaAcao:
    """Erros relacionados aos dados da ação."""

    @pytest.mark.parametrize("dados", ["nao_e_dict", [], None, 42])
    def test_deve_rejeitar_dados_que_nao_sao_dicionario(
        self, validador: ValidadorWorkflow, dados: Any
    ) -> None:
        """Deve rejeitar ação cujos dados não são um dicionário."""
        configuracao = {"estados": {"aberto": {"acoes": {"aprovar": dados}}}}

        with pytest.raises(AcaoInvalidaError) as exc:
            validador.validar(configuracao)
        assert (
            "A ação 'aprovar' do estado 'aberto' está no formato inválido"
            in str(exc.value)
        )

    def test_deve_rejeitar_chaves_nao_permitidas(
        self, validador: ValidadorWorkflow
    ) -> None:
        """Deve rejeitar ação com campos fora do permitido."""
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

        with pytest.raises(AcaoInvalidaError) as exc:
            validador.validar(configuracao)
        assert (
            "A ação 'aprovar' do estado 'aberto' possui chaves não "
            "permitidas: 'handler'. Permitidas: 'proximo_estado, terminal'."
            in str(exc.value)
        )


class TestCampoProximoEstado:
    """Erros relacionados ao campo 'proximo_estado'."""

    @pytest.mark.parametrize("dados", [{}, {"terminal": False}])
    def test_deve_rejeitar_acao_sem_proximo_estado(
        self, validador: ValidadorWorkflow, dados: Any
    ) -> None:
        """Deve rejeitar ação que não possui 'proximo_estado'."""
        configuracao = {"estados": {"aberto": {"acoes": {"aprovar": dados}}}}

        with pytest.raises(AcaoInvalidaError) as exc:
            validador.validar(configuracao)
        assert (
            "A ação 'aprovar' do estado 'aberto' deve possuir o campo "
            "'proximo_estado'" in str(exc.value)
        )

    @pytest.mark.parametrize("proximo_estado", ["", "   ", None, 123, []])
    def test_deve_rejeitar_proximo_estado_invalido(
        self,
        validador: ValidadorWorkflow,
        proximo_estado: Any,
    ) -> None:
        """Deve rejeitar 'proximo_estado' que não é string não vazia."""
        configuracao = {
            "estados": {
                "aberto": {
                    "acoes": {
                        "aprovar": {
                            "proximo_estado": proximo_estado,
                        }
                    }
                }
            }
        }

        with pytest.raises(AcaoInvalidaError) as exc:
            validador.validar(configuracao)
        assert (
            "O próximo estado da ação 'aprovar' do estado 'aberto' deve ser "
            "uma string não vazia" in str(exc.value)
        )


class TestCampoTerminal:
    """Erros relacionados ao campo 'terminal'."""

    def test_deve_rejeitar_acao_sem_terminal(
        self, validador: ValidadorWorkflow
    ) -> None:
        """Deve rejeitar ação que não possui 'terminal'."""
        configuracao = {
            "estados": {
                "aberto": {
                    "acoes": {"aprovar": {"proximo_estado": "aprovado"}}
                }
            }
        }

        with pytest.raises(AcaoInvalidaError) as exc:
            validador.validar(configuracao)
        assert (
            "A ação 'aprovar' do estado 'aberto' deve possuir o campo "
            "'terminal'" in str(exc.value)
        )

    @pytest.mark.parametrize("terminal", ["sim", 1, 0, None, [], ()])
    def test_deve_rejeitar_terminal_nao_booleano(
        self, validador: ValidadorWorkflow, terminal: Any
    ) -> None:
        """Deve rejeitar 'terminal' que não é booleano."""
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

        with pytest.raises(AcaoInvalidaError) as exc:
            validador.validar(configuracao)
        assert (
            "O campo 'terminal' da ação 'aprovar' do estado 'aberto' deve ser"
            " booleano" in str(exc.value)
        )


class TestReferenciaAoProximoEstado:
    """Erros de referência a estados inexistentes."""

    def test_deve_rejeitar_estado_inexistente(
        self, validador: ValidadorWorkflow
    ) -> None:
        """Deve rejeitar transição para estado não declarado."""
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

        with pytest.raises(EstadoInvalidoError) as exc:
            validador.validar(configuracao)

        assert (
            "A ação 'aprovar' do estado 'aberto' referencia o estado "
            "inexistente 'aprovado'" in str(exc.value)
        )


class TestCoerenciaComEstadoDeDestino:
    """Erros de incoerência entre 'terminal' e ações do destino."""

    def test_deve_rejeitar_destino_sem_acoes_em_transicao_nao_terminal(
        self, validador: ValidadorWorkflow
    ) -> None:
        """Não terminal cujo destino não tem ações deve falhar."""
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

        with pytest.raises(AcaoInvalidaError) as exc:
            validador.validar(configuracao)

        assert (
            "A ação 'avancar' do estado 'aberto' não é terminal, mas o estado"
            " de destino 'finalizado' não possui ações configuradas"
            in str(exc.value)
        )

    def test_deve_rejeitar_destino_terminal_com_acoes(
        self, validador: ValidadorWorkflow
    ) -> None:
        """Terminal cujo destino possui ações deve falhar."""
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

        with pytest.raises(AcaoInvalidaError) as exc:
            validador.validar(configuracao)

        assert (
            "A ação 'finalizar' do estado 'aberto' é terminal, mas o "
            "estado de destino 'concluido' possui ações configuradas"
            in str(exc.value)
        )
