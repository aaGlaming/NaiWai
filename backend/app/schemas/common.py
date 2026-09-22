from pydantic import BaseModel


class SuccessOut(BaseModel):
    success: bool = True


class HealthOut(BaseModel):
    status: str
    database: str
    desktop: bool
    message: str
