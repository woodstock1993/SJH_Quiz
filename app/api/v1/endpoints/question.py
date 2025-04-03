from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user, get_admin_user
from app.db.session import get_db
from app.models.question import Question
from app.models.choice import Choice
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse
from app.schemas.choice import ChoiceCreate, ChoiceUpdate

router = APIRouter()

@router.post("/", response_model=dict)
def create_question(
        question_data: QuestionCreate, 
        db: Session = Depends(get_db),
        current_user: User = Depends(get_admin_user)
    ):
    """
    새로운 문제를 생성하는 API.

    요청 본문:
    - id (int): 퀴즈 ID
    - text (Optional[str]): 퀴즈 제목    

    인증 필요:
    - 관리자 계정만 접근 가능

    응답 데이터:
    - id (int): 생성한 퀴즈 ID
    - message (str): Question created successfully
    """    
    new_question = Question(
        text=question_data.text,
        quiz_id=question_data.quiz_id
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return {"message": "Question created successfully", "question_id": new_question.id}

@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(
        question_id: int, 
        db: Session = Depends(get_db),
        current_user: User = Depends(get_admin_user),
    ):
    """
    특정 문제를 조회하는 API.

    요청 경로 파라미터:
    - quiz_id (int): 조회할 퀴즈의 고유 ID

    - 응답 데이터:
        -  text: "문제 내용",
        -  id: 문제 ID,
        -  quiz_id: 문제가 속한 퀴즈 ID,
        -  order: 문제 순번
    
    - 404 오류: 해당 문제를 찾을 수 없는 경우.

    - 인증 필요:
        - 관리자 계정만 접근 가능
    """    
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.get("/{quiz_id}/questions", response_model=List[QuestionResponse])
def get_questions_by_quiz(
        quiz_id: int, 
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
    """
    주어진 퀴즈 ID(quiz_id)에 속한 문제 목록을 반환

    - 요청 경로 파라미터:
        - quiz_id (int): 조회할 퀴즈의 고유 ID

    - 응답 데이터(1):
        -  text: "문제 내용",
        -  id: 문제 ID,
        -  quiz_id: 문제가 속한 퀴즈 ID,
        -  order: 문제 순번

    - 응답 데이터(2):
        - 빈 리스트: 해당 퀴즈에 등록된 문제가 없는 경우

    - 인증 필요:
        - 관리자 또는 사용자 계정만 접근 가능
    """    
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    return questions

@router.put("/{question_id}", response_model=dict)
def update_question(
        question_id: int, 
        question_data: QuestionUpdate, 
        db: Session = Depends(get_db),
        current_user: User = Depends(get_admin_user)
    ):
    """
    특정 문제를 수정하는 API

    요청 경로 파라미터:
    - question_id (int): 수정할 문제 ID.

    요청 본문:
    - question_data : 수정할 문제 데이터.
    
    응답 데이터:
    - dict: 수정 성공 메시지.
    - {
        "message": "Question updated successfully"
      }

    예외:
    - HTTP 404: 해당 ID의 문제가 존재하지 않을 경우.

    인증 필요:
    - 관리자 계정만 접근 가능
    """        
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    for key, value in question_data.dict(exclude_unset=True).items():
        if key == "choices":
            continue

        setattr(question, key, value)

    db.commit()
    db.refresh(question)
    return {"message": "Question updated successfully"}

@router.delete("/{question_id}", response_model=dict)
def delete_question(
        question_id: int, 
        db: Session = Depends(get_db),
        current_user: User = Depends(get_admin_user)
    ):
    """
    특정 문제 및 문제와 관련된 선택지를 삭제하는 API

    - 요청 경로 파라미터:
    - question_id (int): 삭제할 문제 ID

    반환값:
    - dict: 삭제 성공 메시지.
    -  {
        "message": "Question and related choices deleted successfully"
      }

    예외:
    - HTTP 404: 해당 ID의 문제가 존재하지 않을 경우

    - 인증 필요:
        - 관리자 또는 사용자 계정만 접근 가능
    """    
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.query(Choice).filter(Choice.question_id == question_id).delete()
    
    db.delete(question)
    db.commit()
    return {"message": "Question and related choices deleted successfully"}
