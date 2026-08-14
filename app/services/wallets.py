from fastapi import HTTPException

from app.schemas import CreateWalletRequest
from app.repository import wallets as wallets_repository
from sqlalchemy.orm import Session


def get_balance(db: Session, wallet_name: str | None = None):
    if wallet_name is None:
        wallets = wallets_repository.get_all_wallets(db)
        return {'total_balance': sum([w.amount for w in wallets])}
    if not wallets_repository.is_wallet_exist(db, wallet_name):
        raise HTTPException(status_code=404, detail=f'Wallet {wallet_name} not found')
    wallet = wallets_repository.get_wallet_balance_by_name(db, wallet_name)
    db.commit()
    return {'wallet': wallet.name, 'balance': wallet.balance}



def create_wallet(db: Session, wallet : CreateWalletRequest):
    if wallets_repository.is_wallet_exist(db, wallet.name):
        raise HTTPException(status_code=400, detail=f'Wallet {wallet.name} already exists')
    wallet = wallets_repository.create_wallet(db, wallet.name, wallet.initial_balance)
    db.commit()
    return {
        'message': f'Wallet {wallet.name} created',
        'wallet': wallet.name,
        'balance': wallet.balance
    }
