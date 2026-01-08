import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # --- app ---
    app_name: str = os.getenv("APP_NAME", "Project Absensi API")
    env: str = os.getenv("ENV", "dev")

    # --- database ---
    # simpan canonical di snake_case
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./absensi.db").strip()

    # alias kompatibilitas (kalau ada kode lama pakai DATABASE_URL)
    @property
    def DATABASE_URL(self) -> str:
        return self.database_url

    # --- security/admin ---
    secret_key: str = os.getenv("SECRET_KEY", "").strip()
    admin_token_expire_hours: int = int(os.getenv("ADMIN_TOKEN_EXPIRE_HOURS", "12"))
    setup_token: str = os.getenv("SETUP_TOKEN", "").strip()

    @property
    def SECRET_KEY(self) -> str:
        return self.secret_key

    @property
    def ADMIN_TOKEN_EXPIRE_HOURS(self) -> int:
        return self.admin_token_expire_hours

    @property
    def SETUP_TOKEN(self) -> str:
        return self.setup_token

    # --- device tokens ---
    device_tokens: str = os.getenv("DEVICE_TOKENS", "").strip()

    @property
    def DEVICE_TOKENS(self) -> str:
        return self.device_tokens


settings = Settings()

if not settings.secret_key:
    raise RuntimeError("SECRET_KEY belum di-set. Isi SECRET_KEY di file .env")
