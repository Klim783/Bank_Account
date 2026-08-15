from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependency import get_db, get_current_user
from app.models import User
from app.schemas import OperationRequest, OperationResponse, TransferCreateSchema
from app.services import operations as operations_services

router = APIRouter()

@router.post('/operations/income', response_model= OperationResponse)
def add_income(operation: OperationRequest, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    return operations_services.add_income(db, current_user, operation)

@router.post('/operations/expense', response_model = OperationResponse)
def add_expense (operation: OperationRequest, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    return operations_services.add_expense(db,current_user, operation)


@router.get('/operations', response_model=list[OperationResponse])
def get_operations_list(
    wallet_id : int | None = Query(None),
    date_from : datetime | None = Query(None),
    date_to : datetime|None = Query(None),
    user : User = Depends(get_current_user),
    db : Session = Depends(get_db),
):
    return operations_services.get_operations_list(db, user, wallet_id, date_from, date_to)


@router.post('/operations/transfer', response_model=OperationResponse)
async def create_transfer(
    payload:TransferCreateSchema,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await operations_services.transfer_between_wallets(
        db,
        user.id,
        payload.from_wallet_id,
        payload.to_wallet_id,
        payload.amount,
    )

