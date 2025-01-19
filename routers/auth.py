from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, Token
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

# Налаштування bcrypt для хешування паролів
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

# Налаштування JWT
class Settings(BaseModel):
    authjwt_secret_key: str = "your_secret_key"  # Замініть на ваш власний секретний ключ

@AuthJWT.load_config
def get_config():
    return Settings()

# Реєстрація користувача
@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    # Перевірка, чи існує користувач із таким email
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    
    # Хешування пароля
    hashed_password = pwd_context.hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Генерація токенів
    access_token = Authorize.create_access_token(subject=new_user.id)
    refresh_token = Authorize.create_refresh_token(subject=new_user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}

# Логін користувача
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Генерація токенів
    access_token = Authorize.create_access_token(subject=user.id)
    refresh_token = Authorize.create_refresh_token(subject=user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}
