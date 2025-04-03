from pydantic import BaseModel
from typing import Optional

class ChoiceBase(BaseModel):
    text: str
    is_correct: bool
    question_id: int

class ChoiceCreate(ChoiceBase):
    pass

class ChoiceUpdate(BaseModel):
    text: Optional[str] = None
    is_correct: Optional[bool] = None

class ChoiceResponse(ChoiceBase):
    id: int
    question_id: int
    text: str
    is_correct: bool
    
    class Config:
        from_attributes = True
