"""AI Ticket Parsing and Local Ollama Health & Ingestion Endpoints."""

import time
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/ai")


class OllamaPingRequest(BaseModel):
    """Payload for checking local Ollama instance heartbeat and model inventory."""
    ollama_url: str = Field(default="http://localhost:11434", description="Base URL of local Ollama server")
    model: str | None = Field(default=None, description="Optional model to probe")


class OllamaPingResponse(BaseModel):
    """Response payload with health, latency, and available local models."""
    status: str
    ollama_url: str
    latency_ms: int
    models: list[str]
    version: str | None = None
    error: str | None = None


@router.post("/ollama/ping", response_model=OllamaPingResponse)
async def ping_ollama_instance(req: OllamaPingRequest) -> OllamaPingResponse:
    """Test connectivity to a local Ollama server and enumerate available LLM models."""
    base_url = req.ollama_url.rstrip("/")
    start_time = time.perf_counter()

    try:
        async with httpx.AsyncClient(timeout=3.5) as client:
            # Query /api/tags for model inventory
            tags_res = await client.get(f"{base_url}/api/tags")
            latency = int((time.perf_counter() - start_time) * 1000)

            if tags_res.status_code == 200:
                data = tags_res.json()
                models = [m.get("name") for m in data.get("models", []) if "name" in m]

                # Optional: probe version endpoint
                version_str = None
                try:
                    ver_res = await client.get(f"{base_url}/api/version")
                    if ver_res.status_code == 200:
                        version_str = ver_res.json().get("version")
                except Exception:
                    pass

                return OllamaPingResponse(
                    status="online",
                    ollama_url=base_url,
                    latency_ms=max(1, latency),
                    models=models,
                    version=version_str,
                )
            else:
                return OllamaPingResponse(
                    status="error",
                    ollama_url=base_url,
                    latency_ms=max(1, latency),
                    models=[],
                    error=f"Ollama returned HTTP {tags_res.status_code}",
                )

    except httpx.ConnectError:
        latency = int((time.perf_counter() - start_time) * 1000)
        return OllamaPingResponse(
            status="offline",
            ollama_url=base_url,
            latency_ms=max(1, latency),
            models=[],
            error=f"Connection refused at {base_url}. Ensure Ollama is running and accessible.",
        )
    except httpx.TimeoutException:
        latency = int((time.perf_counter() - start_time) * 1000)
        return OllamaPingResponse(
            status="offline",
            ollama_url=base_url,
            latency_ms=max(1, latency),
            models=[],
            error=f"Connection timed out connecting to {base_url}.",
        )
    except Exception as e:
        latency = int((time.perf_counter() - start_time) * 1000)
        return OllamaPingResponse(
            status="error",
            ollama_url=base_url,
            latency_ms=max(1, latency),
            models=[],
            error=str(e),
        )
