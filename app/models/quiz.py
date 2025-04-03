from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)    

    user = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")
    attempts = relationship("UserQuizAttempt", back_populates="quiz")
    registrations = relationship("UserQuizRegistration", back_populates="quiz")
