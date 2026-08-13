from fastapi import APIRouter

from app.schemas import OperationRequest
from app.services import operations as operations_services

router = APIRouter()

@router.post('/operations/income')
def add_income(operation: OperationRequest):
    return operations_services.add_income(operation)

@router.post('/operations/expense')
def add_expense (operation: OperationRequest):
    return operations_services.add_expense(operation)