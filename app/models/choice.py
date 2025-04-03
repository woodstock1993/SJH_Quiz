from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Session
from sqlalchemy import event
from app.db.session import Base

class Choice(Base):
    __tablename__ = "choices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    text = Column(String, nullable=False)  
    is_correct = Column(Boolean, nullable=False, default=False)  
    order = Column(Integer, nullable=False)

    question = relationship("Question", back_populates="choices")

@event.listens_for(Choice, "before_insert")
def set_choice_order(mapper, connection, target):
    session = Session.object_session(target)
    if session is not None:
        max_order = session.query(Choice.order).filter_by(question_id=target.question_id).order_by(Choice.order.desc()).first()
        target.order = (max_order[0] + 1) if max_order else 1