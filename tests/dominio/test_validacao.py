"""Testes unitários para as funções de validação do domínio."""

from typing import Any

import pytest

from sme_workflow_sdk.dominio.validacao import validar_tipo
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
