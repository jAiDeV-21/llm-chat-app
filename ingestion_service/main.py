from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from models import InferenceLogModel, IngestPayload, get_db, init_db
from services.extraction import extract_metadata
from services.pii_redaction import redact_pii
from services.validation import validate_ingest_payload


app = FastAPI(title="Inference Logging Ingestion Service")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.post("/api/ingest/logs")
async def ingest_logs(payload: IngestPayload, db: Session = Depends(get_db)):
    """
    Receives inference logs from SDK.
    Validates, processes, and stores.
    """
    
    try:
        validate_ingest_payload(payload)
        
        # Process each log
        stored_logs = []
        for log_data in payload.logs:
            # 1. Parse and validate
            log_dict = log_data.dict()
            
            # 2. Extract metadata
            extracted_metadata = extract_metadata(log_dict)
            
            # 3. Redact PII (if enabled)
            redacted_log = redact_pii(log_dict)
            
            # 4. Store in database
            db_log = InferenceLogModel(
                **redacted_log,
                extracted_metadata=extracted_metadata
            )
            db.add(db_log)
            stored_logs.append(db_log)
        
        # 5. Batch insert
        db.commit()
        
        # 6. Publish events (optional)
        for log in stored_logs:
            publish_event("inference.logged", log)
        
        return {
            "status": "success",
            "logs_ingested": len(stored_logs)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def publish_event(event_name: str, log: InferenceLogModel) -> None:
    """Placeholder hook for event bus integration."""
    return None




