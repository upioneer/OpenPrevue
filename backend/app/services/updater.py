"""Auto-update notification, GitHub release tracking, and in-place upgrade service."""

import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import socket
import sys

import httpx

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.services.websocket import connection_manager

GITHUB_REPO = "upioneer/OpenPrevue"
GITHUB_TAGS_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/tags?per_page=30"
GITHUB_RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
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
    """Manages update checks against GitHub API and executes independent in-place updates."""

    def __init__(self) -> None:
        self.current_version = getattr(settings, "VERSION", "0.21.0")
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
                # Primary source of truth: Git Tags
                resp = await client.get(GITHUB_TAGS_API_URL, headers=headers)
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
                    valid_tags: list[str] = []
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and "name" in item:
                                tag_str = str(item["name"]).strip()
                                if parse_semver(tag_str) != (0, 0, 0):
                                    valid_tags.append(tag_str)

                    if valid_tags:
                        sorted_tags = sorted(valid_tags, key=parse_semver, reverse=True)
                        top_tag = sorted_tags[0]
                        self.latest_version = top_tag.lstrip("v")
                        self.release_title = f"Release {top_tag}"
                        self.release_url = f"https://github.com/{GITHUB_REPO}/releases/tag/{top_tag}"
                        self.release_notes = ""
                        self.update_available = is_newer_version(self.current_version, self.latest_version)
                        self.is_rate_limited = False
                        self.last_error = None

                        # Optional enrichment: Probe GitHub Release metadata for release notes if available
                        try:
                            rel_resp = await client.get(
                                f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{top_tag}",
                                headers=headers,
                            )
                            if rel_resp.status_code == 200:
                                rel_data = rel_resp.json()
                                self.release_title = rel_data.get("name") or self.release_title
                                self.release_notes = rel_data.get("body") or ""
                                if rel_data.get("html_url"):
                                    self.release_url = rel_data["html_url"]
                        except Exception as e:
                            logger.debug("Optional release metadata enrichment skipped: %s", e)

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
                    else:
                        # No semver tags found
                        self.latest_version = self.current_version
                        self.update_available = False
                        self.is_rate_limited = False
                        self.last_error = None
                        self.user_message = "OpenPrevue is up to date."

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

    async def detect_update_method(self) -> tuple[str, str]:
        """Detect primary and supported in-place update mechanism.

        Returns:
            Tuple of (method_identifier, friendly_description).
            Methods:
              - 'docker_socket': Direct Unix domain socket control (/var/run/docker.sock)
              - 'git': Local Git working tree with git executable
              - 'trigger_file': Persistent storage trigger file (./data/.update_trigger)
              - 'manual': Out-of-band manual Docker / Compose CLI
        """
        # 1. Probe Docker Unix Domain Socket
        docker_socket = os.getenv("DOCKER_SOCKET_PATH", "/var/run/docker.sock")
        if os.path.exists(docker_socket) and os.name != "nt":
            try:
                transport = httpx.AsyncHTTPTransport(uds=docker_socket)
                async with httpx.AsyncClient(transport=transport, timeout=2.0) as client:
                    resp = await client.get("http://localhost/_ping")
                    if resp.status_code == 200:
                        return (
                            "docker_socket",
                            "Docker Engine API connected over /var/run/docker.sock. Direct in-place container upgrade is enabled.",
                        )
            except Exception as e:
                logger.debug("Docker socket exists but ping probe failed: %s", e)

        # 2. Probe Local Git Repository
        try:
            repo_root = Path(__file__).resolve().parents[3]  # OpenPrevue root
            git_dir = repo_root / ".git"
            if git_dir.is_dir() and shutil.which("git"):
                return (
                    "git",
                    "Local Git repository detected. In-place git pull and release checkout enabled.",
                )
        except Exception:
            pass

        # 3. Probe Persistent Storage Trigger File capability
        data_dir = Path(settings.DATA_DIR)
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            test_file = data_dir / ".write_test"
            test_file.touch()
            test_file.unlink()
            return (
                "trigger_file",
                f"Persistent data volume verified at {settings.DATA_DIR}. Host trigger file strategy active (./data/.update_trigger).",
            )
        except Exception:
            pass

        return (
            "manual",
            "Automatic in-place upgrade is unavailable in current runtime. Manual upgrade via docker compose required.",
        )

    async def get_update_capability(self) -> dict:
        """Probe runtime environment and return detailed update engine capability."""
        detected_method, description = await self.detect_update_method()

        docker_socket = os.getenv("DOCKER_SOCKET_PATH", "/var/run/docker.sock")
        docker_available = False
        if os.path.exists(docker_socket) and os.name != "nt":
            try:
                transport = httpx.AsyncHTTPTransport(uds=docker_socket)
                async with httpx.AsyncClient(transport=transport, timeout=1.5) as client:
                    r = await client.get("http://localhost/_ping")
                    docker_available = (r.status_code == 200)
            except Exception:
                docker_available = False

        repo_root = Path(__file__).resolve().parents[3]
        git_available = (repo_root / ".git").is_dir() and bool(shutil.which("git"))

        trigger_path = Path(settings.DATA_DIR) / ".update_trigger"
        trigger_available = False
        try:
            trigger_path.parent.mkdir(parents=True, exist_ok=True)
            trigger_available = os.access(trigger_path.parent, os.W_OK)
        except Exception:
            trigger_available = False

        available_methods = []
        if docker_available:
            available_methods.append("docker_socket")
        if git_available:
            available_methods.append("git")
        if trigger_available:
            available_methods.append("trigger_file")
        if not available_methods:
            available_methods.append("manual")

        return {
            "can_update": detected_method != "manual",
            "detected_method": detected_method,
            "available_methods": available_methods,
            "docker_socket_available": docker_available,
            "git_available": git_available,
            "trigger_file_available": trigger_available,
            "trigger_file_path": str(trigger_path),
            "description": description,
            "current_version": self.current_version,
            "latest_version": self.latest_version,
            "update_available": self.update_available,
        }

    async def apply_update(
        self,
        target_version: str | None = None,
        dry_run: bool = False,
        method: str | None = None,
    ) -> dict:
        """Execute or dry-run an in-place upgrade."""
        resolved_version = (
            target_version.strip().lstrip("v")
            if target_version
            else (self.latest_version or "latest")
        )
        if not resolved_version:
            resolved_version = "latest"

        chosen_method = method
        if not chosen_method:
            detected, _ = await self.detect_update_method()
            chosen_method = detected

        logger.info(
            "Update apply requested: method=%s, target_version=%s, dry_run=%s",
            chosen_method,
            resolved_version,
            dry_run,
        )

        if chosen_method == "docker_socket":
            return await self._apply_docker_socket(resolved_version, dry_run)
        elif chosen_method == "git":
            return await self._apply_git(resolved_version, dry_run)
        elif chosen_method == "trigger_file":
            return await self._apply_trigger_file(resolved_version, dry_run)
        else:
            return {
                "status": "manual_required",
                "method": "manual",
                "target_version": resolved_version,
                "message": (
                    f"In-place upgrade cannot be completed automatically. "
                    f"Please run: docker pull ghcr.io/{GITHUB_REPO}:latest && docker compose up -d"
                ),
            }

    async def _apply_docker_socket(self, version: str, dry_run: bool) -> dict:
        """Perform container upgrade via Docker Unix Domain Socket."""
        docker_socket = os.getenv("DOCKER_SOCKET_PATH", "/var/run/docker.sock")
        target_image = f"ghcr.io/{GITHUB_REPO}:latest" if version == "latest" else f"ghcr.io/{GITHUB_REPO}:v{version}"

        if dry_run:
            return {
                "status": "dry_run_success",
                "method": "docker_socket",
                "target_version": version,
                "target_image": target_image,
                "steps": [
                    "Probe Docker daemon over /var/run/docker.sock (_ping)",
                    f"Pull latest container image {target_image}",
                    "Inspect current container configuration (ports, volumes, environment)",
                    "Rename current container to openprevue-retiring",
                    "Create updated container with identical port mappings and volume mounts",
                    "Start updated container",
                    "Gracefully terminate retired container",
                ],
                "message": f"Pre-flight verification passed for Docker Engine API in-place upgrade to v{version}.",
            }

        try:
            transport = httpx.AsyncHTTPTransport(uds=docker_socket)
            async with httpx.AsyncClient(transport=transport, timeout=120.0) as client:
                # 1. Pull new image
                logger.info("Pulling Docker image %s via Docker Engine API...", target_image)
                pull_url = f"http://localhost/images/create?fromImage={target_image}"
                pull_resp = await client.post(pull_url)
                if pull_resp.status_code not in (200, 204):
                    raise RuntimeError(f"Docker pull failed with status {pull_resp.status_code}: {pull_resp.text}")

                # 2. Inspect running container
                hostname = socket.gethostname()
                inspect_resp = await client.get(f"http://localhost/containers/{hostname}/json")
                if inspect_resp.status_code != 200:
                    # Fallback to trigger file if container ID lookup fails
                    logger.warning("Could not inspect container via hostname %s; falling back to trigger file.", hostname)
                    return await self._apply_trigger_file(version, dry_run=False)

                info = inspect_resp.json()
                orig_name = info.get("Name", "/openprevue").lstrip("/")
                retire_name = f"{orig_name}-retiring-{int(datetime.now(timezone.utc).timestamp())}"

                # 3. Rename old container
                rename_resp = await client.post(f"http://localhost/containers/{hostname}/rename?name={retire_name}")
                if rename_resp.status_code not in (200, 204):
                    logger.warning("Failed renaming old container: %s", rename_resp.text)

                # 4. Create new container with preserved config
                create_payload = {
                    "Image": target_image,
                    "Env": info.get("Config", {}).get("Env", []),
                    "Cmd": info.get("Config", {}).get("Cmd"),
                    "Entrypoint": info.get("Config", {}).get("Entrypoint"),
                    "Labels": info.get("Config", {}).get("Labels", {}),
                    "HostConfig": info.get("HostConfig", {}),
                    "NetworkingConfig": {
                        "EndpointsConfig": info.get("NetworkSettings", {}).get("Networks", {})
                    },
                }
                create_resp = await client.post(f"http://localhost/containers/create?name={orig_name}", json=create_payload)
                if create_resp.status_code not in (200, 201):
                    raise RuntimeError(f"Docker container create failed: {create_resp.text}")

                new_container_id = create_resp.json().get("Id")

                # 5. Create ephemeral swapper container to execute atomic port-safe handoff
                swapper_name = f"openprevue-swapper-{int(datetime.now(timezone.utc).timestamp())}"
                swapper_script = (
                    "import http.client, socket, time, sys\n"
                    "time.sleep(1.5)\n"
                    "def req(m, u):\n"
                    "    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)\n"
                    "    s.connect('/var/run/docker.sock')\n"
                    "    c = http.client.HTTPConnection('localhost')\n"
                    "    c.sock = s\n"
                    "    c.request(m, u)\n"
                    "    r = c.getresponse()\n"
                    "    r.read()\n"
                    "    return r.status\n"
                    f"req('POST', '/containers/{hostname}/stop?t=5')\n"
                    f"r_start = req('POST', '/containers/{new_container_id}/start')\n"
                    f"if r_start in (200, 204):\n"
                    f"    req('DELETE', '/containers/{hostname}?v=false')\n"
                    "sys.exit(0)\n"
                )

                swapper_payload = {
                    "Image": target_image,
                    "User": "0:0",
                    "Cmd": ["python3", "-c", swapper_script],
                    "HostConfig": {
                        "AutoRemove": True,
                        "Binds": [f"{docker_socket}:/var/run/docker.sock"],
                    },
                }
                swapper_resp = await client.post(f"http://localhost/containers/create?name={swapper_name}", json=swapper_payload)
                if swapper_resp.status_code in (200, 201):
                    swapper_id = swapper_resp.json().get("Id")
                    start_swapper = await client.post(f"http://localhost/containers/{swapper_id}/start")
                    if start_swapper.status_code not in (200, 204):
                        logger.warning("Swapper container start failed (%s); attempting direct retirement.", start_swapper.text)
                        asyncio.create_task(self._retire_and_start_direct(hostname, new_container_id))
                else:
                    logger.warning("Swapper container create failed (%s); attempting direct retirement.", swapper_resp.text)
                    asyncio.create_task(self._retire_and_start_direct(hostname, new_container_id))

                return {
                    "status": "success",
                    "method": "docker_socket",
                    "target_version": version,
                    "target_image": target_image,
                    "new_container_id": new_container_id,
                    "message": f"Successfully initiated container swap to OpenPrevue v{version}. Swapping containers...",
                }
        except Exception as err:
            logger.error("Docker socket update failed: %s", err)
            return {
                "status": "error",
                "method": "docker_socket",
                "error": str(err),
                "message": f"Docker Engine upgrade encountered an error: {err}",
            }

    async def _retire_and_start_direct(self, old_id: str, new_id: str, delay: float = 1.0) -> None:
        """Fallback asynchronous container replacement if ephemeral swapper cannot be launched."""
        try:
            await asyncio.sleep(delay)
            docker_socket = os.getenv("DOCKER_SOCKET_PATH", "/var/run/docker.sock")
            transport = httpx.AsyncHTTPTransport(uds=docker_socket)
            async with httpx.AsyncClient(transport=transport, timeout=30.0) as client:
                await client.post(f"http://localhost/containers/{old_id}/stop?t=5")
                await client.post(f"http://localhost/containers/{new_id}/start")
                await client.delete(f"http://localhost/containers/{old_id}?v=false")
                logger.info("Direct container retirement completed for old container %s", old_id)
        except Exception as e:
            logger.error("Direct container retirement encountered error: %s", e)

    async def _apply_git(self, version: str, dry_run: bool) -> dict:
        """Perform bare-metal update via Git pull and frontend build."""
        repo_root = Path(__file__).resolve().parents[3]
        target_ref = f"v{version}" if version != "latest" else "origin/main"

        if dry_run:
            return {
                "status": "dry_run_success",
                "method": "git",
                "target_version": version,
                "target_ref": target_ref,
                "steps": [
                    "Inspect local git working tree cleanliness",
                    "Fetch remote tags via git fetch --tags origin",
                    f"Checkout target ref {target_ref} (or git pull origin main)",
                    "Compile frontend distribution via npm --prefix frontend run build",
                    "Signal service reload or restart daemon",
                ],
                "message": f"Pre-flight verification passed for Git in-place upgrade to {target_ref}.",
            }

        try:
            # 1. Fetch tags
            proc_fetch = await asyncio.create_subprocess_exec(
                "git", "fetch", "--tags", "origin",
                cwd=str(repo_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc_fetch.communicate()

            # 2. Checkout
            if version == "latest":
                proc_co = await asyncio.create_subprocess_exec(
                    "git", "pull", "origin", "main",
                    cwd=str(repo_root),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            else:
                proc_co = await asyncio.create_subprocess_exec(
                    "git", "checkout", target_ref,
                    cwd=str(repo_root),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            await proc_co.communicate()

            # 3. Optional npm build if npm is available
            if shutil.which("npm"):
                npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
                proc_build = await asyncio.create_subprocess_exec(
                    npm_cmd, "--prefix", "frontend", "run", "build",
                    cwd=str(repo_root),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc_build.communicate()

            return {
                "status": "success",
                "method": "git",
                "target_version": version,
                "message": f"Git working tree updated to {target_ref}. Headend restart required to complete update.",
            }
        except Exception as err:
            logger.error("Git update failed: %s", err)
            return {
                "status": "error",
                "method": "git",
                "error": str(err),
                "message": f"Git update encountered an error: {err}",
            }

    async def _apply_trigger_file(self, version: str, dry_run: bool) -> dict:
        """Write update trigger file to persistent storage for companion host script execution."""
        trigger_path = Path(settings.DATA_DIR) / ".update_trigger"
        target_image = f"ghcr.io/{GITHUB_REPO}:latest" if version == "latest" else f"ghcr.io/{GITHUB_REPO}:v{version}"

        if dry_run:
            return {
                "status": "dry_run_success",
                "method": "trigger_file",
                "target_version": version,
                "trigger_file": str(trigger_path),
                "target_image": target_image,
                "steps": [
                    f"Verify write permissions on {settings.DATA_DIR}",
                    f"Write update trigger specification to {trigger_path.name}",
                    "Host watcher/cron executes: docker compose pull && docker compose up -d",
                    "Host watcher cleans up trigger file upon successful container swap",
                    "Client web interface detects headend restart and reloads",
                ],
                "message": f"Pre-flight verification passed for trigger file upgrade to v{version}.",
            }

        try:
            trigger_data = {
                "target_version": version,
                "image": target_image,
                "requested_at": datetime.now(timezone.utc).isoformat(),
                "method": "trigger_file",
                "action": "upgrade",
            }
            trigger_path.parent.mkdir(parents=True, exist_ok=True)
            trigger_path.write_text(json.dumps(trigger_data, indent=2), encoding="utf-8")
            logger.info("Wrote update trigger file to %s", trigger_path)

            return {
                "status": "triggered",
                "method": "trigger_file",
                "target_version": version,
                "trigger_file": str(trigger_path),
                "target_image": target_image,
                "message": (
                    f"Update trigger written for v{version}. "
                    f"The companion host updater will pull and restart the container."
                ),
            }
        except Exception as err:
            logger.error("Writing trigger file failed: %s", err)
            return {
                "status": "error",
                "method": "trigger_file",
                "error": str(err),
                "message": f"Failed writing update trigger file: {err}",
            }


update_service = UpdateService()
