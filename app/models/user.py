from datetime import datetime
import pytz
KST = pytz.timezone('Asia/Seoul')

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
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
    registered_at = Column(DateTime, default=lambda: datetime.now(KST))

    quiz = relationship("Quiz", back_populates="registrations")
    user = relationship("User", back_populates="quiz_registrations")

class UserQuizAttempt(Base):
    __tablename__ = "user_quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    attempted_at = Column(DateTime, default=lambda: datetime.now(KST))

    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="quiz_attempts")