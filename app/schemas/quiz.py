from datetime import datetime
from pydantic import BaseModel
from typing import List, Any
from typing import Optional

from app.schemas.choice import ChoiceResponse

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None

class QuizCreate(QuizBase):
    pass

class QuizUpdate(QuizBase):
    pass

class QuizResponse(QuizBase):
    id: int
    title: str

    class Config:
        from_attributes = True

class QuestionWithChoicesResponse(BaseModel):
    id: int
    text: str
    quiz_id: int
    choices: List[ChoiceResponse]

    class Config:
        orm_mode = True

class QuizRegistrationCreate(BaseModel):
    user_id: int
    quiz_id: int

class QuizRegistrationResponse(QuizRegistrationCreate):
    id: int
    registered_at: datetime

    class Config:
        orm_mode = True

class QuizAttemptCreate(BaseModel):
    user_id: int
    quiz_id: int

class QuizAttemptResponse(QuizAttemptCreate):
    id: int
    attempted_at: datetime

    class Config:
        orm_mode = True

class QuizAnswerRequest(BaseModel):
    quiz_attempt_id: int
    question_id: int
    selected_choice_id: int

class QuizAnswerResponse(BaseModel):
    quiz_attempt_id: int
    question_id: int
    choice_id: int
    message: str

class QuizSubmissionRequest(BaseModel):
    user_id: int
    quiz_attempt_id: int
    answers: List[Any]

class QuizSubmissionResponse(BaseModel):
    attempt_id: int
    message: str

class Answer(BaseModel):
    question_id: int
    choice_id: int

class ChoiceSubmit:
    def __init__(self, id: int, is_selected: bool):
        self.id = id
        self.is_selected = is_selected

class QuestionSubmit:
    def __init__(self, id: int, text: str, choices: List[ChoiceSubmit]):
        self.id = id
        self.text = text
        self.choices = choices

class QuizSubmitRequest:
    def __init__(self, quiz_id: int, title: str, description: str, questions: QuestionSubmit):
        self.quiz_id = quiz_id
        self.title = title
        self.description = description
        self.questions = questions