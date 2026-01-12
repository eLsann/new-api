import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # --- app ---
    app_name: str = os.getenv("APP_NAME", "Project Absensi API")
    env: str = os.getenv("ENV", "dev")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./absensi.db").strip()

    @property
    def DATABASE_URL(self) -> str:
        return self.database_url

    # --- security/admin ---
    secret_key: str = os.getenv("SECRET_KEY", "").strip()
    admin_token_expire_hours: int = int(os.getenv("ADMIN_TOKEN_EXPIRE_HOURS", "12"))

    @property
    def SECRET_KEY(self) -> str:
        return self.secret_key

    @property
    def ADMIN_TOKEN_EXPIRE_HOURS(self) -> int:
        return self.admin_token_expire_hours

    # --- device tokens ---
    device_tokens: str = os.getenv("DEVICE_TOKENS", "").strip()

    @property
    def DEVICE_TOKENS(self) -> str:
        return self.device_tokens

    # --- face recognition ---
    max_distance: float = float(os.getenv("MAX_DISTANCE", "0.95"))
    min_face_px: int = int(os.getenv("MIN_FACE_PX", "90"))

    @property
    def MAX_DISTANCE(self) -> float:
        return self.max_distance

    @property
    def MIN_FACE_PX(self) -> int:
        return self.min_face_px

    # --- attendance/cooldown ---
    cooldown_seconds: int = int(os.getenv("COOLDOWN_SECONDS", "45"))

    @property
    def COOLDOWN_SECONDS(self) -> int:
        return self.cooldown_seconds

    # --- snapshots ---
    save_snapshots: bool = os.getenv("SAVE_SNAPSHOTS", "true").lower() in ("true", "1", "yes")
    snapshot_dir: str = os.getenv("SNAPSHOT_DIR", "./data/snapshots").strip()
    snapshot_on_unknown: bool = os.getenv("SNAPSHOT_ON_UNKNOWN", "true").lower() in ("true", "1", "yes")
    snapshot_on_low_conf: bool = os.getenv("SNAPSHOT_ON_LOW_CONF", "true").lower() in ("true", "1", "yes")
    low_conf_distance: float = float(os.getenv("LOW_CONF_DISTANCE", "0.85"))

    @property
    def SAVE_SNAPSHOTS(self) -> bool:
        return self.save_snapshots

    @property
    def SNAPSHOT_DIR(self) -> str:
        return self.snapshot_dir

    @property
    def SNAPSHOT_ON_UNKNOWN(self) -> bool:
        return self.snapshot_on_unknown

    @property
    def SNAPSHOT_ON_LOW_CONF(self) -> bool:
        return self.snapshot_on_low_conf

    @property
    def LOW_CONF_DISTANCE(self) -> float:
        return self.low_conf_distance


settings = Settings()

if not settings.secret_key:
    raise RuntimeError("SECRET_KEY not set. Please configure it in .env file")
