from sqlalchemy.orm import Session
from app.models import User

def get_user(db: Session, login: str) -> User | None:
    return db.query(User).filter(User.login == login).first()


def create_user(db: Session, login: str, hashed_password:str) -> User:
    user = User(login=login, hashed_password = hashed_password)  # 1. Передаем login
    db.add(user)
    db.commit()               # 2. Фиксируем в БД
    db.refresh(user)          # 3. Обновляем объект (получаем id из БД)
    return user