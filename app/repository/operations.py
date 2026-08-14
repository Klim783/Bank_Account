from decimal import Decimal

from sqlalchemy.orm import Session

from app.enum import CurrencyEnum
from app.models import Operation


def create_operation(
	db: Session,
	wallet_id: int,
	type: str,
	amount: Decimal,
	currency: CurrencyEnum,
	category: str | None = None,
	subcategory: str | None = None
) -> Operation:
	operation = Operation(
		wallet_id = wallet_id,
		type = type,
		amount = amount,
		currency = currency,
		category = category,
		subcategory = subcategory
	)
	db.add(operation)
	db.flush()
	return operation
