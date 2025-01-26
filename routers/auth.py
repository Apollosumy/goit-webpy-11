from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, Token, VerifyEmail, PasswordResetRequest, PasswordResetConfirm, AvatarUploadResponse
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
import redis
import cloudinary.uploader

# Ініціалізація Redis
redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)

# Налаштування bcrypt для хешування паролів
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

class Settings(BaseModel):
    authjwt_secret_key: str = "your_secret_key"

@AuthJWT.load_config
def get_config():
    return Settings()

# Реєстрація
@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = Authorize.create_access_token(subject=new_user.id)
    refresh_token = Authorize.create_refresh_token(subject=new_user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}

# Логін
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = Authorize.create_access_token(subject=user.id)
    refresh_token = Authorize.create_refresh_token(subject=user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}

# Верифікація email
@router.post("/verify-email")
def verify_email(data: VerifyEmail, db: Session = Depends(get_db)):
    user_id = redis_client.get(data.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    db.commit()
    redis_client.delete(data.token)
    return {"message": "Email verified successfully"}

# Скидання паролю - запит
@router.post("/reset-password/request")
def request_password_reset(data: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = "some_unique_token"
    redis_client.setex(token, 3600, user.id)
    return {"message": "Password reset email sent"}

# Скидання паролю - підтвердження
@router.post("/reset-password/confirm")
def confirm_password_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    user_id = redis_client.get(data.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = pwd_context.hash(data.new_password)
    db.commit()
    redis_client.delete(data.token)
    return {"message": "Password reset successful"}

# Завантаження аватара
@router.post("/upload-avatar", response_model=AvatarUploadResponse)
def upload_avatar(file: UploadFile = File(...), db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_identity()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    upload_result = cloudinary.uploader.upload(file.file, folder="avatars")
    user.avatar_url = upload_result["secure_url"]
    db.commit()
    return {"avatar_url": user.avatar_url}
