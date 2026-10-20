"""Testes unitários para as funções de validação do domínio."""

from typing import Any

import pytest

from sme_workflow_sdk.dominio.validacao import (
    validar_booleano,
    validar_mapping,
    validar_string_nao_vazia,
    validar_tipo,
)
from sme_workflow_sdk.excecoes.base import ValidacaoDominioError


class TestValidarTipo:
    """Testes para validar_tipo."""

    @pytest.mark.parametrize(
        ("valor", "tipo_esperado"),
        [(1, int), ("texto", str), (True, (bool, int))],
    )
    def test_aceita_tipo_esperado(
        self, valor: Any, tipo_esperado: type | tuple[type, ...]
    ) -> None:
        """Deve aceitar valores do tipo esperado."""
        validar_tipo(valor, tipo_esperado, "tipo.campo")

    def test_aceita_tupla_de_tipos(self) -> None:
        """Deve aceitar valor correspondente a um dos tipos da tupla."""
        validar_tipo("texto", (int, str), "Tipo.campo")

    def test_rejeita_tipo_invalido(self) -> None:
        """Deve informar os tipos recebido e esperado."""
        with pytest.raises(ValidacaoDominioError) as exc:
            validar_tipo("texto", int, "Tipo.campo")
        assert str(exc.value) == "Tipo.campo deve ser int, recebido str"

    def test_rejeita_tipo_invalido_com_tupla(self) -> None:
        """Deve listar os tipos aceitos na mensagem."""
        with pytest.raises(ValidacaoDominioError) as exc:
            validar_tipo(1.5, (int, str), "Tipo.campo")

        assert (
            str(exc.value) == "Tipo.campo deve ser int | str, recebido float"
        )


class TestValidarStringNaoVazia:
    """Testes para validar_string_nao_vazia."""

    @pytest.mark.parametrize("valor", ["texto", " texto "])
    def test_aceita_string_nao_vazia(self, valor: str) -> None:
        """Deve aceitar strings que contenham caracteres."""
        validar_string_nao_vazia(valor, "Tipo.campo")

    @pytest.mark.parametrize("valor", ["", "   ", "\t\n"])
    def test_rejeita_string_vazia_ou_com_espacos(self, valor: str) -> None:
        """Deve rejeitar strings vazias ou compostas por espaços."""
        with pytest.raises(ValidacaoDominioError) as exc:
            validar_string_nao_vazia(valor, "Tipo.campo")

        assert str(exc.value) == "Tipo.campo não pode ser vazio"

    @pytest.mark.parametrize("valor", [None, 123, True])
    def test_rejeita_valor_que_nao_seja_string(self, valor: Any) -> None:
        """Deve rejeitar valores que não sejam strings."""
        with pytest.raises(ValidacaoDominioError) as exc:
            validar_string_nao_vazia(valor, "Tipo.campo")

        assert (
            str(exc.value)
            == f"Tipo.campo deve ser str, recebido {type(valor).__name__}"
        )


class TestValidarBooleano:
    """Testes para validar_booleano."""

    @pytest.mark.parametrize("valor", [True, False])
    def test_aceita_booleano(self, valor: bool) -> None:
        """Deve aceitar True e False."""
        validar_booleano(valor, "Tipo.campo")

    @pytest.mark.parametrize("valor", [0, 1, None, "true", [], ()])
    def test_rejeita_valor_que_nao_seja_booleano(self, valor: Any) -> None:
        """Deve rejeitar valores que não sejam estritamente bool."""
        with pytest.raises(ValidacaoDominioError) as exc:
            validar_booleano(valor, "Tipo.campo")

        assert (
            str(exc.value)
            == f"Tipo.campo deve ser bool, recebido {type(valor).__name__}"
        )


class TestValidarMapping:
    """Testes para validar_mapping."""

    @pytest.mark.parametrize("valor", [{}, {"chave": "valor"}])
    def test_aceita_mapping(self, valor: Any) -> None:
        """Deve aceitar objetos que implementem Mapping."""
        validar_mapping(valor, "Tipo.campo")

    def test_aceita_none_quando_permitido(self) -> None:
        """Deve aceitar None quando permitir_none for True."""
        validar_mapping(None, "Tipo.campo", permitir_none=True)

    def test_rejeita_none_quando_nao_permitido(self) -> None:
        """Deve rejeitar None quando não permitido."""
        with pytest.raises(ValidacaoDominioError) as exc:
            validar_mapping(None, "Tipo.campo")

        assert (
            str(exc.value)
            == "Tipo.campo não pode ser None; use '{}' para vazio"
        )

    @pytest.mark.parametrize("valor", [[], (), "texto", 123])
    def test_rejeita_valor_que_nao_seja_mapping(self, valor: Any) -> None:
        """Deve rejeitar valores que não implementem Mapping."""
        with pytest.raises(ValidacaoDominioError) as exc:
            validar_mapping(valor, "Tipo.campo")

        assert (
            str(exc.value)
            == f"Tipo.campo deve ser Mapping, recebido {type(valor).__name__}"
        )
