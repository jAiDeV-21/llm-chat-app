from typing import Optional

try:
    from supabase import Client, create_client
except ModuleNotFoundError:
    Client = None
    create_client = None

from core.config import settings


supabase_client: Optional[Client] = None


def create_supabase_client() -> Optional[Client]:
    """Change this function if you move away from Supabase later."""
    if not settings.supabase_url and not settings.supabase_key:
        return None

    if not settings.supabase_url or not settings.supabase_key:
        raise ValueError("Both SUPABASE_URL and SUPABASE_KEY must be set")

    if not create_client:
        raise RuntimeError("Install the supabase package to use Supabase storage")

    return create_client(settings.supabase_url, settings.supabase_key)


def init_db() -> None:
    global supabase_client
    supabase_client = create_supabase_client()


def close_db() -> None:
    global supabase_client
    supabase_client = None


def get_supabase_client() -> Optional[Client]:
    return supabase_client


def get_supabase_table() -> str:
    return settings.supabase_table
