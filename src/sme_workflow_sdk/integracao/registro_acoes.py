"""Registro centralizado dos métodos associados às ações do workflow."""

from collections.abc import Callable
from typing import Any

from sme_workflow_sdk.excecoes.integracao import AcaoDuplicadaError

MetodoWorkflow = Callable[..., Any]


class RegistroAcoes:
    """Armazena métodos associados a combinações de estado e ação.

    O registro mantém referências às funções originais, sem criar ou armazenar
    instâncias das classes da aplicação consumidora.
    """

    def __init__(self) -> None:
        """Inicializa um registro vazio de ações."""
        self._acoes: dict[tuple[str, str], MetodoWorkflow] = {}

    def registrar(
        self,
        *,
        estado: str,
        acao: str,
        metodo: MetodoWorkflow,
    ) -> None:
        """Registra um método para uma combinação de estado e ação.

        Args:
            estado (str): _description_
            acao (str): _description_
            metodo (MetodoWorkflow): _description_

        Raises:
            AcaoDuplicadaError: _description_
        """
        chave = (estado, acao)
        metodo_existente = self._acoes.get(chave)

        if metodo_existente is not None:
            if metodo_existente is metodo:
                return

            raise AcaoDuplicadaError(
                f"Já existe um método registrado para o estado "
                f"'{estado}' e a ação '{acao}'."
            )

        self._acoes[chave] = metodo

    def obter(self, *, estado: str, acao: str) -> MetodoWorkflow | None:
        """Retorna o método associado à combinação informada, se existir.

        Args:
            estado (str): _description_
            acao (str): _description_

        Returns:
            MetodoWorkflow | None: _description_
        """
        return self._acoes.get((estado, acao))

    def listar(self) -> dict[tuple[str, str], MetodoWorkflow]:
        """Retorna uma cópia das ações registradas.

        Returns:
            dict[tuple[str, str], MetodoWorkflow]: _description_
        """
        return self._acoes.copy()

    def limpar(self) -> None:
        """Remove todas as associações do registro."""
        self._acoes.clear()


registro_acoes = RegistroAcoes()
