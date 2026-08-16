from sqlalchemy.orm import Session
from app.repository import users as users_repository
from app.schemas import UserResponse, TokenResponse
from app.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException


def create_user(db: Session, login: str, password: str) -> UserResponse:
    if users_repository.get_user(db, login):
        raise HTTPException(status_code=400, detail='User already exists')
    user = users_repository.create_user(db, login, hash_password(password))
    return UserResponse.model_validate(user)


def login(db: Session, login: str, password: str) -> TokenResponse:
    user = users_repository.get_user(db, login)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid login or password')
    token = create_access_token(user.login)
    return TokenResponse(access_token=token)