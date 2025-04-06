from datetime import timedelta, datetime
import pytz

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt

from app.core.security import verify_password, get_password_hash
from app.core.config import settings
from app.db.session import get_db
from app.crud.user import get_user_by_username, get_user_by_email
from app.models.user import User
from app.schemas.auth import LoginRequest, OAuth2EmailRequest, Token, TokenResponse

router = APIRouter()
KST = pytz.timezone('Asia/Seoul')

def create_access_token(data: dict, expires_delta: timedelta):
    """JWT 토큰 생성 함수"""
    to_encode = data.copy()
    expire = datetime.now(KST) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    login_data: OAuth2EmailRequest,
    db: Session = Depends(get_db)
):
    """
    사용자 인증 후 JWT 액세스 토큰을 발급하는 API

    요청 본문:
    - email (str): 사용자 이메일
    - password (str): 사용자 비밀번호

    응답 데이터:
    - access_token (str): 인증된 사용자를 위한 JWT 액세스 토큰
    - token_type (str): 토큰 타입 (bearer)

    예외 처리:
    - 잘못된 이메일 또는 비밀번호 입력 시 400 상태 코드와 함께 "Invalid email or password" 오류를 반환
    """        
    user = get_user_by_email(db, email=login_data.email)
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    access_token = create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=timedelta(minutes=30)
    )
    return TokenResponse(access_token=access_token, token_type="bearer")

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: LoginRequest, db: Session = Depends(get_db)):
    """
    사용자 로그인 후 JWT 액세스 토큰을 발급하는 API

    요청 본문:
    - email (str): 사용자 이메일
    - password (str): 사용자 비밀번호

    응답 데이터:
    - access_token (str): 인증된 사용자를 위한 JWT 액세스 토큰
    - token_type (str): 토큰 타입 (bearer)

    예외 처리:
    - 잘못된 사용자명 또는 비밀번호 입력 시 400 상태 코드와 함께 "Incorrect username or password" 오류를 반환
    """ 
    user_token = login_user(db, form_data.username, form_data.password)
    if not user_token:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return user_token