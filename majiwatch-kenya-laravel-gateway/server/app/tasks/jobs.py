from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.alerts.logic import evaluate_alerts
from app.db.session import SessionLocal
from app.etl.ingest_all import ingest_all_sources
from app.etl.ingest import ensure_synthetic_baseline, ensure_synthetic_waterpoints
from app.scoring.compute import compute_scores
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.jobs.run_nightly")
def run_nightly() -> dict:
    now = datetime.now(UTC)
    year = now.year
    period = now.date().isoformat()

    db: Session = SessionLocal()
    try:
        ingest_all_sources(db)
        ensure_synthetic_baseline(db, year=year, period=period)
        ensure_synthetic_waterpoints(db)
        compute_scores(db, year=year, period=period)
        evaluate_alerts(db, year=year, period=period)
        return {"ok": True, "year": year, "period": period}
    finally:
        db.close()


@celery_app.task(name="app.tasks.jobs.run_compute_manual")
def run_compute_manual(year: int, period: str) -> dict:
    db: Session = SessionLocal()
    try:
        ingest_all_sources(db)
        ensure_synthetic_baseline(db, year=year, period=period)
        ensure_synthetic_waterpoints(db)
        compute_scores(db, year=year, period=period)
        evaluate_alerts(db, year=year, period=period)
        return {"ok": True, "year": year, "period": period}
    finally:
        db.close()
