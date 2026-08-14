from datetime import datetime

from unicodedata import category

from app.api.v1.users import get_current_user
from app.dependency import get_db
from app.models import User
from app.schemas import OperationRequest, OperationResponse
from fastapi import HTTPException, Depends
from app.database import SessionLocal
from app.repository import wallets as wallets_repository
from sqlalchemy.orm import Session, Query
from app.repository import operations as operations_repository

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
        type = 'income',
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
        type = 'expense',
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


