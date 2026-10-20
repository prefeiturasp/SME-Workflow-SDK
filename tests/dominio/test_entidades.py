"""Testes unitários para as entidades do workflow."""

import pytest

from sme_workflow_sdk.dominio.entidades import Acao
from sme_workflow_sdk.excecoes import ValidacaoDominioError


class TestAcao:
    """Validação da entidade Acao."""

    def test_cria_acao_valida(self) -> None:
        """Deve criar ação com todos os campos válidos."""
        acao = Acao(nome="aprovar", proximo_estado="aprovado", terminal=True)

        assert acao.nome == "aprovar"
        assert acao.proximo_estado == "aprovado"
        assert acao.terminal is True

    @pytest.mark.parametrize("nome", ["", "   "])
    def test_rejeita_nome_vazio(self, nome: str) -> None:
        """Deve rejeitar nome vazio."""
        with pytest.raises(ValidacaoDominioError) as exc:
            Acao(nome=nome, proximo_estado="aprovado", terminal=True)

        assert str(exc.value) == "Acao.nome não pode ser vazio"

    @pytest.mark.parametrize("nome", [None, 123])
    def test_rejeita_nome_com_tipo_invalido(self, nome: object) -> None:
        """Deve rejeitar nome que não seja string."""
        with pytest.raises(ValidacaoDominioError) as exc:
            Acao(nome=nome, proximo_estado="aprovado", terminal=True)

        assert (
            str(exc.value)
            == f"Acao.nome deve ser str, recebido {type(nome).__name__}"
        )

    @pytest.mark.parametrize("proximo_estado", ["", "   "])
    def test_rejeita_proximo_estado_vazio(self, proximo_estado: str) -> None:
        """Deve rejeitar estado de destino vazio."""
        with pytest.raises(ValidacaoDominioError) as exc:
            Acao(nome="aprovar", proximo_estado=proximo_estado, terminal=True)

        assert str(exc.value) == "Acao.proximo_estado não pode ser vazio"

    @pytest.mark.parametrize("terminal", [1, 0, None, "sim"])
    def test_rejeita_terminal_nao_booleano(self, terminal: object) -> None:
        """Deve rejeitar terminal que não seja bool."""
        with pytest.raises(ValidacaoDominioError) as exc:
            Acao(
                nome="aprovar",
                proximo_estado="aprovado",
                terminal=terminal,
            )

        assert (
            str(exc.value) == "Acao.terminal deve ser bool, recebido "
            f"{type(terminal).__name__}"
        )
