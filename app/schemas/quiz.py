from pydantic import BaseModel
from typing import List
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