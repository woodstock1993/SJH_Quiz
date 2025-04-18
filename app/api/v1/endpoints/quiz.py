from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Any, Dict, List, Optional

from app.db.session import get_db
from app.schemas.choice import ChoiceResponse
from app.schemas.quiz import *
from app.schemas.question import QuestionResponse
from app.crud import quiz as crud_quiz
from app.core.security import get_current_user, get_admin_user
from app.models.user import User
from app.models.question import Question

router = APIRouter()

@router.post("/", response_model=QuizResponse)
def create_quiz_api(
        quiz: QuizCreate, 
        db: Session = Depends(get_db), 
        current_user: User = Depends(get_admin_user)
    ):
    """
    퀴즈 생성 API

    요청 본문:
    - title (Optional[str]): 퀴즈 제목
    - description (Optional[str]): 퀴즈 설명  

    응답 데이터:
    - id (int): 퀴즈 ID
    - title (str): 수정된 퀴즈 제목
    - description (str): 수정된 퀴즈 설명 

    인증 필요:
    - 관리자 계정만 접근 가능
    """
    return crud_quiz.create_quiz(db, quiz, user_id=current_user.id)

@router.post("/quizzes/{quiz_id}/register", response_model=QuizRegistrationCreate)
def register_quiz(
    quiz_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    사용자 특정 퀴즈 등록 API

    요청 본문:
    - quiz_id (int): 퀴즈 ID
    
    인증 필요:
    - 사용자 계정 접근 가능
    """
    registration = crud_quiz.register_user_for_quiz(db, user_id=current_user.id, quiz_id=quiz_id)
    if not registration:
        raise HTTPException(status_code=400, detail="Quiz registration failed")
    return registration

@router.post("/quizzes/{quiz_id}/attempt", response_model=QuizAttemptCreate)
def attempt_quiz(
    quiz_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    사용자 특정 퀴즈 응시 API

    요청 본문:
    - user_id (int): 사용자 ID
    - quiz_id (int): 퀴즈 ID
    
    인증 필요:
    - 사용자 계정 접근 가능
    """    
    attempt = crud_quiz.create_user_quiz_attempt(db, user_id=current_user.id, quiz_id=quiz_id)
    if not attempt:
        raise HTTPException(status_code=400, detail="Quiz attempt creation failed")
    return attempt

@router.get("/", response_model=Dict[str, Any])
def get_quizzes(
    db: Session = Depends(get_db),
    page: int = Query(0, alias="page"),
    page_size: int = Query(10, alias="page_size"),    
    current_user: User = Depends(get_current_user)
):
    """
    퀴즈 조회 API

    이 API는 다음 기능을 제공합니다:
    1. 관리자는 전체 퀴즈를 조회할 수 있습니다.
    2. 일반 사용자는 자신이 응시한 퀴즈만 조회할 수 있습니다.

    파라미터:
    - page: 페이지 번호 (기본값: 0)
    - page_size: 페이지당 퀴즈 개수 (기본값: 10)
    - current_user: 현재 로그인한 사용자 (옵션)

    응답 데이터:
    - total_count: 전체 퀴즈 개수
    - page: 현재 페이지 번호
    - page_size: 페이지당 항목 수
    - quizzes: 퀴즈 목록

    인증 필요:
    - 관리자 또는 사용자 계정만 접근 가능
    """
    return crud_quiz.read_quizzes(db, page=page, page_size=page_size, current_user=current_user)


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz(quiz_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    특정 퀴즈 조회 API

    quiz_id에 해당하는 퀴즈 정보를 조회합니다.

    - 요청 경로 파라미터:
        - quiz_id (int): 조회할 퀴즈의 고유 ID

    - 응답 데이터:        
        - title (str): 퀴즈 제목
        - description (str): 퀴즈 설명
        - is_attempted (bool): 사용자가 응시했는지 여부

    - 예외 처리:
        - 404 Not Found: 해당 quiz_id의 퀴즈가 존재하지 않을 경우

    - 인증 필요:
        - 관리자 또는 사용자 계정만 접근 가능
    """
    quiz = crud_quiz.read_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.get("/{quiz_id}/question/choices", response_model=Dict[str, Any])
def get_choices_questions_by_quiz(
        quiz_id: int, 
        db: Session = Depends(get_db),
        page: int = Query(0, alias="page"), 
        page_size: int = Query(10, alias="page_size"),
        current_user: User = Depends(get_admin_user),
    ):
    """
    특정 퀴즈의 모든 질문과 선택지를 조회하는 API

    quiz_id에 해당하는 퀴즈의 질문과 선택지를 조회합니다.
    관리자로 인증된 사용자만 접근할 수 있습니다.

    요청 경로 파라미터:
    - quiz_id (int): 조회할 퀴즈의 고유 ID

    요청 쿼리 파라미터:
    - page (int, 기본값: 0): 페이지 번호
    - page_size (int, 기본값: 10): 한 페이지에 포함될 질문 개수

    응답 데이터:
    - total_count (int): 해당 퀴즈의 전체 질문 개수
    - page (int): 현재 페이지 번호
    - page_size (int): 페이지당 질문 개수
    - questions (list): 질문 목록
        - id (int): 질문 ID
        - quiz_id (int): 퀴즈 ID
        - text (str): 질문 내용
        - order (int): 퀴즈 질문 순번
        - choices (list): 선택지 목록
            - id (int): 선택지 ID
            - question_id (int): 해당 선택지가 속한 질문 ID
            - text (str): 선택지 내용
            - is_correct (bool): 정답 여부

    인증 필요:
    - 관리자 계정만 접근 가능
    """    
    offset = page * page_size
    total_count = db.query(Question).filter(Question.quiz_id == quiz_id).count()
    questions = (
        db.query(Question)
        .filter(Question.quiz_id == quiz_id)
        .options(joinedload(Question.choices))
        .order_by(Question.id.asc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "questions": [
            QuestionResponse(
                id=q.id,
                quiz_id=q.quiz_id,
                text=q.text,
                order=q.order,
                choices=[
                    ChoiceResponse(
                        id=c.id,
                        question_id=c.question_id,
                        text=c.text,
                        is_correct=c.is_correct
                    ) for c in q.choices
                ]
            ) for q in questions
        ]
    }

@router.get("/{quiz_id}/random-questions")
def get_random_quiz_questions(
        quiz_id: int, 
        num: int = Query(None, description="Number of questions to retrieve"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_admin_user),
    ):
    """
    사용자 퀴즈별 무작위 문제 및 선택지 조회 API

    요청 본문:
    - quiz_id (int): 퀴즈 ID
    - num (int): 생성 문제 수
    
    인증 필요:
    - 관리자 계정 접근 가능
    """    
    result = crud_quiz.read_random_questions(db, quiz_id, num)
    if result is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return result

@router.get("/{quiz_id}/start")
def get_start_quiz(
        quiz_id: int,
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),        
):
    """
    사용자 퀴즈 시작 API

    요청 본문:
    - user_id (int): 사용자 ID
    - quiz_id (int): 퀴즈 ID    
    
    인증 필요:
    - 사용자 계정 접근 가능
    """        
    result = crud_quiz.read_random_questions(db, user_id, quiz_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return result

@router.get("/refresh/{user_quiz_attempt_id}")
def get_refresh_quiz(
        quiz_id: int,
        user_quiz_attempt_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    사용자 퀴즈별 정보(문제, 선택지, 답안지) 조회 API

    요청 본문:
    - quiz_id (int): 퀴즈 ID    
    - user_id (int): 사용자 ID
    
    인증 필요:
    - 사용자 계정 접근 가능
    """            
    result = crud_quiz.read_quiz_attempt_cache(quiz_id, user_quiz_attempt_id)
    if result is None:
        raise HTTPException(status_code=404, detail="UserQuizAttempt not found")
    return result

@router.put("/{quiz_id}", response_model=QuizResponse)
def update_quiz_api(quiz_id: int, quiz_update: QuizUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    퀴즈 수정 API

    quiz_id에 해당하는 퀴즈의 내용을 수정합니다.
    관리자로 인증된 사용자만 수정할 수 있습니다.

    요청 경로 파라미터:
    - quiz_id (int): 수정할 퀴즈의 고유 ID

    요청 본문:
    - title (Optional[str]): 퀴즈 제목
    - description (Optional[str]): 퀴즈 설명    

    응답 데이터:    
    - title (str): 수정된 퀴즈 제목
    - description (str): 수정된 퀴즈 설명    

    인증 필요:
    - 관리자 계정만 접근 가능

    예외 처리:
    - 404: 해당 quiz_id의 퀴즈가 존재하지 않는 경우
    """    
    quiz = crud_quiz.update_quiz(db, quiz_id, quiz_update)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.patch("/{quiz_id}/answer", response_model=QuizAnswerResponse)
def update_quiz_answer(
    quiz_id: int,
    user_quiz_attempt_id: int,
    request: QuizAnswerRequest,    
    current_user: User = Depends(get_current_user),
):
    """
    사용자 선택지 업데이트 API

    요청 본문:
    - quiz_id (int): 퀴즈 ID    
    - user_quiz_attempt_id (int): 사용자 퀴즈 응시 ID
    
    인증 필요:
    - 사용자 계정 접근 가능
    """     
    result = crud_quiz.update_quiz_answer(quiz_id, user_quiz_attempt_id, request)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to update answer")    
    return result
    
@router.post("/{quiz_id}/submit", response_model=None)
def post_submit_quiz(
        quiz_id: int,
        user_quiz_attempt_id: int,
        data: QuizSubmissionRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    사용자 시험 제출 API

    요청 본문:
    - quiz_id (int): 퀴즈 ID    
    - user_quiz_attempt_id (int): 사용자 퀴즈 응시 ID
    
    인증 필요:
    - 사용자 계정 접근 가능
    """         
    result = crud_quiz.submit_quiz(db, quiz_id, user_quiz_attempt_id, data)
    if result is None:
        raise HTTPException(status_code=400, detail="Quiz submition failed")        
    return result

@router.post("/sample")
def quiz_sample(
    title: str,
    description: str,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    샘플 퀴즈 생성 API

    요청 본문:
    - title: 문제 제목
    - description: 문제 설명
    - user_id (int): 사용자 ID     
    
    인증 필요:
    - 관리자 계정 접근 가능
    """         
    result = crud_quiz.test_create_quiz_with_questions_and_choices(db, title=title, description=description, user_id=user_id)
    return result

@router.get("/{quiz_id}/validate")
def get_validate_quiz(
        quiz_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_admin_user),
):
    """
    퀴즈 검증 API

    요청 본문:
    - quiz_id (int): 퀴즈 ID
    
    인증 필요:
    - 관리자 계정 접근 가능
    """     
    result = crud_quiz.validate_quiz(db, quiz_id=quiz_id)
    if result is None:
        raise HTTPException(status_code=400, detail="Quiz Validation failed")        
    return result
