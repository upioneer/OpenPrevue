"""Pydantic models for System Settings."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SettingItem(BaseModel):
    """Single key-value setting pair."""
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: str
    updated_at: str | datetime | None = None


class SettingUpdate(BaseModel):
    """Payload for updating a setting value."""
    value: str


class SettingsDictionary(BaseModel):
    """Dictionary mapping of all active settings."""
    settings: dict[str, str]
