from collections import defaultdict
from time import time

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_optional_user
from app.models import ContactMessage, User
from app.schemas import ContactRequest

router = APIRouter()
_contact_hits: dict[str, list[float]] = defaultdict(list)
_MAX_PER_MINUTE = 5


def _rate_limit_contact(request: Request) -> None:
    host = request.client.host if request.client else "unknown"
    now = time()
    window = [stamp for stamp in _contact_hits[host] if now - stamp < 60]
    if len(window) >= _MAX_PER_MINUTE:
        raise HTTPException(status_code=429, detail="留言过于频繁，请稍后再试")
    window.append(now)
    _contact_hits[host] = window


@router.post("/contact", status_code=status.HTTP_201_CREATED)
def submit_contact(
    form: ContactRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    _rate_limit_contact(request)
    item = ContactMessage(
        user_id=user.id if user else None,
        name=form.name.strip(),
        email=str(form.email),
        subject=form.subject.strip(),
        message=form.message.strip(),
    )
    db.add(item)
    db.commit()
    return {"success": True, "message": "留言发送成功，感谢你的反馈！", "id": item.id}
