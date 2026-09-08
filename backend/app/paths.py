import sys
from pathlib import Path


def resource_root() -> Path:
    """Return the source root or PyInstaller bundle resource root."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


def frontend_dist_dir() -> Path:
    return resource_root() / "frontend" / "dist"


def images_dir() -> Path:
    return resource_root() / "images"


def image_manifest_path() -> Path:
    bundled = frontend_dist_dir() / "images.json"
    if bundled.exists():
        return bundled
    return resource_root() / "frontend" / "public" / "images.json"
