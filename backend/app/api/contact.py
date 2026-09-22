from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_optional_user
from app.database import get_db
from app.models import User
from app.schemas.contact import ContactOut, ContactRequest
from app.services.contact import create_contact_message

router = APIRouter()


@router.post("/contact", status_code=status.HTTP_201_CREATED, response_model=ContactOut)
def submit_contact(
    form: ContactRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
) -> ContactOut:
    host = request.client.host if request.client else "unknown"
    return create_contact_message(db, form, host, user)
