from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import router
from db.supabase_client import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        yield
    finally:
        close_db()


app = FastAPI(title="Inference Logging Ingestion Service", lifespan=lifespan)
app.include_router(router)
