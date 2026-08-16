from datetime import datetime
from decimal import Decimal
from app.models import User
from app.schemas import OperationRequest, OperationResponse
from fastapi import HTTPException, Depends, requests
from app.repository import wallets as wallets_repository
from sqlalchemy.orm import Session
from fastapi import Query
from app.repository import operations as operations_repository
from app.enum import OperationType, CurrencyEnum
from app.services.exhange_service import get_exchange_rate, FALLBACK_RATES


def add_income(db: Session, current_user : User,operation: OperationRequest) -> OperationResponse:
    if not wallets_repository.is_wallet_exist(db, current_user.id, operation.wallet_name):
        raise HTTPException(
            status_code=404,
            detail=f'Wallet {operation.wallet_name} not found'
        )
    wallet = wallets_repository.add_income(db, current_user.id, operation.wallet_name, operation.amount)
    operation = operations_repository.create_operation(
        db = db,
        wallet_id = wallet.id,
        type = OperationType.INCOME,
        amount = operation.amount,
        currency=wallet.currency,
        category = operation.description
    )
    db.commit()
    return OperationResponse.model_validate(operation)





def add_expense(db: Session, current_user: User,operation: OperationRequest) -> OperationResponse:
    if not wallets_repository.is_wallet_exist(db, current_user.id, operation.wallet_name):
        raise HTTPException(
            status_code=404,
            detail=f'Wallet {operation.wallet_name} not found'
        )
    wallet = wallets_repository.get_wallet_balance_by_name(db,current_user.id, operation.wallet_name)
    if wallet.balance < operation.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available {wallet.balance}"
        )
    wallet = wallets_repository.add_expense(db, current_user.id, operation.wallet_name, operation.amount)
    operation = operations_repository.create_operation(
        db = db,
        wallet_id = wallet.id,
        type = OperationType.EXPENSE,
        amount = operation.amount,
        currency=wallet.currency,
        category = operation.description
    )
    db.commit()
    return OperationResponse.model_validate(operation)


def get_operations_list(
    db: Session,
    current_user : User,
    wallet_id : int | None = Query(None),
    date_from : datetime | None = Query(None),
    date_to : datetime|None = Query(None),
) -> list[OperationResponse]:
    if wallet_id:
        wallet = wallets_repository.get_wallet_by_id(db, current_user.id, wallet_id)
        if not wallet:
            raise HTTPException(
                status_code = 404,
                detail = f'Wallet {wallet_id} not found'
            )
        wallets_ids = [wallet.id]
    else:
        wallets = wallets_repository.get_all_wallets(db, current_user.id)
        wallets_ids = [w.id for w in wallets]

    operations = operations_repository.get_operations_list(
        db,
        wallets_ids,
        date_from,
        date_to
    )
    result = []
    for operation in operations:
        result.append(OperationResponse.model_validate(operation))
    return result


async def transfer_between_wallets(
        db:Session, user_id: int, from_wallet_id: int, to_wallet_id:int, amount: Decimal
) -> OperationResponse:
    from_wallet = wallets_repository.get_wallet_by_id(db, from_wallet_id, user_id)
    to_wallet = wallets_repository.get_wallet_by_id(db, to_wallet_id, user_id)

    if not from_wallet or not to_wallet:
        raise HTTPException(404, detail=f'Wallet {from_wallet_id} not found')
    if from_wallet.balance < amount:
        raise HTTPException(
            status_code=400,
            detail= f'Not enough money'
        )
    target_amount = amount
    if from_wallet.currency != to_wallet.currency:
        exchange_rate = await get_exchange_rate(
            from_wallet.currency, to_wallet.currency
        )
        target_amount = round(amount*exchange_rate,2)

    from_wallet.balance = round(from_wallet.balance - amount,2)
    to_wallet.balance = round(to_wallet.balance + target_amount,2)
    operation = operations_repository.create_operation(
        db = db,
        wallet_id = from_wallet.id,
        type = OperationType.TRANSFER,
        amount = target_amount,
        currency=from_wallet.currency,
        category='перевод',
    )
    db.add(from_wallet)
    db.add(to_wallet)
    db.add(operation)
    db.commit()
    return OperationResponse.model_validate(operation)