"""Exceções relacionadas à integração declarativa do workflow."""


class AcaoDuplicadaError(Exception):
    """Indica que uma combinação de estado e ação já foi registrada."""


class DeclaracaoWorkflowInvalidaError(ValueError):
    """Indica que os parâmetros declarados no decorator são inválidos."""


class EstadoWorkflowIncompativelError(ValueError):
    """Indica que o estado recebido difere do estado declarado na ação."""
