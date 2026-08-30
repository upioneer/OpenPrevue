"""Auto-update notification and GitHub release tracking service."""

from datetime import datetime, timezone
import httpx
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.services.websocket import connection_manager

GITHUB_REPO = "upioneer/OpenPrevue"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
CACHE_TTL_SECONDS = 6 * 3600  # 6 hours minimum cache to prevent rate limit exhaustion


def parse_semver(version_str: str) -> tuple[int, int, int]:
    """Parse semantic version string (e.g., 'v0.15.0' or '0.15.0') into an integer tuple."""
    cleaned = version_str.strip().lstrip("v")
    parts = cleaned.split(".")
    try:
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2].split("-")[0]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except (ValueError, IndexError):
        return (0, 0, 0)


def is_newer_version(current: str, latest: str) -> bool:
    """Return True if latest version is strictly greater than current version."""
    curr_tuple = parse_semver(current)
    latest_tuple = parse_semver(latest)
    return latest_tuple > curr_tuple


class UpdateService:
    """Manages update checks against GitHub API with caching and rate limit protection."""

    def __init__(self) -> None:
        self.current_version = getattr(settings, "VERSION", "0.15.0")
        self.last_checked: datetime | None = None
        self.latest_version: str = self.current_version
        self.update_available: bool = False
        self.release_url: str = f"https://github.com/{GITHUB_REPO}/releases"
        self.release_notes: str = ""
        self.release_title: str = ""
        self.rate_limit_remaining: int | None = None
        self.rate_limit_reset_minutes: int | None = None
        self.is_rate_limited: bool = False
        self.user_message: str | None = None
        self.last_error: str | None = None

    async def get_update_interval_setting(self) -> str:
        """Fetch configured update check interval from database ('weekly', 'daily', 'on_boot', 'disabled')."""
        try:
            async with get_db() as db:
                async with db.execute("SELECT value FROM settings WHERE key = 'update_check_interval'") as cursor:
                    row = await cursor.fetchone()
                    if row and row["value"]:
                        return row["value"]
        except Exception as e:
            logger.debug("Failed reading update_check_interval setting: %s", e)
        return "disabled"

    async def get_status(self) -> dict:
        """Return current cached update status with plain-English user messaging."""
        interval = await self.get_update_interval_setting()
        return {
            "current_version": self.current_version,
            "latest_version": self.latest_version,
            "update_available": self.update_available,
            "release_url": self.release_url,
            "release_title": self.release_title,
            "release_notes": self.release_notes,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "update_check_interval": interval,
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset_minutes": self.rate_limit_reset_minutes,
            "is_rate_limited": self.is_rate_limited,
            "user_message": self.user_message,
            "last_error": self.last_error,
        }

    async def check_for_updates(self, force: bool = False) -> dict:
        """Probe GitHub API for the latest release with rate-limit and TTL caching."""
        interval = await self.get_update_interval_setting()

        if interval == "disabled" and not force:
            logger.debug("Automatic update check is disabled in settings.")
            self.user_message = "Automatic update checking is turned off."
            return await self.get_status()

        # Check in-memory cache TTL
        now = datetime.now(timezone.utc)
        if not force and self.last_checked:
            elapsed = (now - self.last_checked).total_seconds()
            if elapsed < CACHE_TTL_SECONDS:
                logger.debug("Returning cached update status (checked %ds ago).", int(elapsed))
                return await self.get_status()

        logger.info("Checking GitHub for OpenPrevue updates (Current: v%s)...", self.current_version)
        headers = {
            "User-Agent": f"OpenPrevue-Updater/{self.current_version}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(GITHUB_API_URL, headers=headers)
                self.last_checked = now

                # Track rate limit headers
                if "x-ratelimit-remaining" in resp.headers:
                    try:
                        self.rate_limit_remaining = int(resp.headers["x-ratelimit-remaining"])
                    except ValueError:
                        pass

                if "x-ratelimit-reset" in resp.headers:
                    try:
                        reset_epoch = int(resp.headers["x-ratelimit-reset"])
                        reset_dt = datetime.fromtimestamp(reset_epoch, tz=timezone.utc)
                        mins = max(1, int((reset_dt - now).total_seconds() / 60))
                        self.rate_limit_reset_minutes = mins
                    except Exception:
                        self.rate_limit_reset_minutes = 60

                if resp.status_code == 200:
                    data = resp.json()
                    tag_name = data.get("tag_name", "").strip()
                    self.latest_version = tag_name.lstrip("v")
                    self.release_title = data.get("name", f"Release {tag_name}")
                    self.release_notes = data.get("body", "")
                    self.release_url = data.get("html_url", f"https://github.com/{GITHUB_REPO}/releases")
                    self.update_available = is_newer_version(self.current_version, self.latest_version)
                    self.is_rate_limited = False
                    self.last_error = None

                    if self.update_available:
                        self.user_message = f"A new version of OpenPrevue (v{self.latest_version}) is available."
                        logger.info(
                            "New OpenPrevue version available: v%s (Current: v%s)",
                            self.latest_version,
                            self.current_version,
                        )
                        # Broadcast update notification to connected UI clients
                        await connection_manager.broadcast(
                            "update_available",
                            {
                                "current_version": self.current_version,
                                "latest_version": self.latest_version,
                                "release_url": self.release_url,
                                "release_title": self.release_title,
                            },
                        )
                    else:
                        self.user_message = f"OpenPrevue is running the newest version (v{self.current_version})."
                        logger.info("OpenPrevue is up to date (v%s).", self.current_version)

                elif resp.status_code in (403, 429):
                    self.is_rate_limited = True
                    mins = self.rate_limit_reset_minutes or 60
                    self.user_message = (
                        f"You have checked for updates too many times recently. "
                        f"GitHub has paused requests for a bit. Please wait about {mins} minutes before checking again."
                    )
                    self.last_error = "Rate limit temporarily exceeded."
                    logger.warning("GitHub API rate limit reached during update check.")

                elif resp.status_code == 404:
                    self.latest_version = self.current_version
                    self.update_available = False
                    self.is_rate_limited = False
                    self.last_error = None
                    self.user_message = "OpenPrevue is up to date."

                elif resp.status_code >= 500:
                    self.is_rate_limited = False
                    self.user_message = (
                        "GitHub is temporarily having trouble responding. "
                        "Your current installation is working normally, and we will check again later."
                    )
                    self.last_error = "GitHub server is temporarily unavailable."
                    logger.warning("GitHub API returned server error status %d", resp.status_code)

                else:
                    self.is_rate_limited = False
                    self.user_message = "Could not complete the update check right now. We will check again later."
                    self.last_error = f"Update probe returned status {resp.status_code}"
                    logger.warning("Update check failed with status %d: %s", resp.status_code, resp.text)

        except (httpx.ConnectError, httpx.TimeoutException) as conn_err:
            self.last_checked = now
            self.is_rate_limited = False
            self.user_message = "Could not connect to GitHub to check for updates. Please check your internet connection and try again."
            self.last_error = "Connection timeout or unreachable."
            logger.warning("Network connection error during update check: %s", conn_err)

        except Exception as err:
            self.last_checked = now
            self.is_rate_limited = False
            self.user_message = "Could not check for updates right now. Please try again in a few moments."
            self.last_error = str(err)
            logger.warning("Unexpected error during update probe: %s", err)

        return await self.get_status()


update_service = UpdateService()
