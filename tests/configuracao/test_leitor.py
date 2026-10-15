"""Testes unitários para LeitorWorkflow."""

from pathlib import Path
from typing import Any

import pytest

from sme_workflow_sdk.configuracao.leitor import LeitorWorkflow
from sme_workflow_sdk.excecoes import (
    ArquivoNaoEncontradoError,
    ConfiguracaoInvalidaError,
    FormatoInvalidoError,
)


class TestCarregarSucesso:
    """Cenários de carregamento bem-sucedido."""

    def test_carrega_yaml_valido(
        self,
        leitor: LeitorWorkflow,
        yaml_valido: Path,
        workflow_exemplo_dict: dict[str, Any],
    ) -> None:
        """Deve carregar um YAML válido e retornar o dicionário."""
        configuracao = leitor.carregar(str(yaml_valido))

        assert isinstance(configuracao, dict)
        assert configuracao == workflow_exemplo_dict

    def test_estrutura_de_estados(
        self, leitor: LeitorWorkflow, yaml_valido: Path
    ) -> None:
        """Deve preservar a estrutura de estados e ações do YAML."""
        configuracao = leitor.carregar(str(yaml_valido))

        estados = configuracao["estados"]
        assert set(estados.keys()) == {
            "aberto",
            "aprovado",
            "em_execucao",
            "rejeitado",
            "concluido",
        }
        assert estados["aberto"]["acoes"]["aprovar"] == {
            "proximo_estado": "aprovado",
            "terminal": False,
        }
        assert estados["rejeitado"]["acoes"] is None
        assert estados["concluido"]["acoes"] is None

    def test_aceita_extensao_yml(
        self,
        leitor: LeitorWorkflow,
        yaml_extensao_yml: Path,
        workflow_exemplo_dict: dict[str, Any],
    ) -> None:
        """Deve aceitar arquivos com extensão .yml."""
        configuracao = leitor.carregar(str(yaml_extensao_yml))
        assert configuracao == workflow_exemplo_dict

    def test_aceita_extensao_maiuscula(
        self,
        leitor: LeitorWorkflow,
        tmp_path: Path,
    ) -> None:
        """Deve aceitar extensão em maiúsculas (ex.: .YAML)."""
        arquivo = tmp_path / "workflow.YAML"
        arquivo.write_text("nome: teste\n", encoding="utf-8")

        configuracao = leitor.carregar(str(arquivo))
        assert configuracao == {"nome": "teste"}


class TestValidacaoDeCaminho:
    """Erros relacionados ao caminho do arquivo."""

    def test_extensao_invalida(
        self, leitor: LeitorWorkflow, arquivo_extensao_invalida: Path
    ) -> None:
        """Deve rejeitar arquivos com extensão não suportada."""
        with pytest.raises(FormatoInvalidoError) as exc:
            leitor.carregar(str(arquivo_extensao_invalida))
        assert (
            "Somente arquivos '.yaml, .yml' são aceitos. Recebido: '.txt'"
            in str(exc.value)
        )

    def test_sem_extensao(
        self, leitor: LeitorWorkflow, arquivo_sem_extensao: Path
    ) -> None:
        """Deve rejeitar arquivos sem extensão."""
        with pytest.raises(FormatoInvalidoError) as exc:
            leitor.carregar(str(arquivo_sem_extensao))

        assert "sem extensão" in str(exc.value)
        assert (
            "Somente arquivos '.yaml, .yml' são aceitos. Recebido: 'sem "
            "extensão'" in str(exc.value)
        )

    def test_arquivo_inexistente(
        self, leitor: LeitorWorkflow, tmp_path: Path
    ) -> None:
        """Deve lançar erro quando o caminho não existe."""
        caminho = tmp_path / "nao_existe.yaml"

        with pytest.raises(ArquivoNaoEncontradoError) as exc:
            leitor.carregar(str(caminho))

        assert f"Arquivo não encontrado: '{caminho}'." in str(exc.value)

    def test_diretorio_em_vez_de_arquivo(
        self, leitor: LeitorWorkflow, tmp_path: Path
    ) -> None:
        """Deve lançar erro quando o caminho aponta para diretório."""
        diretorio = tmp_path / "pasta.yaml"
        diretorio.mkdir()

        with pytest.raises(ArquivoNaoEncontradoError) as exc:
            leitor.carregar(str(diretorio))

        assert f"'{diretorio}' não é um arquivo válido" in str(exc.value)


class TestLeituraYaml:
    """Erros na leitura/parsing do YAML."""

    def test_yaml_com_sintaxe_invalida(
        self, leitor: LeitorWorkflow, yaml_sintaxe_invalida: Path
    ) -> None:
        """Deve lançar erro quando o YAML tem sintaxe inválida."""
        with pytest.raises(FormatoInvalidoError) as exc:
            leitor.carregar(str(yaml_sintaxe_invalida))

        assert f"YAML inválido em '{str(yaml_sintaxe_invalida)}'" in str(
            exc.value
        )

    def test_encoding_invalido(
        self, leitor: LeitorWorkflow, yaml_encoding_invalido: Path
    ) -> None:
        """Deve lançar erro quando o arquivo não está em UTF-8."""
        with pytest.raises(FormatoInvalidoError) as exc:
            leitor.carregar(str(yaml_encoding_invalido))

        assert (
            f"Arquivo '{str(yaml_encoding_invalido)}' não está em UTF-8"
            in str(exc.value)
        )

    def test_multiplos_documentos_yaml(
        self, leitor: LeitorWorkflow, yaml_multiplos_documentos: Path
    ) -> None:
        """Deve lançar erro quando há múltiplos documentos YAML."""
        with pytest.raises(FormatoInvalidoError) as exc:
            leitor.carregar(str(yaml_multiplos_documentos))

        assert (
            "Esperado exatamente 1 documento YAML em "
            f"'{str(yaml_multiplos_documentos)}', encontrados: 2."
            in str(exc.value)
        )


class TestValidacaoDeConteudo:
    """Erros no conteúdo do YAML."""

    def test_arquivo_vazio(
        self, leitor: LeitorWorkflow, yaml_vazio: Path
    ) -> None:
        """Deve lançar erro quando o arquivo está vazio."""
        with pytest.raises(ConfiguracaoInvalidaError) as exc:
            leitor.carregar(str(yaml_vazio))

        assert (
            f"O arquivo '{str(yaml_vazio)}' está vazio ou só contém "
            "comentários." in str(exc.value)
        )

    def test_apenas_comentarios(
        self, leitor: LeitorWorkflow, yaml_apenas_comentarios: Path
    ) -> None:
        """Deve lançar erro quando há apenas comentários no YAML."""
        with pytest.raises(ConfiguracaoInvalidaError) as exc:
            leitor.carregar(str(yaml_apenas_comentarios))

        assert (
            f"O arquivo '{str(yaml_apenas_comentarios)}' está vazio ou só "
            "contém comentários." in str(exc.value)
        )

    def test_raiz_lista(
        self, leitor: LeitorWorkflow, yaml_raiz_lista: Path
    ) -> None:
        """Deve lançar erro quando a raiz do YAML é uma lista."""
        with pytest.raises(ConfiguracaoInvalidaError) as exc:
            leitor.carregar(str(yaml_raiz_lista))

        assert (
            f"Esperado um formato YAML na raiz de '{str(yaml_raiz_lista)}', "
            "recebido: 'list'." in str(exc.value)
        )

    def test_raiz_escalar(
        self, leitor: LeitorWorkflow, yaml_raiz_escalar: Path
    ) -> None:
        """Deve lançar erro quando a raiz do YAML é um escalar."""
        with pytest.raises(ConfiguracaoInvalidaError) as exc:
            leitor.carregar(str(yaml_raiz_escalar))

        assert (
            f"Esperado um formato YAML na raiz de '{str(yaml_raiz_escalar)}', "
            "recebido: 'str'." in str(exc.value)
        )


class TestConstantes:
    """Garante que a configuração da classe está correta."""

    def test_extensoes_validas(self) -> None:
        """Deve expor exatamente as extensões .yaml e .yml."""
        assert len(LeitorWorkflow.EXTENSOES_VALIDAS) == 2
        assert ".yaml" in LeitorWorkflow.EXTENSOES_VALIDAS
        assert ".yaml" in LeitorWorkflow.EXTENSOES_VALIDAS
