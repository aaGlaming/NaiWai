from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_\-]+$")
    password: str = Field(min_length=8, max_length=128)
    nickname: str = Field(min_length=1, max_length=50)
    email: EmailStr | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str
    email: str | None
    role: str
    local_data_imported: bool = False


class ContactRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    subject: str = Field(min_length=1, max_length=150)
    message: str = Field(min_length=1, max_length=5000)


class LocalStats(BaseModel):
    draws: int = Field(default=0, ge=0)
    ssrCount: int = Field(default=0, ge=0)
    wallpapers: int = Field(default=0, ge=0)
    tarot: int = Field(default=0, ge=0)
    quiz: int = Field(default=0, ge=0)
    memes: int = Field(default=0, ge=0)
    downloads: int = Field(default=0, ge=0)
    matches: int = Field(default=0, ge=0)
    streak: int = Field(default=0, ge=0)
    lastCheckin: str = ""


class LocalDataImportRequest(BaseModel):
    favorites: list[str] = Field(default_factory=list, max_length=2000)
    collection: list[str] = Field(default_factory=list, max_length=2000)
    unlocked: list[str] = Field(default_factory=list, max_length=200)
    stats: LocalStats = Field(default_factory=LocalStats)


class UserEventRequest(BaseModel):
    event: str
    count: int = Field(default=1, ge=1, le=100)
    ssr: int = Field(default=0, ge=0, le=100)
