from pydantic import BaseModel, Field


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
    pityCount: int = Field(default=0, ge=0)
    lastDailyDraw: str = ""
    mines: int = Field(default=0, ge=0)
    lastDailyMine: str = ""


class LocalDataImportRequest(BaseModel):
    favorites: list[str] = Field(default_factory=list, max_length=2000)
    collection: list[str] = Field(default_factory=list, max_length=2000)
    unlocked: list[str] = Field(default_factory=list, max_length=200)
    stats: LocalStats = Field(default_factory=LocalStats)


class UserEventRequest(BaseModel):
    event: str
    count: int = Field(default=1, ge=0, le=100)
    ssr: int = Field(default=0, ge=0, le=100)
    pity: int = Field(default=0, ge=0, le=100)


class UserDataOut(BaseModel):
    favorites: list[str]
    collection: list[str]
    unlocked: list[str]
    stats: LocalStats


class FilenameSuccessOut(BaseModel):
    success: bool = True
    filename: str


class UserDataMutationOut(BaseModel):
    success: bool = True
    data: UserDataOut
