from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.dependency import get_db
from app.schemas import OperationRequest
from app.services import operations as operations_services

router = APIRouter()

@router.post('/operations/income')
def add_income(operation: OperationRequest, db: Session = Depends(get_db)):
    return operations_services.add_income(operation)

@router.post('/operations/expense')
def add_expense (operation: OperationRequest, db: Session = Depends(get_db)):
    return operations_services.add_expense(operation)