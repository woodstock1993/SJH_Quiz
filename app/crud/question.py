from sqlalchemy.orm import Session
from app.models.choice import Choice
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate
from app.schemas.choice import ChoiceCreate, ChoiceUpdate

def create_question(db: Session, question_data: QuestionCreate):
    db_question = Question(**question_data.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def read_question(db: Session, question_id: int):
    return db.query(Question).filter(Question.id == question_id).first()

def read_questions_by_quiz(db: Session, quiz_id: int):
    return db.query(Question).filter(Question.quiz_id == quiz_id).all()

def update_question(db: Session, question_id: int, question_data: QuestionUpdate):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if db_question:
        for key, value in question_data.dict(exclude_unset=True).items():
            setattr(db_question, key, value)
        db.commit()
        db.refresh(db_question)
    return db_question

def delete_question(db: Session, question_id: int):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if db_question:
        db.query(Choice).filter(Choice.question_id == question_id).delete()
        db.delete(db_question)
        db.commit()
    return db_question
