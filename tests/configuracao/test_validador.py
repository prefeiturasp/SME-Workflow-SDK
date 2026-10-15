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
        configuracao_valida: dict[str, Any],
    ) -> None:
        """Deve aceitar uma configuração completa e válida."""
        validador.validar(configuracao_valida)
