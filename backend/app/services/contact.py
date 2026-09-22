import logging
from collections import defaultdict
from time import time

from sqlalchemy.orm import Session

from app.core.exceptions import RateLimitError
from app.models import ContactMessage, User
from app.schemas.contact import ContactOut, ContactRequest

logger = logging.getLogger(__name__)


class MemoryRateLimiter:
    def __init__(self, max_per_minute: int = 5, window_seconds: float = 60) -> None:
        self.max_per_minute = max_per_minute
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> None:
        now = time()
        window = [stamp for stamp in self._hits[key] if now - stamp < self.window_seconds]
        if len(window) >= self.max_per_minute:
            logger.info("contact rate limited for key=%s", key)
            raise RateLimitError("留言过于频繁，请稍后再试")
        window.append(now)
        self._hits[key] = window

    def reset(self) -> None:
        self._hits.clear()


contact_limiter = MemoryRateLimiter()


def create_contact_message(
    db: Session,
    form: ContactRequest,
    client_key: str,
    user: User | None,
) -> ContactOut:
    contact_limiter.check(client_key)
    item = ContactMessage(
        user_id=user.id if user else None,
        name=form.name.strip(),
        email=str(form.email),
        subject=form.subject.strip(),
        message=form.message.strip(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return ContactOut(success=True, message="留言发送成功，感谢你的反馈！", id=item.id)
