from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import event
from sqlalchemy.orm import relationship, Session
from app.db.session import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    text = Column(String, nullable=False)
    order = Column(Integer, nullable=False)

    quiz = relationship("Quiz", back_populates="questions")
    choices = relationship("Choice", back_populates="question")

@event.listens_for(Question, "before_insert")
def set_question_order(mapper, connection, target):
    session = Session.object_session(target)
    if session is not None:
        max_order = session.query(Question.order).filter_by(quiz_id=target.quiz_id).order_by(Question.order.desc()).first()
        target.order = (max_order[0] + 1) if max_order else 1