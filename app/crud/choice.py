from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.models.choice import Choice
from app.schemas import choice as schemas

def create_choice(db: Session, choice: schemas.ChoiceCreate):
    db_choice = Choice(**choice.dict())
    db.add(db_choice)
    db.commit()
    db.refresh(db_choice)
    return db_choice

def get_choice(db: Session, choice_id: int):
    return db.query(Choice).filter(Choice.id == choice_id).first()

def get_choices_by_question(db: Session, question_id: int):
    return db.query(Choice).filter(Choice.question_id == question_id).all()

def update_choice(db: Session, choice_id: int, choice: schemas.ChoiceUpdate):
    db_choice = db.query(Choice).filter(Choice.id == choice_id).first()
    if db_choice:
        for key, value in choice.dict(exclude_unset=True).items():
            setattr(db_choice, key, value)
        db.commit()
        db.refresh(db_choice)
    return db_choice

def delete_choice(db: Session, choice_id: int):
    db_choice = db.query(Choice).filter(Choice.id == choice_id).first()
    if db_choice:
        db.delete(db_choice)
        db.commit()
    return db_choice
