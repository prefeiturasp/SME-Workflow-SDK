"""Disponibiliza funções genéricas para validação de dados do domínio.

Este módulo reúne funções reutilizáveis para validar tipos, strings,
valores booleanos, mapeamentos e identificadores utilizados pelas
entidades do workflow.

As funções centralizam as regras básicas de validação e lançam
ValidacaoDominioError quando os valores informados não atendem
aos critérios estabelecidos.
"""

import re
from collections.abc import Mapping
from typing import Any

from sme_workflow_sdk.excecoes import ValidacaoDominioError


def validar_tipo(
    valor: Any,
    tipo_esperado: type | tuple[type, ...],
    nome_campo: str,
) -> None:
    """Valida se um valor corresponde a um dos tipos esperados.

    Utiliza isinstance() para verificar se o valor pertence ao tipo
    informado ou a uma tupla de tipos aceitos

    Args:
        valor (Any): Valor que será validado.
        tipo_esperado (type | tuple[type, ...]): Tipo ou tupla de tipos
            aceitos.
        nome_campo (str): Nome do campo usado na mensagem de erro.

    Raises:
        ValidacaoDominioError: Se o valor não corresponder a nenhum
            dos tipos esperados.
    """
    if not isinstance(valor, tipo_esperado):
        if isinstance(tipo_esperado, tuple):
            nome_tipo = " | ".join(tipo.__name__ for tipo in tipo_esperado)
        else:
            nome_tipo = tipo_esperado.__name__
        raise ValidacaoDominioError(
            f"{nome_campo} deve ser {nome_tipo}, recebido "
            f"{type(valor).__name__}"
        )


def validar_string_nao_vazia(valor: Any, nome_campo: str) -> None:
    """Valida se um valor é uma string não vazia.

    Considera inválidas strings vazias ou compostas exclusivamente
    por espaços em branco. A função não remove os espaços do valor
    original.

    Args:
        valor (Any): Valor que será validado.
        nome_campo (str): Nome do campo usado na mensagem de erro.

    Raises:
        ValidacaoDominioError: Se o valor não for uma string ou estiver vazio
            após a remoção de espaços.
    """
    validar_tipo(valor, str, nome_campo)
    if not valor.strip():
        raise ValidacaoDominioError(f"{nome_campo} não pode ser vazio")


def validar_booleano(valor: Any, nome_campo: str) -> None:
    """Valida se um valor é estritamente do tipo bool.

    Não aceita valores de outros tipos, incluindo inteiros como 0 e 1,
    mesmo que possam ser utilizados como booleanos em expressões Python.

    Args:
        valor (Any): Valor que será validado.
        nome_campo (str): Nome do campo usado na mensagem de erro.

    Raises:
        ValidacaoDominioError: Se o valor não for bool.
    """
    if not isinstance(valor, bool):
        raise ValidacaoDominioError(
            f"{nome_campo} deve ser bool, recebido {type(valor).__name__}"
        )


def validar_mapping(
    valor: Any,
    nome_campo: str,
    *,
    permitir_none: bool = False,
) -> None:
    """Valida se um valor implementa a interface Mapping.

    Verifica se o valor implementa collections.abc.Mapping.
    Quando permitir_none é True, o valor None também é aceito.

    Args:
        valor (Any): Valor que será validado.
        nome_campo (str): Nome do campo usado na mensagem de erro.
        permitir_none (bool, optional): Define se None também é aceito. O
            padrão é False.

    Raises:
        ValidacaoDominioError: Se o valor não implementar Mapping
            e None não for permitido.
    """
    if valor is None and permitir_none:
        return

    if valor is None:
        raise ValidacaoDominioError(
            f"{nome_campo} não pode ser None; use '{{}}' para vazio"
        )
    if not isinstance(valor, Mapping):
        esperado = "Mapping | None" if permitir_none else "Mapping"
        raise ValidacaoDominioError(
            f"{nome_campo} deve ser {esperado}, recebido "
            f"{type(valor).__name__}"
        )


def validar_identificador(valor: str, nome_campo: str) -> None:
    """Valida o formato de um identificador de estado ou ação.

    Aceita somente letras ASCII, com palavras separadas por
    sublinhados. Cada palavra deve conter pelo menos uma letra.

    Não são permitidos números, espaços, hífens, caracteres acentuados,
    sublinhados no início ou no fim, nem sublinhados consecutivos.

    Exemplos de identificadores válidos:
        - ``pendente``
        - ``em_execucao``
        - ``aguardando_aprovacao``

    Exemplos de identificadores inválidos:
        - ``em-execucao``: contém hífen.
        - ``estado2``: contém número.
        - ``em execução``: contém espaço.
        - ``em_execução``: contém caractere acentuado.

    Args:
        valor (str): Nome do estado ou da ação a ser validado.
        nome_campo (str): Nome do campo usado na mensagem de erro.

    Raises:
        ValidacaoDominioError: Se o identificador não respeitar
            o padrão definido pelo domínio.
    """
    identificador = re.compile(r"[A-Za-z]+(?:_[A-Za-z]+)*")
    if not identificador.fullmatch(valor):
        raise ValidacaoDominioError(
            f"{nome_campo} inválido ('{valor}'). O valor deve conter apenas "
            "letras e sublinhados ('_') entre palavras (ex.: 'em_execucao'). "
            "Não são permitidos sublinhados no início, no fim ou duplicados."
        )
