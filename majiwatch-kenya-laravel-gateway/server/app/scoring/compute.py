from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import County, CountyIndicator, CountyScore


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def _score_nrv(nrv_pct: float | None) -> float:
    if nrv_pct is None:
        return 50.0
    return _clamp(100 - max(0.0, nrv_pct - 25.0) * 2.0)


def _score_hours(hours: float | None) -> float:
    if hours is None:
        return 50.0
    return _clamp((hours / 24.0) * 100.0)


def compute_scores(db: Session, year: int, period: str) -> None:
    db.execute(delete(CountyScore).where(CountyScore.year == year, CountyScore.period == period))
    db.commit()

    now = datetime.now(UTC)
    counties = db.scalars(select(County)).all()
    for c in counties:
        ind = db.scalars(
            select(CountyIndicator)
            .where(CountyIndicator.county_code == c.code, CountyIndicator.year == year, CountyIndicator.period == period)
            .order_by(CountyIndicator.computed_at.desc())
            .limit(1)
        ).first()

        water_access = _clamp(ind.water_access_improved_pct if ind and ind.water_access_improved_pct is not None else 50.0)

        sanitation_improved = ind.sanitation_improved_pct if ind else None
        open_def = ind.open_defecation_pct if ind else None
        sanitation = _clamp((sanitation_improved or 50.0) - 1.6 * (open_def or 0.0))

        water_quality = _clamp(ind.water_quality_compliance_pct if ind and ind.water_quality_compliance_pct is not None else 50.0)

        utility_perf = _clamp(
            0.45 * _score_nrv(ind.nrv_pct if ind else None)
            + 0.30 * _score_hours(ind.hours_supply_per_day if ind else None)
            + 0.25 * _clamp(ind.billing_efficiency_pct if ind and ind.billing_efficiency_pct is not None else 50.0)
        )

        governance = _clamp(
            (70.0 if (ind and ind.governance_policy_present) else 40.0)
            + 30.0 * _clamp((ind.governance_participation_index or 0.5) * 100.0) / 100.0
        )

        drought = ind.drought_risk_index if ind else None
        recharge = ind.recharge_potential_index if ind else None
        climate_resilience = _clamp(100.0 * (0.6 * (1.0 - (drought or 0.5)) + 0.4 * (recharge or 0.5)))

        composite = _clamp(
            0.25 * water_access
            + 0.25 * sanitation
            + 0.15 * water_quality
            + 0.15 * utility_perf
            + 0.10 * governance
            + 0.10 * climate_resilience
        )

        coverage_fields = [
            ind.water_access_improved_pct if ind else None,
            ind.sanitation_improved_pct if ind else None,
            ind.open_defecation_pct if ind else None,
            ind.water_quality_compliance_pct if ind else None,
            ind.nrv_pct if ind else None,
            ind.hours_supply_per_day if ind else None,
            ind.billing_efficiency_pct if ind else None,
            ind.drought_risk_index if ind else None,
            ind.recharge_potential_index if ind else None,
        ]
        coverage = sum(1 for v in coverage_fields if v is not None) / len(coverage_fields)
        confidence = _clamp(25 + 75 * coverage)

        db.add(
            CountyScore(
                county_code=c.code,
                year=year,
                period=period,
                water_access=water_access,
                sanitation=sanitation,
                water_quality=water_quality,
                utility_performance=utility_perf,
                governance=governance,
                climate_resilience=climate_resilience,
                composite=composite,
                confidence=confidence,
                computed_at=now,
            )
        )

    db.commit()

