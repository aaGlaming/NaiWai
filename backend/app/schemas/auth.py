from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str
    email: str | None
    role: str
    local_data_imported: bool = False


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_\-]+$")
    password: str = Field(min_length=8, max_length=128)
    nickname: str = Field(min_length=1, max_length=50)
    email: EmailStr | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthUserOut(BaseModel):
    user: UserResponse
