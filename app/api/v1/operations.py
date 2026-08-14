from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_db, get_current_user
from app.models import User
from app.schemas import OperationRequest
from app.services import operations as operations_services

router = APIRouter()

@router.post('/operations/income')
def add_income(operation: OperationRequest, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    return operations_services.add_income(db, current_user, operation)

@router.post('/operations/expense')
def add_expense (operation: OperationRequest, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    return operations_services.add_expense(db,current_user, operation)