from enum import auto, StrEnum


class CurrencyEnum(StrEnum):
	RUB = auto()
	USD = auto()
	EUR = auto()

class OperationResponse(StrEnum):
	EXPENSE = auto()
	INCOME = auto()
	TRANSFER = auto()