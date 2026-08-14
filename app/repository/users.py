from sqlalchemy.orm import Session
from app.models import User

def get_user(db:Session, login:str) -> User:
	return db.query(User).filter(User.login == login).first()


def create_user(db:Session, login:str) -> User:
	user = User()
	db.add(user)
	db.flush()

