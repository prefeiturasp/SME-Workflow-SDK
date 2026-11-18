"""Exceções relacionadas à integração declarativa do workflow."""


class AcaoDuplicadaError(Exception):
    """Indica que uma combinação de estado e ação já foi registrada."""
