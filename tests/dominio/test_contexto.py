"""Testes unitários para ContextoExecucao."""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, cast

import pytest

from sme_workflow_sdk.dominio.contexto import ContextoExecucao
from sme_workflow_sdk.excecoes import ValidacaoDominioError


class TestContextoExecucao:
    """Casos de criação e validação do contexto de execução."""

    def test_cria_contexto_com_valores_padrao(self) -> None:
        """Deve gerar identificador e inicializar dados vazios."""
        contexto = ContextoExecucao(autor="usuario_1")

        assert contexto.autor == "usuario_1"
        assert contexto.identificador
        assert isinstance(contexto.dados, MappingProxyType)
        assert contexto.dados == {}

    def test_cria_contexto_com_dados(self) -> None:
        """Deve preservar os dados informados."""
        dados = {"solicitacao_id": 123, "origem": "portal"}

        contexto = ContextoExecucao(
            autor="usuario_1",
            identificador="execucao-123",
            dados=dados,
        )

        assert contexto.autor == "usuario_1"
        assert contexto.identificador == "execucao-123"
        assert contexto.dados == dados
        assert isinstance(contexto.dados, Mapping)

    def test_copia_dados_para_nao_refletir_alteracoes_externas(self) -> None:
        """Alterações no dicionário original não devem alterar o contexto."""
        dados = {"status": "aberto"}
        contexto = ContextoExecucao(autor="usuario_1", dados=dados)

        dados["status"] = "aprovado"

        assert contexto.dados["status"] == "aberto"

    def test_nao_permite_alterar_mapping_dados(self) -> None:
        """O mapeamento de dados deve ser somente leitura."""
        contexto = ContextoExecucao(autor="usuario_1")

        with pytest.raises(ValidacaoDominioError) as exc:
            cast(dict[str, Any], contexto.dados)["chave"]

        assert (
            str(exc.value)
            == "ContextoExecucao.dados não pôde ser convertido: 'mappingproxy'"
            " object does not support item assignment"
        )

    @pytest.mark.parametrize("autor", ["", "   "])
    def test_rejeita_autor_vazio(self, autor: str) -> None:
        """Deve rejeitar autor vazio ou composto por espaços."""
        with pytest.raises(ValidacaoDominioError) as exc:
            ContextoExecucao(autor=autor)

        assert str(exc.value) == "ContextoExecucao.autor não pode ser vazio"

    @pytest.mark.parametrize("autor", [None, 123, True])
    def test_rejeita_autor_com_tipo_invalido(self, autor: object) -> None:
        """Deve rejeitar autor que não seja string."""
        with pytest.raises(ValidacaoDominioError) as exc:
            ContextoExecucao(autor=cast(str, object()))

        assert (
            str(exc.value) == "ContextoExecucao.autor deve ser str, recebido "
            f"{type(autor).__name__}"
        )

    @pytest.mark.parametrize("identificador", ["", "   "])
    def test_rejeita_identificador_vazio(self, identificador: str) -> None:
        """Deve rejeitar identificador vazio ou composto por espaços."""
        with pytest.raises(ValidacaoDominioError) as exc:
            ContextoExecucao(autor="usuario_1", identificador=identificador)

        assert (
            str(exc.value)
            == "ContextoExecucao.identificador não pode ser vazio"
        )

    @pytest.mark.parametrize("identificador", [None, 123])
    def test_rejeita_identificador_com_tipo_invalido(
        self, identificador: object
    ) -> None:
        """Deve rejeitar identificador que não seja string."""
        with pytest.raises(ValidacaoDominioError) as exc:
            ContextoExecucao(
                autor="usuario_1", identificador=cast(str, object())
            )

        assert (
            str(exc.value)
            == "ContextoExecucao.identificador deve ser str, recebido "
            f"{type(identificador).__name__}"
        )

    def test_rejeita_dados_none(self) -> None:
        """Deve rejeitar None no campo dados."""
        with pytest.raises(ValidacaoDominioError) as exc:
            ContextoExecucao(
                autor="usuario_1", dados=cast(Mapping[str, Any], None)
            )

        assert (
            str(exc.value)
            == "ContextoExecucao.dados não pode ser None; use '{}' para vazio"
        )

    @pytest.mark.parametrize("dados", [[], (), "texto", 123])
    def test_rejeita_dados_que_nao_sao_mapping(self, dados: object) -> None:
        """Deve rejeitar dados que não implementem Mapping."""
        with pytest.raises(ValidacaoDominioError) as exc:
            ContextoExecucao(
                autor="usuario_1", dados=cast(Mapping[str, Any], object())
            )

        assert (
            str(exc.value)
            == "ContextoExecucao.dados deve ser Mapping, recebido "
            f"{type(dados).__name__}"
        )
