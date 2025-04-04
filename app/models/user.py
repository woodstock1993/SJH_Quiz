import pytz
KST = pytz.timezone('Asia/Seoul')

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, unique=False, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())    

    quizzes = relationship("Quiz", back_populates="user")
    quiz_attempts = relationship("UserQuizAttempt", back_populates="user")
    quiz_registrations = relationship("UserQuizRegistration", back_populates="user")

class UserQuizRegistration(Base):
    __tablename__ = "user_quiz_registrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    registered_at = Column(DateTime, server_default=func.now())

    quiz = relationship("Quiz", back_populates="registrations")
    user = relationship("User", back_populates="quiz_registrations")

class UserQuizAttempt(Base):
    __tablename__ = "user_quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    attempted_at = Column(DateTime, server_default=func.now())

    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="quiz_attempts")
    attempt_questions = relationship("UserQuizAttemptQuestion", back_populates="attempt")
    answers = relationship("UserQuizAttemptAnswer", back_populates="user_quiz_attempt")

class UserQuizAttemptAnswer(Base):
    __tablename__ = "user_quiz_attempt_answers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_quiz_attempt_id = Column(Integer, ForeignKey("user_quiz_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    choice_id = Column(Integer, ForeignKey("choices.id"), nullable=False)
    
    # 관계 설정
    user_quiz_attempt = relationship("UserQuizAttempt", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    choice = relationship("Choice", back_populates="answers")

class UserQuizAttemptQuestion(Base):
    __tablename__ = "user_quiz_attempt_questions"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("user_quiz_attempts.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))

    attempt = relationship("UserQuizAttempt", back_populates="attempt_questions")
    question = relationship("Question")    

    __table_args__ = (UniqueConstraint('attempt_id', 'question_id', name='uq_attempt_question'),)

