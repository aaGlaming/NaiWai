import ctypes
import json
import logging
import multiprocessing
import os
import secrets
import socket
import sqlite3
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen


if not getattr(sys, "frozen", False):
    backend_dir = Path(__file__).resolve().parents[1] / "backend"
    sys.path.insert(0, str(backend_dir))


APP_NAME = "NAIWA"
MUTEX_NAME = "Local\\NAIWA-Desktop-8F9A30F4"


def app_data_dir() -> Path:
    override = os.environ.get("NAIWA_DATA_DIR")
    if override:
        result = Path(override).resolve()
    else:
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        result = base / APP_NAME
    (result / "data").mkdir(parents=True, exist_ok=True)
    (result / "backups").mkdir(parents=True, exist_ok=True)
    (result / "logs").mkdir(parents=True, exist_ok=True)
    return result


def configure_environment(data_dir: Path) -> Path:
    database_path = data_dir / "data" / "naiwa.db"
    settings_path = data_dir / "settings.json"
    try:
        saved = json.loads(settings_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        saved = {"secret_key": secrets.token_hex(32)}
        settings_path.write_text(json.dumps(saved, ensure_ascii=False, indent=2), encoding="utf-8")
    os.environ["DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
    os.environ["SECRET_KEY"] = saved["secret_key"]
    os.environ["DESKTOP_MODE"] = "true"
    os.environ["COOKIE_SECURE"] = "false"
    return database_path


def acquire_single_instance():
    if sys.platform != "win32":
        return None
    handle = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if ctypes.windll.kernel32.GetLastError() == 183:
        ctypes.windll.user32.MessageBoxW(None, "奶蛙世界已经在运行。", "NAIWA", 0x40)
        return False
    return handle


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_until_ready(url: str, timeout: float = 20) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError("本地服务启动超时")


class DesktopApi:
    def __init__(self, database_path: Path, data_dir: Path):
        self.database_path = database_path
        self.data_dir = data_dir

    @staticmethod
    def _window():
        import webview
        return webview.active_window() or webview.windows[0]

    def app_info(self):
        return {"desktop": True, "version": "1.0.0", "data_dir": str(self.data_dir)}

    def backup_data(self):
        import webview
        default_name = f"naiwa-backup-{datetime.now():%Y%m%d-%H%M%S}.db"
        selected = self._window().create_file_dialog(
            webview.SAVE_DIALOG,
            directory=str(self.data_dir / "backups"),
            save_filename=default_name,
            file_types=("NAIWA database (*.db)",),
        )
        if not selected:
            return {"success": False, "cancelled": True}
        destination = Path(selected[0])
        with sqlite3.connect(self.database_path) as source, sqlite3.connect(destination) as target:
            source.backup(target)
        return {"success": True, "path": str(destination)}

    def restore_data(self):
        import webview
        selected = self._window().create_file_dialog(
            webview.OPEN_DIALOG,
            directory=str(self.data_dir / "backups"),
            file_types=("NAIWA database (*.db)",),
        )
        if not selected:
            return {"success": False, "cancelled": True}
        source_path = Path(selected[0])
        try:
            with sqlite3.connect(f"file:{source_path.as_posix()}?mode=ro", uri=True) as check:
                if check.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("数据库完整性检查失败")
                tables = {row[0] for row in check.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if not {"users", "images", "user_stats"}.issubset(tables):
                    raise ValueError("不是有效的奶蛙世界备份")
            if not self._window().create_confirmation_dialog("恢复数据", "恢复会覆盖当前本地数据，是否继续？"):
                return {"success": False, "cancelled": True}
            from app.database import get_engine
            get_engine().dispose()
            with sqlite3.connect(source_path) as source, sqlite3.connect(self.database_path) as target:
                source.backup(target)
            return {"success": True, "restart_required": True}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def open_data_folder(self):
        if sys.platform == "win32":
            os.startfile(self.data_dir)
        return {"success": True}


def initialize_database() -> None:
    from app import models  # noqa: F401
    from app.database import Base, get_engine, get_session_factory
    from scripts.seed_data import seed_database

    Base.metadata.create_all(get_engine())
    with get_session_factory()() as db:
        seed_database(db)


def smoke_test(database_path: Path) -> None:
    from app.database import get_session_factory
    from app.models import Achievement, Image, User
    from app.paths import frontend_dist_dir, image_manifest_path

    if not database_path.is_file():
        raise RuntimeError("Desktop database was not created")
    if not (frontend_dist_dir() / "index.html").is_file():
        raise RuntimeError("Frontend build is missing")
    if not image_manifest_path().is_file():
        raise RuntimeError("Image manifest is missing")
    with get_session_factory()() as db:
        if db.query(Image).count() < 1 or db.query(Achievement).count() < 1:
            raise RuntimeError("Initial desktop data was not seeded")
        db.query(User).count()


def run() -> int:
    instance = acquire_single_instance()
    if instance is False:
        return 0
    data_dir = app_data_dir()
    database_path = configure_environment(data_dir)
    logging.basicConfig(filename=data_dir / "logs" / "naiwa.log", level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")
    initialize_database()

    if "--smoke-test" in sys.argv:
        smoke_test(database_path)
        if instance and sys.platform == "win32":
            ctypes.windll.kernel32.CloseHandle(instance)
        return 0

    import uvicorn
    import webview
    from app.main import app

    port = find_free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, name="naiwa-api", daemon=True)
    thread.start()
    health_url = f"http://127.0.0.1:{port}/api/health"
    wait_until_ready(health_url)

    api = DesktopApi(database_path, data_dir)
    webview.create_window("奶蛙世界", f"http://127.0.0.1:{port}/api/v1/auth/desktop-login",
                          js_api=api, width=1280, height=820, min_size=(900, 620),
                          background_color="#F4F0E8")
    try:
        webview.start(debug=False)
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        if instance and sys.platform == "win32":
            ctypes.windll.kernel32.CloseHandle(instance)
    return 0


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(run())
