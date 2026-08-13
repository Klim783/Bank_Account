from fastapi import APIRouter, HTTPException, status

from app.schemas import OperationRequest

router = APIRouter()

BALANCE = {}

@router.post('/operations/income')
def add_income(operation: OperationRequest):
    if operation.wallet_name not in BALANCE:
        raise HTTPException(
            status_code = 404,
            detail = f'Wallet {operation.wallet_name} not found'
        )
    BALANCE[operation.wallet_name] += operation.amount
    return{
        'message' : 'Income added',
        'wallet' : operation.wallet_name,
        'balance' : operation.amount,
        'description' : operation.description,
        'new_balance': BALANCE[operation.wallet_name]
    }

@router.post('/operations/expense')
def add_expense (operation: OperationRequest):
    if operation.wallet_name not in BALANCE:
        raise HTTPException(
            status_code = 404,
            detail = f'Wallet {operation.wallet_name} not found'
        )
    if BALANCE[operation.wallet_name] < operation.amount:
        raise HTTPException(
            status_code = 400,
            detail = f"Insufficient funds. Available {BALANCE[operation.wallet_name]}"
        )
    BALANCE[operation.wallet_name] -= operation.amount
    return{
        'message' : 'Expense added',
        'wallet' : operation.wallet_name,
        'balance' : operation.amount,
        'description' : operation.description,
        'new_balance': BALANCE[operation.wallet_name]
    }