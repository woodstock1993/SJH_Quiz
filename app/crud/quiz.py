from datetime import datetime
import httpx
import json
import random
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, Query
from sqlalchemy.orm import joinedload, Session

from app.utils.utils import transform_to_quiz_submit
from app.core.config import redis_client, settings
from app.models.user import User
from app.models.quiz import Quiz
from app.models.choice import Choice
from app.models.user import UserQuizAttempt, UserQuizAttemptQuestion, UserQuizAttemptAnswer, UserQuizRegistration, UserQuizScore
from app.models.question import Question
from app.schemas.quiz import *

def create_quiz(db: Session, quiz: QuizCreate, user_id: int):
    db_quiz = Quiz(**quiz.dict(), user_id=user_id) 
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

def register_user_for_quiz(db: Session, user_id: int, quiz_id: int):
    existing_registration = db.query(UserQuizRegistration).filter(
        UserQuizRegistration.user_id == user_id,
        UserQuizRegistration.quiz_id == quiz_id
    ).first()
    
    if existing_registration:
        raise HTTPException(status_code=400, detail="User is already registered for this quiz.")
    
    registration = UserQuizRegistration(
        user_id=user_id,
        quiz_id=quiz_id,
        registered_at=datetime.now()
    )
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration

def create_user_quiz_attempt(db: Session, user_id: int, quiz_id: int):    
    registered = db.query(UserQuizRegistration).filter(
        UserQuizRegistration.user_id == user_id,
        UserQuizRegistration.quiz_id == quiz_id
    ).first()
    
    if not registered:
        raise HTTPException(status_code=400, detail="User is not registered for this quiz.")
        
    existing_attempt = db.query(UserQuizAttempt).filter(
        UserQuizAttempt.user_id == user_id,
        UserQuizAttempt.quiz_id == quiz_id
    ).first()
    
    if existing_attempt:
        raise HTTPException(status_code=400, detail="User has already attempted this quiz.")
    
    attempt = UserQuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        attempted_at=datetime.now()
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt

def get_user_quiz_attempts(db: Session, user_id: int):
    return db.query(UserQuizAttempt).filter(UserQuizAttempt.user_id == user_id).all()

def read_user_quiz_statuses(db: Session, user_id: int):
    registered_quizzes = db.query(UserQuizRegistration.quiz_id).filter(UserQuizRegistration.user_id == user_id).all()
    attempted_quizzes = db.query(UserQuizAttempt.quiz_id).filter(UserQuizAttempt.user_id == user_id).all()
    
    registered_quiz_ids = {quiz.quiz_id for quiz in registered_quizzes}
    attempted_quiz_ids = {quiz.quiz_id for quiz in attempted_quizzes}
    
    quiz_statuses = []
    for quiz_id in registered_quiz_ids:
        quiz_statuses.append({
            "quiz_id": quiz_id,
            "registered": True,
            "attempted": quiz_id in attempted_quiz_ids
        })
    
    return quiz_statuses

def read_quizzes(
    db: Session,    
    page: int = Query(0, alias="page"),
    page_size: int = Query(10, alias="page_size"),
    current_user: Optional[User] = None
):
    offset = page * page_size
    
    if current_user and current_user.is_superuser:
        quizzes = db.query(Quiz).offset(offset).limit(page_size).all()
        total_count = db.query(Quiz).count()

        return {
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "quizzes": [
                QuizResponse(
                    id=quiz.id,
                    title=quiz.title,
                    description=quiz.description
                )
                for quiz in quizzes
            ]
        }

    user_attempts = {
        attempt.quiz_id for attempt in db.query(UserQuizAttempt)
        .filter(UserQuizAttempt.user_id == current_user.id)
        .all()
    }

    quizzes = (
        db.query(Quiz)
        .filter(Quiz.id.in_(user_attempts))
        .offset(offset)
        .limit(page_size)
        .all()
    )
    total_count = db.query(Quiz).filter(Quiz.id.in_(user_attempts)).count()

    return {
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "quizzes": [
            QuizResponse(
                id=quiz.id,
                title=quiz.title,
                description=quiz.description,
                is_attempted=True
            )
            for quiz in quizzes
        ]
    }

def read_quiz(db: Session, quiz_id: int):
    return db.query(Quiz).filter(Quiz.id == quiz_id).first()

def read_questions_with_choices_by_quiz(db: Session, quiz_id: int):
    return db.query(Question).filter(Question.quiz_id == quiz_id).options(joinedload(Question.choices)).all()

def read_random_questions(db: Session, user_id: int, quiz_id: int, num_questions: int = None):
    """
    사용자가 시험 시작할 때 문제 순서와 답안 순서를 Redis에 반영하는 함수 (퀴즈 정보 포함)
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        return None

    user_quiz_attempt = UserQuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        is_submit=False
    )
    db.add(user_quiz_attempt)
    db.commit()
    db.refresh(user_quiz_attempt)

    redis_key = f"quiz:{quiz_id}:user_quiz_attempts:{user_quiz_attempt.id}"
    cached_data = redis_client.get(redis_key)
    
    if cached_data:
        return json.loads(cached_data)    

    total_questions = db.query(Question).filter(Question.quiz_id == quiz_id).count()
    
    if num_questions is None:
        num_questions = quiz.question_count or total_questions
    
    if num_questions > total_questions:
        num_questions = total_questions
    
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    # selected_questions = random.sample(questions, num_questions)
    selected_questions = questions
    
    result = {
        "quiz_id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "questions": []
    }

    for question in selected_questions:
        choices = db.query(Choice).filter(Choice.question_id == question.id).all()
        # random.shuffle(choices)
        result["questions"].append({
            "id": question.id,
            "text": question.text,
            "choices": [{"id": choice.id, "text": choice.text} for choice in choices]
        })
    
    
    redis_client.setex(redis_key, 3600, json.dumps(result))  # 퀴즈 정보까지 Redis에 저장

    return result

def update_quiz(db: Session, quiz_id: int, quiz_update: QuizUpdate):
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if db_quiz:
        for key, value in quiz_update.dict(exclude_unset=True).items():
            setattr(db_quiz, key, value)
        db.commit()
        db.refresh(db_quiz)
    return db_quiz

def update_quiz_answer(quiz_id: int, user_quiz_attempt_id: int,  request: QuizAnswerRequest):
    """
    사용자가 선택지를 클릭할 때 Redis에 반영하는 함수
    """
    attempt_key = f"quiz:{quiz_id}:user_quiz_attempts:{user_quiz_attempt_id}:answers"
        
    if redis_client.exists(attempt_key):
        answers = {k: v for k, v in redis_client.hgetall(attempt_key).items()}
    else:
        answers = {}
    
    answers[str(request.question_id)] = str(request.selected_choice_id)
    
    redis_client.hset(attempt_key, request.question_id, request.selected_choice_id)

    if not redis_client.ttl(attempt_key):
        redis_client.expire(attempt_key, 1200)

    return QuizAnswerResponse(
        quiz_attempt_id=user_quiz_attempt_id, 
        question_id=request.question_id,
        choice_id=request.selected_choice_id,
        message="Answer updated successfully"
    )

def read_quiz_attempt_cache(quiz_id: int, user_quiz_attempt_id: int):
    """
    사용자가 시험 중 새로고침 했을 때 문제 순서, 답안 순서, 사용자의 선택한 답안을 반환하는 API
    """
    redis_key = f"quiz:{quiz_id}:user_quiz_attempts:{user_quiz_attempt_id}"
    attempt_key = f"{redis_key}:answers"
    
    cached_data = redis_client.get(redis_key)
    if not cached_data:
        return {"error": "No quiz data found."}

    quiz_data = json.loads(cached_data)
    
    user_answers = {k: v for k, v in redis_client.hgetall(attempt_key).items()} if redis_client.exists(attempt_key) else {}
    print(quiz_data)

    if isinstance(quiz_data, list):
        
        if quiz_data:
            quiz_data = {"questions": quiz_data}
        else:
            raise ValueError("quiz_data 리스트가 비어 있음")
    
    for question in quiz_data["questions"]:
        question_id = str(question["id"])
        for choice in question["choices"]:
            choice["is_selected"] = choice["id"] == int(user_answers.get(question_id, "-1"))
    
    return quiz_data

def submit_quiz(db: Session, quiz_id: int, user_quiz_attempt_id: int, data: QuizSubmitRequest):   
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise ValueError("퀴즈를 찾을 수 없습니다.")
    
    # 데이터 변환
    quiz_data = transform_to_quiz_submit(data)

    correct_count = 0
    total_count = len(quiz_data.questions)
    
    # 각 질문의 선택된 답안 저장
    for question in quiz_data.questions:
        user_quiz = UserQuizAttemptQuestion(
            attempt_id=user_quiz_attempt_id,
            question_id=question['id'],
        )
        db.add(user_quiz)
        for choice in question['choices']:
            print(choice)
            user_answer = UserQuizAttemptAnswer(
                user_quiz_attempt_id=user_quiz_attempt_id,
                question_id=question['id'],
                choice_id=choice['id']
            )
            db.add(user_answer)

            choice_obj = db.query(Choice).filter(Choice.id == choice['id']).first()            
            if choice_obj and choice_obj.is_correct and choice['is_selected']:
                correct_count += 1

    attempt = db.query(UserQuizAttempt).filter(UserQuizAttempt.id == user_quiz_attempt_id).first()
    if not attempt:
        raise ValueError("퀴즈 응시 정보를 찾을 수 없습니다.")
    attempt.is_submit = True

    user_score = UserQuizScore(
        user_quiz_attempt_id=user_quiz_attempt_id,
        score=correct_count,
        total=total_count
    )
    db.add(user_score)
    db.commit()    

    return {
        "message": "퀴즈 제출 완료", 
        "score": correct_count,
        "total": total_count     
        }

def test_create_quiz_with_questions_and_choices(db: Session, title: str, description: str, user_id: int):
    quiz = Quiz(title=title, description=description, user_id=user_id)
    db.add(quiz)
    db.flush()

    for i in range(1, 101):
        question = Question(
            quiz_id=quiz.id,
            text=f"문제 {i}",
        )
        db.add(question)
        db.flush()

        for j in range(1, 6):  # 선택지 5개 생성
            choice = Choice(
                question_id=question.id,
                text=f"{i}번 문제 선택지 {j}",
                is_correct=(j == 1)  # 첫 번째 선택지만 정답
            )
            db.add(choice)

    db.commit()
    db.refresh(quiz)
    return quiz

def validate_quiz(db: Session, quiz_id: int) -> dict:
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        return {"valid": False, "reason": "퀴즈가 존재하지 않습니다."}

    if not quiz.questions or len(quiz.questions) == 0:
        return {"valid": False, "reason": "퀴즈에 문제가 없습니다."}

    for question in quiz.questions:
        choices = question.choices
        
        if len(choices) < 2:
            return {"valid": False, "reason": f"문제 ID {question.id}에 선택지가 2개 미만입니다."}

        correct_choices = [c for c in choices if c.is_correct]
        if len(correct_choices) == 0:
            return {"valid": False, "reason": f"문제 ID {question.id}에 정답이 없습니다."}
        
    return {"valid": True, "reason": "퀴즈가 올바르게 구성되었습니다."}
