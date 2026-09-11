import json
from pathlib import Path

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Achievement, Image
from app.paths import image_manifest_path

ACHIEVEMENTS = [
    ("first_favorite", "初次收藏", "收藏第一张奶蛙图", "favorites", 1, "💖"),
    ("collector_10", "收藏达人", "收藏 10 张奶蛙图", "favorites", 10, "📚"),
    ("first_draw", "初出茅庐", "完成第一次抽卡", "draws", 1, "🎰"),
    ("draw_10", "抽卡狂人", "累计抽卡 10 次", "draws", 10, "🔥"),
    ("ssr_get", "传说降临", "抽到一张 SSR", "ssr_count", 1, "👑"),
    ("wallpaper_1", "壁纸大师", "生成第一张壁纸", "wallpapers", 1, "🖼️"),
    ("tarot_1", "命运占卜", "完成第一次塔罗占卜", "tarot", 1, "🔮"),
    ("quiz_1", "自我认知", "完成奶蛙心情测试", "quiz", 1, "🧠"),
    ("meme_1", "梗图制造机", "制作第一张梗图", "memes", 1, "😂"),
    ("dex_20", "图鉴收集者", "图鉴解锁 20 张", "collection", 20, "🐸"),
    ("match_1", "对上了", "完成第一局对对碰", "matches", 1, "🎴"),
    ("checkin_1", "今日已躺", "完成第一次签到", "streak", 1, "📅"),
    ("streak_7", "一周佛系", "连续签到 7 天", "streak", 7, "🧘"),
    ("daily_draw_1", "今日赠礼", "领取第一次每日赠抽", "daily_draws", 1, "🎁"),
]


def seed_database(db, manifest: Path | None = None) -> tuple[int, int]:
    catalog = json.loads((manifest or image_manifest_path()).read_text(encoding="utf-8"))["images"]
    known = set(db.scalars(select(Image.filename)).all())
    for order, item in enumerate(catalog):
        if item["filename"] not in known:
            db.add(Image(filename=item["filename"], category=item["category"],
                         extension=item["extension"], sort_order=order))
    known_achievements = set(db.scalars(select(Achievement.code)).all())
    for code, name, description, condition_type, value, icon in ACHIEVEMENTS:
        if code not in known_achievements:
            db.add(Achievement(code=code, name=name, description=description, icon=icon,
                               condition_type=condition_type, condition_value=value))
    db.commit()
    return len(catalog), len(ACHIEVEMENTS)


def main():
    with SessionLocal() as db:
        image_count, achievement_count = seed_database(db)
        print(f"Seed complete: {image_count} images, {achievement_count} achievements")


if __name__ == "__main__":
    main()
