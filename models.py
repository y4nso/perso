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
    is_admin: bool = False
    is_zoo: bool = False
    item1: bool = False
    item2: bool = False
    item3: bool = False
    item4: bool = False
    item5: bool = False
    item6: bool = False
    item7: bool = False
    item8: bool = False
    item9: bool = False
    item10: bool = False

class UserIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None

class Token(BaseModel):
    access_token: str
    token_type: str
