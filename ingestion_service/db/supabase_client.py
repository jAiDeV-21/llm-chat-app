import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

try:
    from supabase import Client, create_client
except ModuleNotFoundError:
    Client = None
    create_client = None


if load_dotenv:
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")


SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_TABLE = os.environ.get("SUPABASE_TABLE", "inference_logs")
supabase_client: Optional[Client] = None


def create_supabase_client() -> Optional[Client]:
    """Change this function if you move away from Supabase later."""
    if not SUPABASE_URL and not SUPABASE_KEY:
        return None

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Both SUPABASE_URL and SUPABASE_KEY must be set")

    if not create_client:
        raise RuntimeError("Install the supabase package to use Supabase storage")

    return create_client(SUPABASE_URL, SUPABASE_KEY)


def init_db() -> None:
    global supabase_client
    supabase_client = create_supabase_client()


def close_db() -> None:
    global supabase_client
    supabase_client = None


def get_supabase_client() -> Optional[Client]:
    return supabase_client


def get_supabase_table() -> str:
    return SUPABASE_TABLE
