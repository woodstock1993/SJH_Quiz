from pydantic import BaseModel
from fastapi import Form
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class OAuth2EmailRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
