from typing import Any, Dict, List, Optional

from fastapi import Depends, Query

from sqlalchemy.orm import joinedload, Session
from app.models.user import User
from app.models.quiz import Quiz
from app.models.choice import Choice
from app.models.user import UserQuizAttempt
from app.models.question import Question
from app.schemas.quiz import QuizCreate, QuizUpdate, QuizResponse

def create_quiz(db: Session, quiz: QuizCreate, user_id: int):
    db_quiz = Quiz(**quiz.dict(), user_id=user_id) 
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

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

def update_quiz(db: Session, quiz_id: int, quiz_update: QuizUpdate):
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if db_quiz:
        for key, value in quiz_update.dict(exclude_unset=True).items():
            setattr(db_quiz, key, value)
        db.commit()
        db.refresh(db_quiz)
    return db_quiz

def delete_quiz(db: Session, quiz_id: int):
    try:
        db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        
        if not db_quiz:
            return None

        questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
        
        for question in questions:
            db.query(Choice).filter(Choice.question_id == question.id).delete()

        db.query(Question).filter(Question.quiz_id == quiz_id).delete()

        db.delete(db_quiz)
        
        db.commit()
        return db_quiz

    except Exception as e:
        db.rollback()
        raise e
