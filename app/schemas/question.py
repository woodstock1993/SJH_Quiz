from pydantic import BaseModel
from typing import List, Optional
from app.schemas.choice import ChoiceCreate, ChoiceUpdate, ChoiceResponse

class QuestionBase(BaseModel):
    text: str

class QuestionCreate(QuestionBase):
    quiz_id: int    
    text: str    

class QuestionUpdate(BaseModel):
    text: Optional[str] = None

class QuestionResponse(QuestionBase):
    id: int
    quiz_id: int
    order: int
    text: str
    choices: List[ChoiceResponse]
    
    class Config:
        from_attributes = True
