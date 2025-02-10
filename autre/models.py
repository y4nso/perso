# models.py
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    email: EmailStr
    hashed_password: str
    full_name: str = None
    epreuve1: bool = False
    epreuve2: bool = False
    epreuve3: bool = False
    epreuve4: bool = False

class UserIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None

class Token(BaseModel):
    access_token: str
    token_type: str
