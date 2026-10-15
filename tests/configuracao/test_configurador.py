"""Testes unitários para ConfiguradorWorkflow."""

from pathlib import Path
from typing import Any

import pytest

from sme_workflow_sdk.configuracao import ConfiguradorWorkflow
from sme_workflow_sdk.configuracao.leitor import LeitorWorkflow
from sme_workflow_sdk.configuracao.validador import ValidadorWorkflow
from sme_workflow_sdk.excecoes import (
    AcaoInvalidaError,
    ArquivoNaoEncontradoError,
    EstadoInvalidoError,
    FormatoInvalidoError,
)


class TestInicializacao:
    """Comportamento esperado na inicialização do configurador."""

    def test_cria_leitor_interno(
        self, configurador: ConfiguradorWorkflow
    ) -> None:
        """Deve instanciar um LeitorWorkflow internamente."""
        assert isinstance(configurador._leitor, LeitorWorkflow)

    def test_cria_validador_interno(
        self, configurador: ConfiguradorWorkflow
    ) -> None:
        """Deve instanciar um ValidadorWorkflow internamente."""
        assert isinstance(configurador._validador, ValidadorWorkflow)


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


class TestValidar:
    """Comportamento do método validar."""

    def test_aceita_configuracao_valida(
        self,
        configurador: ConfiguradorWorkflow,
        workflow_exemplo_dict: dict[str, Any],
    ) -> None:
        """Deve aceitar uma configuração válida sem levantar erro."""
        configurador.validar(workflow_exemplo_dict)

    def test_delega_para_validador(
        self,
        configurador: ConfiguradorWorkflow,
        workflow_exemplo_dict: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Garante que o Configurador apenas delega ao Validador."""
        chamado: dict[str, Any] = {}

        def fake_validar(configuracao: dict[str, Any]) -> None:
            chamado["configuracao"] = configuracao

        monkeypatch.setattr(configurador._validador, "validar", fake_validar)

        configurador.validar(workflow_exemplo_dict)

        assert chamado["configuracao"] is workflow_exemplo_dict

    def test_propaga_erro_de_estado_invalido(
        self, configurador: ConfiguradorWorkflow
    ) -> None:
        """Deve propagar EstadoInvalidoError do validador."""
        configuracao: dict[str, Any] = {"estados": []}

        with pytest.raises(EstadoInvalidoError) as exc:
            configurador.validar(configuracao)
        assert "Campo 'estados' ausente ou inválido" in str(exc.value)

    def test_propaga_erro_de_acao_invalida(
        self, configurador: ConfiguradorWorkflow
    ) -> None:
        """Deve propagar AcaoInvalidaError do validador."""
        configuracao = {
            "estados": {"aberto": {"acoes": {"aprovar": {"terminal": True}}}}
        }

        with pytest.raises(AcaoInvalidaError) as exc:
            configurador.validar(configuracao)
        assert "deve possuir o campo 'proximo_estado'" in str(exc.value)
