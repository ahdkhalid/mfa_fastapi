from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str

class UserDelete(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int
    disabled: bool = False

    class Config:
        orm_mode = True
