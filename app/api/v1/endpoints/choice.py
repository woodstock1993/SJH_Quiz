from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.choice import ChoiceCreate, ChoiceUpdate, ChoiceResponse
from app.core.security import get_current_user, get_admin_user
from app.crud.choice import create_choice, get_choice, get_choices_by_question, update_choice, delete_choice
from app.db.session import get_db
from app.models import User

router = APIRouter()

@router.post("/", response_model=ChoiceResponse)
def create_choice_endpoint(
        choice: ChoiceCreate, 
        db: Session = Depends(get_db),
        current_user: User = Depends(get_admin_user),
    ):
    """
    문제에 대한 선택지를 생성하는 API

    요청 본문:
    - question_id (int): 선택지가 속한 문제 ID
    - text (str): 선택지 내용
    - is_correct (bool): 해당 선택지가 정답인지 여부

    응답 데이터:
    - id (int): 생성된 선택지의 고유 ID
    - question_id (int): 해당 선택지가 속한 문제 ID
    - text (str): 선택지 내용
    - is_correct (bool): 정답 여부

    예외 처리:
    - 유효하지 않은 문제 ID일 경우 적절한 예외 처리 필요

    인증 필요:
    - 관리자 계정만 접근 가능
    """
    return create_choice(db=db, choice=choice)

@router.get("/{choice_id}", response_model=ChoiceResponse)
def get_choice_endpoint(
        choice_id: int, 
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
    """
    특정 선택지를 조회하는 API

    요청 경로 매개변수:
    - choice_id (int): 조회할 선택지의 고유 ID

    응답 데이터:
    - id (int): 선택지의 고유 ID
    - question_id (int): 해당 선택지가 속한 문제 ID
    - text (str): 선택지 내용
    - is_correct (bool): 정답 여부

    예외 처리:
    - 선택지가 존재하지 않으면 404 오류 반환

    인증 필요:
    - 관리자 또는 사용자계정만 접근 가능
    """
    choice = get_choice(db=db, choice_id=choice_id)
    if not choice:
        raise HTTPException(status_code=404, detail="Choice not found")
    return choice

@router.get("/question/{question_id}", response_model=list[ChoiceResponse])
def get_choices_by_question_endpoint(
        question_id: int, 
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
    """
    특정 문제에 속한 선택지를 조회하는 API

    요청 경로 매개변수:
    - question_id (int): 선택지를 조회할 문제 고유 ID

    응답 데이터:
    - 선택지 리스트 (list):
        - id (int): 선택지의 고유 ID
        - question_id (int): 해당 선택지가 속한 문제 ID
        - text (str): 선택지 내용
        - is_correct (bool): 정답 여부

    예외 처리:
    - 해당 문제에 속한 선택지가 존재하지 않으면 404 오류 반환

    인증 필요:
    - 관리자 또는 사용자계정만 접근 가능    
    """    
    choices = get_choices_by_question(db, question_id)
    if not choices:
        raise HTTPException(status_code=404, detail="No choices found for this question")
    return choices

@router.put("/{choice_id}", response_model=ChoiceResponse)
def update_choice_endpoint(
        choice_id: int, 
        choice: ChoiceUpdate, 
        db: Session = Depends(get_db),
        current_user: User = Depends(get_admin_user),
    ):
    """
    선택지 수정 API

    요청 경로 매개변수:
    - choice_id (int): 수정할 선택지 고유 ID

    요청 본문:
    - text (str): 변경할 선택지 내용
    - is_correct (bool): 정답 여부 변경

    응답 데이터:
    - id (int): 선택지 고유 ID
    - question_id (int): 해당 선택지가 속한 문제 ID
    - text (str): 선택지 내용
    - is_correct (bool): 정답 여부

    예외 처리:
    - 선택지가 존재하지 않으면 404 오류 반환

    인증 필요:
    - 관리자 또는 사용자계정만 접근 가능
    """    
    return update_choice(db=db, choice_id=choice_id, choice=choice)

@router.delete("/{choice_id}")
def delete_choice_endpoint(
        choice_id: int, 
        db: Session = Depends(get_db),
        current_user: User = Depends(get_admin_user)
    ):
    """
    선택지 삭제 API

    요청 경로 매개변수:
    - choice_id (int): 삭제할 선택지 고유 ID

    응답 데이터:
    - {"message": "Choice deleted successfully"}: 성공적으로 삭제된 경우 반환

    예외 처리:
    - 선택지가 존재하지 않으면 404 오류 반환

    인증 필요:
    - 관리자 또는 사용자계정만 접근 가능
    """    
    delete_choice(db=db, choice_id=choice_id)
    return {"message": "Choice deleted successfully"}
