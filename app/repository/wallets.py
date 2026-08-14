from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from app.enum import CurrencyEnum
from app.models import Wallet, User
from decimal import Decimal

def is_wallet_exist(db: Session,user_id : int, wallet_name: str) -> bool:
    return db.query(Wallet).filter( Wallet.user_id == user_id, Wallet.name == wallet_name).first() is not None


def add_income(db: Session,user_id: int, wallet_name: str, amount: Decimal) -> Wallet | None:
    wallet = db.query(Wallet).filter(Wallet.name == wallet_name, Wallet.user_id == user_id).first()
    if wallet:
        wallet.balance += amount
        db.commit()
    return wallet


def get_wallet_balance_by_name(db: Session, user_id, wallet_name: str) -> Wallet | None:
    return db.query(Wallet).filter(Wallet.name == wallet_name, Wallet.user_id == user_id).first()


def add_expense(db: Session, user_id : int,  wallet_name: str, amount: Decimal) -> Wallet | None:
    wallet = db.query(Wallet).filter(Wallet.name == wallet_name, Wallet.user_id == user_id).first()
    if wallet:
        wallet.balance -= amount
        db.commit()
    return wallet


def get_all_wallets(db: Session, user_id : int) -> list[type[Wallet]]:
    return db.query(Wallet).filter(Wallet.user_id == user_id).all()

def create_wallet(db: Session, user_id : int, wallet_name: str, amount: float, currency : CurrencyEnum) -> Wallet:
    wallet = Wallet(name=wallet_name, balance=amount, user_id = user_id, currency = currency)
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet

def get_wallet_by_id(db:Session, user_id : int, wallet_id : int)-> Wallet | None:
    return db.query(Wallet).filter(Wallet.id == wallet_id, Wallet.user_id == user_id).scalar()