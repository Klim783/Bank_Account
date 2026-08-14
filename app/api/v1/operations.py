from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, Query

from app.dependency import get_db, get_current_user
from app.models import User
from app.schemas import OperationRequest, OperationResponse
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
    wallet_di : int | None = Query(None),
    date_from : datetime | None = Query(None),
    date_to : datetime|None = Query(None),
    user : User = Depends(get_current_user),
    db : Session = Depends(get_db),
):
