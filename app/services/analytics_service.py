from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app.models import InferenceLog

class AnalyticsService:
    """Generate metrics for dashboards"""
    
    @staticmethod
    def get_latency_stats(
        db: Session,
        provider: str = None,
        model: str = None,
        hours: int = 24
    ) -> dict:
        """Get latency metrics"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(InferenceLog).filter(
            InferenceLog.timestamp >= cutoff,
            InferenceLog.status == "success"
        )
        
        if provider:
            query = query.filter(InferenceLog.provider == provider)
        if model:
            query = query.filter(InferenceLog.model == model)
        
        logs = query.all()
        latencies = [log.latency_ms for log in logs]
        
        return {
            "p50": sorted(latencies)[len(latencies)//2] if latencies else 0,
            "p95": sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0,
            "p99": sorted(latencies)[int(len(latencies)*0.99)] if latencies else 0,
            "mean": sum(latencies) / len(latencies) if latencies else 0,
            "max": max(latencies) if latencies else 0,
        }
    
    @staticmethod
    def get_throughput_stats(
        db: Session,
        provider: str = None,
        hours: int = 24
    ) -> dict:
        """Get throughput (tokens/sec)"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(
            InferenceLog.provider,
            func.sum(InferenceLog.output_tokens).label("total_tokens"),
            func.count(InferenceLog.id).label("count"),
            func.sum(InferenceLog.latency_ms).label("total_latency")
        ).filter(InferenceLog.timestamp >= cutoff)
        
        if provider:
            query = query.filter(InferenceLog.provider == provider)
        
        results = query.group_by(InferenceLog.provider).all()
        
        return {
            result.provider: {
                "tokens_per_second": result.total_tokens / (result.total_latency / 1000) if result.total_latency > 0 else 0,
                "requests": result.count
            }
            for result in results
        }
    
    @staticmethod
    def get_error_stats(
        db: Session,
        hours: int = 24
    ) -> dict:
        """Get error metrics"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        total = db.query(func.count(InferenceLog.id)).filter(
            InferenceLog.timestamp >= cutoff
        ).scalar()
        
        errors = db.query(
            InferenceLog.status,
            func.count(InferenceLog.id).label("count")
        ).filter(
            InferenceLog.timestamp >= cutoff,
            InferenceLog.status != "success"
        ).group_by(InferenceLog.status).all()
        
        return {
            "total_requests": total,
            "error_breakdown": {
                error.status: error.count for error in errors
            },
            "error_rate": sum(e.count for e in errors) / total if total > 0 else 0
        }