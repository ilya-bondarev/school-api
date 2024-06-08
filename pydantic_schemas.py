from pydantic import BaseModel, EmailStr, constr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    login: EmailStr
    password: str
    full_name: str
    role_id: int
    photo: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes=True

class UserCreate(BaseModel):
    login: EmailStr
    password: str
    full_name: str
    role_id: int
    photo: Optional[str] = None
    description: Optional[str] = None

class UserLogIn(BaseModel):
    login: EmailStr
    password: str

class UserProfile(BaseModel):
    id: int
    full_name: str
    login: EmailStr
    role_id: int
    registration_date: datetime
    photo: str
    description: str

    class Config:
        from_attributes = True

class Teacher(BaseModel):
    id: int
    full_name:str
    description: Optional[str]
    photo: Optional[str]
    lessons_amount: int = Field(default=0)
    rating: float = Field(default=5.0)
    registration_date: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires: datetime

    class Config:
        from_attributes=True

class TokenData(BaseModel):
    username: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class Block(BaseModel):
    id: int
    x: int
    y: int
    width: int
    height: int
    content: str = ""
    contentType: str
    contentUrl: str = ""
    pageNumber: int = 1

class Lesson(BaseModel):
    id: int
    teacher_id: int
    teacher: UserProfile
    student_id: int
    student: UserProfile
    date_time: datetime
    duration: int
    status_id: int

    class Config:
        from_attributes=True

class LessonCreate(BaseModel):
    teacher_id: int
    student_id: int
    date_time: datetime
    duration: int
    status_id: int

class LessonUpdateStatus(BaseModel):
    status_id: int

class TeacherFiles():
    file_name: str
    file_type: str
