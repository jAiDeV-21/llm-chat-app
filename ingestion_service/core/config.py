import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None


if load_dotenv:
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")


def _get_int(name: str, default: int) -> int:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    return int(raw_value)


def _get_float(name: str, default: float) -> float:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    return float(raw_value)


@dataclass(frozen=True)
class Settings:
    supabase_url: Optional[str]
    supabase_key: Optional[str]
    supabase_table: str
    max_batch_size: int
    flush_interval_seconds: float


settings = Settings(
    supabase_url=os.environ.get("SUPABASE_URL"),
    supabase_key=os.environ.get("SUPABASE_KEY"),
    supabase_table=os.environ.get("SUPABASE_TABLE", "inference_logs"),
    max_batch_size=_get_int("MAX_BATCH_SIZE", 100),
    flush_interval_seconds=_get_float("FLUSH_INTERVAL_SECONDS", 1.0),
)
