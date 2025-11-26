from enum import Enum


class TransactionType(str, Enum):
    """Tipo de transacción: ingreso o gasto"""
    INCOME = "income"
    EXPENSE = "expense"


class PaymentMethod(str, Enum):
    """Método de pago: efectivo o tarjeta"""
    CASH = "cash"
    CARD = "card"


class PriorityLevel(str, Enum):
    """Nivel de prioridad del recordatorio"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
