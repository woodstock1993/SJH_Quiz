from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.crud import user as user_crud
from app.crud import quiz as quiz_crud
from app.core.security import get_admin_user, get_current_user

router = APIRouter()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    새로운 사용자를 생성하는 API

    요청 본문:
    - email (str): 사용자 이메일 (고유값)
    - password (str): 사용자 비밀번호
    - name (str): 사용자 이름
    - is_active (boolean): 활성 상태,
    - is_superuser(boolean): 관리자 권한

    응답 데이터:
    - id (int): 사용자 ID
    - email (str): 사용자 이메일
    - name (str): 사용자 이름
    - is_active (boolean): 활성 상태
    - is_superuser(boolean): 관리자 권한 

    예외 처리:
    - 중복된 이메일 입력 시 400 상태 코드와 함께 "이미 존재하는 이메일입니다." 오류를 반환합니다.
    """    
    user = user_crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 이메일입니다."
        )
    return user_crud.create_user(db=db, user_in=user_in)

@router.get("/", response_model=List[UserRead])
def get_users(
        page: int = Query(0, alias="page"),
        page_size: int = Query(10, alias="page_size"),
        db: Session = Depends(get_db),
        current_user = Depends(get_admin_user)
    ):
    """
    전체 사용자 목록을 조회하는 API

    요청 쿼리 파라미터:
    - page (int, 기본값: 0): 조회할 페이지 번호
    - page_size (int, 기본값: 10): 한 페이지에 포함될 사용자 수

    응답 데이터:
    - id (int): 사용자 ID
    - email (str): 사용자 이메일
    - name (str): 사용자 이름
    - is_active (boolean): 활성 상태
    - is_superuser(boolean): 관리자 권한

    인증 필요:
    - 관리자 계정만 접근 가능
    """
    users = user_crud.get_users(db, page=page, page_size=page_size)
    return users

@router.get("/{user_id}", response_model=UserRead)
def get_user(
        user_id: int, 
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
    """
    특정 사용자 정보를 조회하는 API

    요청 경로 파라미터:
    - user_id (int): 조회할 사용자의 ID

    응답 데이터:
    - id (int): 사용자 ID
    - email (str): 사용자 이메일
    - name (str): 사용자 이름
    - is_active (boolean): 활성 상태
    - is_superuser(boolean): 관리자 권한

    예외 처리:
    - 사용자가 존재하지 않을 경우 404 상태 코드 반환


    인증 필요:
    - 관리자 또는 사용자 계정만 접근 가능
    """    
    user = user_crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    return user

@router.get("/{user_id}/quizzes/", response_model=list)
def get_user_quiz_statuses(
    user_id: int,     
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return quiz_crud.read_user_quiz_statuses(db, user_id)


@router.put("/{user_id}", response_model=UserRead)
def update_user(    
    user_id: int, 
    user_in: UserUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    특정 사용자의 정보를 수정하는 API

    요청 경로 파라미터:
    - user_id (int): 수정할 사용자의 ID

    요청 본문:
    - email (str): 사용자 이메일
    - name (str): 사용자 이름
    - is_active (boolean): 활성 상태
    - is_superuser(boolean): 관리자 권한

    응답 데이터:
    - id (int): 사용자 ID
    - email (str): 사용자 이메일
    - name (str): 사용자 이름
    - is_active (boolean): 활성 상태
    - is_superuser(boolean): 관리자 권한

    예외 처리:
    - 사용자가 존재하지 않을 경우 404 상태 코드 반환

    인증 필요:
    - 관리자 계정만 접근 가능
    """    
    user = user_crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    user = user_crud.update_user(db=db, db_user=user, user_in=user_in)
    return user