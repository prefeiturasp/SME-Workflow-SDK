"""Testes unitários para ConfiguradorWorkflow."""

from pathlib import Path
from typing import Any

import pytest

from sme_workflow_sdk.configuracao.configurador import ConfiguradorWorkflow
from sme_workflow_sdk.configuracao.leitor import LeitorWorkflow
from sme_workflow_sdk.excecoes import (
    ArquivoNaoEncontradoError,
    FormatoInvalidoError,
)


class TestInicializacao:
    """Comportamento esperado na inicialização do configurador."""

    def test_cria_leitor_interno(
        self, configurador: ConfiguradorWorkflow
    ) -> None:
        """Deve instanciar um LeitorWorkflow internamente."""
        assert isinstance(configurador._leitor, LeitorWorkflow)


class TestCarregar:
    """Comportamento do método carregar."""

    def test_carrega_yaml_valido(
        self,
        configurador: ConfiguradorWorkflow,
        yaml_valido: Path,
        workflow_exemplo_dict: dict[str, Any],
    ) -> None:
        """Deve retornar o dicionário do workflow de exemplo."""
        configuracao = configurador.carregar(str(yaml_valido))

        assert configuracao == workflow_exemplo_dict
        assert "estados" in configuracao

    def test_delega_para_leitor(
        self,
        configurador: ConfiguradorWorkflow,
        yaml_valido: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Garante que o Configurador apenas delega ao Leitor."""
        chamado: dict[str, str] = {}

        def fake_carregar(caminho: str) -> dict[str, Any]:
            chamado["caminho"] = caminho
            return {"nome": "fake"}

        monkeypatch.setattr(configurador._leitor, "carregar", fake_carregar)

        resultado = configurador.carregar(str(yaml_valido))

        assert resultado == {"nome": "fake"}
        assert chamado["caminho"] == str(yaml_valido)

    def test_propaga_erro_de_formato(
        self, configurador: ConfiguradorWorkflow, tmp_path: Path
    ) -> None:
        """Deve propagar FormatoInvalidoError do leitor."""
        arquivo = tmp_path / "workflow.txt"
        arquivo.write_text("nome: teste\n", encoding="utf-8")

        with pytest.raises(FormatoInvalidoError) as exc:
            configurador.carregar(str(arquivo))

        assert (
            "Somente arquivos '.yaml, .yml' são aceitos. Recebido: '.txt'."
            in str(exc.value)
        )

    def test_propaga_erro_arquivo_nao_encontrado(
        self, configurador: ConfiguradorWorkflow, tmp_path: Path
    ) -> None:
        """Deve propagar ArquivoNaoEncontradoError do leitor."""
        caminho = tmp_path / "inexistente.yaml"
        with pytest.raises(ArquivoNaoEncontradoError) as exc:
            configurador.carregar(str(caminho))

        assert f"Arquivo não encontrado: '{str(caminho)}'." in str(exc.value)
