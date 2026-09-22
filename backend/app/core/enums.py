from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "active"


class UserRole(str, Enum):
    USER = "user"


class UserEvent(str, Enum):
    DRAW = "draw"
    WALLPAPER = "wallpaper"
    TAROT = "tarot"
    QUIZ = "quiz"
    MEME = "meme"
    DOWNLOAD = "download"
    MATCH = "match"
    CHECKIN = "checkin"
    DAILY_DRAW = "daily_draw"


EVENT_COUNTER_FIELDS = {
    UserEvent.WALLPAPER: "wallpapers",
    UserEvent.TAROT: "tarot",
    UserEvent.QUIZ: "quiz",
    UserEvent.MEME: "memes",
    UserEvent.DOWNLOAD: "downloads",
    UserEvent.MATCH: "matches",
}
