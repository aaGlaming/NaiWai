from pydantic import BaseModel, EmailStr, Field


class ContactRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    subject: str = Field(min_length=1, max_length=150)
    message: str = Field(min_length=1, max_length=5000)


class ContactOut(BaseModel):
    success: bool = True
    message: str
    id: int
