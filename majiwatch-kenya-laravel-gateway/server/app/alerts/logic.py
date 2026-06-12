from datetime import UTC, datetime

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Alert, CountyIndicator, CountyScore
from app.reporting.emergency_report import render_emergency_report_pdf


def _active_alert_exists(db: Session, county_code: str, rule: str) -> bool:
    row = db.execute(
        select(Alert.id).where(and_(Alert.county_code == county_code, Alert.rule == rule, Alert.resolved_at.is_(None))).limit(1)
    ).first()
    return row is not None


def evaluate_alerts(db: Session, year: int, period: str) -> None:
    scores = db.scalars(select(CountyScore).where(CountyScore.year == year, CountyScore.period == period)).all()
    now = datetime.now(UTC)

    for s in scores:
        ind = db.scalars(
            select(CountyIndicator)
            .where(CountyIndicator.county_code == s.county_code, CountyIndicator.year == year, CountyIndicator.period == period)
            .order_by(CountyIndicator.computed_at.desc())
            .limit(1)
        ).first()

        od = float(ind.open_defecation_pct) if ind and ind.open_defecation_pct is not None else 0.0
        nrv = float(ind.nrv_pct) if ind and ind.nrv_pct is not None else 0.0
        lpcd = float(ind.litres_per_capita_per_day) if ind and ind.litres_per_capita_per_day is not None else 999.0
        cholera = bool(ind.cholera_outbreak_flag) if ind and ind.cholera_outbreak_flag is not None else False

        severity = None
        rule = None
        message = None

        if s.composite < 30 or cholera:
            severity = "emergency"
            rule = "emergency_composite_or_cholera"
            message = "Emergency trigger: composite < 30 or cholera/water-quality outbreak signal."
        elif s.composite < 45 or od > 30 or nrv > 50 or lpcd < 20:
            severity = "warning"
            rule = "warning_thresholds"
            message = "Warning trigger: composite < 45 OR open defecation > 30% OR non-revenue water > 50% OR water supply < 20 lpcd."
        elif s.composite < 60:
            severity = "watch"
            rule = "watch_composite"
            message = "Watch trigger: composite < 60."

        if severity is None or rule is None or message is None:
            continue

        if _active_alert_exists(db, s.county_code, rule):
            continue

        alert = Alert(
            county_code=s.county_code,
            severity=severity,
            rule=rule,
            message=message,
            triggered_at=now,
            resolved_at=None,
            pdf_report_path=None,
        )
        db.add(alert)
        db.flush()

        if severity == "emergency":
            pdf_path = render_emergency_report_pdf(db=db, alert_id=alert.id, year=year, period=period, out_dir=settings.data_dir)
            alert.pdf_report_path = pdf_path

        db.commit()

