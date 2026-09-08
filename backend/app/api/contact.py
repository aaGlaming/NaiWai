from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_optional_user
from app.models import ContactMessage, User
from app.schemas import ContactRequest

router = APIRouter()


@router.post("/contact", status_code=status.HTTP_201_CREATED)
def submit_contact(form: ContactRequest, db: Session = Depends(get_db), user: User | None = Depends(get_optional_user)):
    item = ContactMessage(user_id=user.id if user else None, name=form.name.strip(), email=str(form.email),
                          subject=form.subject.strip(), message=form.message.strip())
    db.add(item)
    db.commit()
    return {"success": True, "message": "留言发送成功，感谢你的反馈！", "id": item.id}
