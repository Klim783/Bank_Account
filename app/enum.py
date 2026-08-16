from enum import Enum

class CurrencyEnum(str, Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"

class OperationType(str, Enum):
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"
    TRANSFER = "TRANSFER"