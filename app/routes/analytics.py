from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.services.analytics_service import AnalyticsService
from app.database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/latency")
def get_latency_dashboard(
    provider: str = Query(None),
    model: str = Query(None),
    hours: int = Query(24),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_latency_stats(db, provider, model, hours)

@router.get("/throughput")
def get_throughput_dashboard(
    provider: str = Query(None),
    hours: int = Query(24),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_throughput_stats(db, provider, hours)

@router.get("/errors")
def get_error_dashboard(
    hours: int = Query(24),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_error_stats(db, hours)