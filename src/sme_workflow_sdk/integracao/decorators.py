"""Decorators para declarar ações associadas aos estados do workflow."""

from collections.abc import Callable
from functools import wraps
from typing import Any, cast

from sme_workflow_sdk.excecoes.integracao import (
    DeclaracaoWorkflowInvalidaError,
    EstadoWorkflowIncompativelError,
)
from sme_workflow_sdk.integracao.registro_acoes import registro_acoes


def workflow[Retorno](
    *, estado: str, acao: str
) -> Callable[[Callable[..., Retorno]], Callable[..., Retorno]]:
    """Associa um método da aplicação consumidora a um estado e uma ação.

    Ao ser chamado, o método decorado exige o estado atual da entidade, compara
    esse estado com o declarado e valida a transição por meio do motor
    configurado no runtime. Somente após a validação bem-sucedida a
    implementação original é executada.

    O argumento ``estado`` é consumido pelo decorator e não é repassado ao
    método original.

    O método original é armazenado no registro centralizado para permitir que
    o SDK localize a implementação associada à combinação de estado e ação,
    sem instanciar classes da aplicação consumidora.

    A validação de duplicidade é realizada pelo :class:`RegistroAcoes
    <sme_workflow_sdk.integracao.registro_acoes.RegistroAcoes>`.

    Args:
        estado (str): Nome do estado do workflow ao qual o método será
            associado.
        acao (str): Nome da ação do workflow executada pelo método.

    Raises:
        DeclaracaoWorkflowInvalidaError: e o estado ou a ação não forem
            strings não vazias ou se o objeto decorado não for chamável.
        AcaoDuplicadaError: Se já existir outro método registrado para
            a mesma combinação de estado e ação.
        EstadoWorkflowIncompativelError: Se o estado recebido na chamada for
            diferente do estado declarado no decorator.

    Returns:
        Callable[..., Retorno]: Um decorator que registra o método e retorna
        uma função que valida a transição antes de executar o método original.

    Example:
        ```python
        class SolicitacaoService:
            @workflow(estado="pendente", acao="aprovar")
            def aprovar(self, solicitacao, usuario):
                # Regras de negócio da aplicação consumidora.
                return solicitacao
        ```

        A chamada do método exige o estado atual:

        ```python
        resultado = servico.aprovar(
            estado=solicitacao.status,
            solicitacao=solicitacao,
            usuario=usuario,
        )
        ```
    """
    if not isinstance(estado, str) or not estado.strip():
        raise DeclaracaoWorkflowInvalidaError(
            "O parâmetro 'estado' deve ser uma string não vazia."
        )

    if not isinstance(acao, str) or not acao.strip():
        raise DeclaracaoWorkflowInvalidaError(
            "O parâmetro 'acao' deve ser uma string não vazia."
        )

    estado_declarado = estado

    def decorator(metodo: Callable[..., Retorno]) -> Callable[..., Retorno]:
        """Registra o método e cria o wrapper de validação.

        O método original é armazenado no registro centralizado. Em seguida,
        é criado um wrapper que intercepta as chamadas, obtém o motor
        configurado e valida a transição antes de executar a implementação
        original.

        Args:
            metodo (Callable[..., Retorno]): Função ou método da aplicação
                consumidora associado ao estado e à ação declarados.

        Raises:
            DeclaracaoWorkflowInvalidaError: Se o objeto recebido não for
                chamável.
            EstadoWorkflowIncompativelError: Se outro método já estiver
                registrado para a mesma combinação de estado e ação.

        Returns:
            Callable[..., Retorno]:  Um wrapper que preserva os metadados do
            método original e realiza a validação da transição antes de sua
            execução.
        """
        if not callable(metodo):
            raise DeclaracaoWorkflowInvalidaError(
                "O decorator @workflow deve ser aplicado a um método ou "
                "função."
            )

        registro_acoes.registrar(
            estado=estado,
            acao=acao,
            metodo=cast(Callable[..., Any], metodo),
        )

        @wraps(metodo)
        def wrapper(
            *args: Any,
            estado: str,
            **kwargs: Any,
        ) -> Retorno:
            """Valida a transição e executa o método original.

            O estado recebido é comparado com o estado declarado no decorator.
            Em seguida, o motor configurado no runtime valida se a ação está
            permitida conforme a configuração do workflow.

            O argumento ``estado`` não é repassado ao método original.
            Os demais argumentos posicionais e nomeados são preservados.

            Args:
                *args: (Any): Argumentos posicionais destinados ao método
                    original.
                estado (str):  Estado atual da entidade que será validada.
                **kwargs (Any): Argumentos nomeados destinados ao método
                    original.

            Raises:
                EstadoWorkflowIncompativelError: Se o estado recebido
                    for diferente do estado declarado no decorator.

            Returns:
                Retorno: O resultado produzido pela execução do método
                    original.
            """
            if estado != estado_declarado:
                raise EstadoWorkflowIncompativelError(
                    f"A ação '{acao}' foi declarada para o estado "
                    f"'{estado_declarado}', mas recebeu o estado "
                    f"'{estado}'."
                )
            return metodo(*args, **kwargs)

        return wrapper

    return decorator
