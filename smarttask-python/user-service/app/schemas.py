from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True  # în loc de orm_mode pentru Pydantic v2


class Token(BaseModel):
    access_token: str
    token_type: str
