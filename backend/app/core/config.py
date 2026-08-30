"""Application configuration settings."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application settings loaded from environment or defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server parameters
    PORT: int = 8080
    HOST: str = "0.0.0.0"
    TZ: str = "America/Chicago"
    DATA_DIR: str = "./data"
    LOG_LEVEL: str = "INFO"
    APP_ENV: str = "development"

    # Aggregator defaults
    DEFAULT_POSTAL_CODE: str = "70112"
    DEFAULT_METRO_LABEL: str = "NEW ORLEANS"
    DEFAULT_LATITUDE: float = 29.9511
    DEFAULT_LONGITUDE: float = -90.0715
    DEFAULT_RADIUS_MILES: float = 35.0

    # Optional provider credentials
    TICKETMASTER_API_KEY: str | None = None
    SEATGEEK_CLIENT_ID: str | None = None
    SEATGEEK_CLIENT_SECRET: str | None = None
    EVENTBRITE_API_TOKEN: str | None = None

    # Optional Telegram bot
    TELEGRAM_BOT_TOKEN: str | None = None

    @property
    def database_path(self) -> Path:
        """Resolved SQLite database file path."""
        data_directory = Path(self.DATA_DIR)
        data_directory.mkdir(parents=True, exist_ok=True)
        return data_directory / "openprevue.db"


settings = Settings()
