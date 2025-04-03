from sqlalchemy.orm import Session
from models.user import User
from core.security import verify_password, create_access_token
from datetime import timedelta

from app.core.config import settings

def authenticate_user(db: Session, name: str, password: str):
    user = db.query(User).filter(User.name == name).first()
    if not user or not verify_password(password, user.password):
        return None
    return user

def login_user(db: Session, name: str, password: str):
    user = authenticate_user(db, name, password)
    if not user:
        return None
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}
