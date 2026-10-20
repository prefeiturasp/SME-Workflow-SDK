"""Testes unitários para as entidades do workflow."""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, cast

import pytest

from sme_workflow_sdk.dominio.entidades import Acao, Estado, Transicao
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
            Acao(
                nome=cast(str, nome), proximo_estado="aprovado", terminal=True
            )

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
                terminal=cast(bool, terminal),
            )

        assert (
            str(exc.value) == "Acao.terminal deve ser bool, recebido "
            f"{type(terminal).__name__}"
        )


class TestEstado:
    """Validação da entidade Estado."""

    def test_cria_estado_com_acoes(self) -> None:
        """Deve criar estado e proteger seu mapeamento de ações."""
        acao = Acao(nome="aprovar", proximo_estado="aprovado", terminal=True)
        acoes = {"aprovar": acao}

        estado = Estado(nome="aberto", acoes=acoes)

        assert estado.nome == "aberto"
        assert estado.acoes == acoes
        assert isinstance(estado.acoes, MappingProxyType)

    def test_cria_estado_sem_acoes(self) -> None:
        """Deve aceitar None como mapeamento de ações."""
        estado = Estado(nome="finalizado", acoes=None)

        assert estado.acoes is None

    def test_copia_acoes_para_nao_refletir_alteracoes_externas(self) -> None:
        """Alterações no dicionário original não devem alterar o estado."""
        acao = Acao(nome="aprovar", proximo_estado="aprovado", terminal=True)
        acoes = {"aprovar": acao}
        estado = Estado(nome="aberto", acoes=acoes)

        acoes.clear()

        assert estado.acoes == {"aprovar": acao}

    def test_rejeita_nome_vazio(self) -> None:
        """Deve rejeitar nome de estado vazio."""
        with pytest.raises(ValidacaoDominioError) as exc:
            Estado(nome=" ", acoes=None)

        assert str(exc.value) == "Estado.nome não pode ser vazio"

    @pytest.mark.parametrize("acoes", [[], (), "texto", 123])
    def test_rejeita_acoes_que_nao_sao_mapping(self, acoes: object) -> None:
        """Deve rejeitar ações que não sejam Mapping nem None."""
        with pytest.raises(ValidacaoDominioError) as exc:
            Estado(nome="aberto", acoes=cast(Mapping[str, Any], acoes))

        assert (
            str(exc.value) == "Estado.acoes deve ser Mapping | None, recebido "
            f"{type(acoes).__name__}"
        )

    def test_rejeita_nome_de_acao_vazio(self) -> None:
        """Deve rejeitar chave de ação vazia."""
        acao = Acao(nome="aprovar", proximo_estado="aprovado", terminal=True)

        with pytest.raises(ValidacaoDominioError) as exc:
            Estado(nome="aberto", acoes={" ": acao})

        assert (
            str(exc.value) == "Estado.acoes: nome da ação não pode ser vazio"
        )

    def test_rejeita_valor_que_nao_seja_acao(self) -> None:
        """Deve rejeitar valores do mapeamento que não sejam Acao."""
        acao = cast(Acao, "invalida")
        with pytest.raises(ValidacaoDominioError) as exc:
            Estado(nome="aberto", acoes={"aprovar": acao})

        assert (
            str(exc.value)
            == "Estado.acoes[aprovar] deve ser Acao, recebido str"
        )


class TestTransicao:
    """Validação da entidade Transicao."""

    def test_cria_transicao_valida(self) -> None:
        """Deve criar transição com todos os campos válidos."""
        transicao = Transicao(
            estado_anterior="aberto",
            acao="aprovar",
            proximo_estado="aprovado",
            terminal=True,
        )

        assert transicao.estado_anterior == "aberto"
        assert transicao.acao == "aprovar"
        assert transicao.proximo_estado == "aprovado"
        assert transicao.terminal is True

    @pytest.mark.parametrize(
        ("campo", "valor", "mensagem"),
        [
            (
                "estado_anterior",
                "",
                "Transicao.estado_anterior não pode ser vazio",
            ),
            ("acao", " ", "Transicao.acao não pode ser vazio"),
            (
                "proximo_estado",
                "",
                "Transicao.proximo_estado não pode ser vazio",
            ),
        ],
    )
    def test_rejeita_strings_obrigatorias_vazias(
        self, campo: str, valor: str, mensagem: str
    ) -> None:
        """Deve rejeitar campos textuais obrigatórios vazios."""
        valores: dict[str, object] = {
            "estado_anterior": "aberto",
            "acao": "aprovar",
            "proximo_estado": "aprovado",
            "terminal": True,
        }
        valores[campo] = valor

        with pytest.raises(ValidacaoDominioError) as exc:
            Transicao(
                estado_anterior=cast(str, valores["estado_anterior"]),
                acao=cast(str, valores["acao"]),
                proximo_estado=cast(str, valores["proximo_estado"]),
                terminal=cast(bool, valores["terminal"]),
            )

        assert str(exc.value) == mensagem

    def test_rejeita_terminal_nao_booleano(self) -> None:
        """Deve rejeitar terminal que não seja bool."""
        with pytest.raises(ValidacaoDominioError) as exc:
            Transicao(
                estado_anterior="aberto",
                acao="aprovar",
                proximo_estado="aprovado",
                terminal=cast(bool, 1),
            )

        assert (
            str(exc.value) == "Transicao.terminal deve ser bool, recebido int"
        )
