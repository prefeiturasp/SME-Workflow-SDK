"""Funções genéricas para validação de dados do domínio."""

import re
from collections.abc import Mapping
from typing import Any

from sme_workflow_sdk.excecoes import ValidacaoDominioError


def validar_tipo(
    valor: Any,
    tipo_esperado: type | tuple[type, ...],
    nome_campo: str,
) -> None:
    """Valida se um valor corresponde ao tipo esperado.

    Args:
        valor (Any): Valor que será validado.
        tipo_esperado (type | tuple[type, ...]): Tipo ou tupla de tipos
            aceitos.
        nome_campo (str): Nome do campo usado na mensagem de erro.

    Raises:
        ValidacaoDominioError: Se o valor não corresponder a nenhum dos tipos
            esperados. A causa original será um TypeError.
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
    """Valida se um valor é uma string não vazia ou composta por espaços.

    Args:
        valor (Any): Valor que será validado.
        nome_campo (str): Nome do campo usado na mensagem de erro.

    Raises:
        ValidacaoDominioError: e o valor não for uma string ou estiver vazio
            após a remoção de espaços.
    """
    validar_tipo(valor, str, nome_campo)
    if not valor.strip():
        raise ValidacaoDominioError(f"{nome_campo} não pode ser vazio")


def validar_booleano(valor: Any, nome_campo: str) -> None:
    """Valida se um valor é estritamente do tipo bool.

    Valores inteiros como 0 e 1 não são aceitos, mesmo que possam ser
    utilizados como booleanos em algumas expressões Python.

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
    """Valida se um valor implementa Mapping.

    Args:
        valor (Any): Valor que será validado.
        nome_campo (str): Nome do campo usado na mensagem de erro.
        permitir_none (bool, optional): Define se None também é aceito. O
            padrão é False.

    Raises:
        ValidacaoDominioError: Se o valor não implementar Mapping e não
            for None em um campo que permita esse valor.
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
    """Garante que o valor contém apenas letras e underscore.

    Aceita strings compostas por letras, usando ``_`` **apenas entre
    palavras**. O underscore não pode iniciar, terminar, aparecer
    duplicado nem ser o único caractere.

    Não são permitidos números, espaços, hífens, acentos ou quaisquer
    símbolos.

    Exemplos:
        Aceitos: ``"em_execucao"``, ``"abc_def"``, ``"Acao"``, ``"a"``.
        Rejeitados: ``"_"``, ``"_privado"``, ``"abc_"``, ``"A_"``,
        ``"a__b"``, ``"123abc"``, ``"abc1"``, ``"1.5"``, ``"abc-def"``,
        ``"abc def"``, ``"execução"``.


    Args:
        valor (str): Valor já validado como string não vazia.
        nome_campo (str): Nome do campo usado na mensagem de erro.

    Raises:
        ValidacaoDominioError: Se o valor contiver caracteres fora de
            ``[A-Za-z_]``, ou se o ``_`` não estiver entre palavras.
    """
    identificador = re.compile(r"[A-Za-z]+(?:_[A-Za-z]+)*")
    if not identificador.fullmatch(valor):
        raise ValidacaoDominioError(
            f"{nome_campo} inválido ('{valor}'). O valor deve conter apenas "
            "letras e sublinhados ('_') entre palavras (ex.: 'em_execucao'). "
            "Não são permitidos sublinhados no início, no fim ou duplicados."
        )
