import math
import uuid
from datetime import UTC, datetime

from geoalchemy2.elements import WKTElement
from shapely import wkb
from shapely.geometry import Point
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import County, CountyIndicator, Waterpoint


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def _hash01(text: str) -> float:
    h = 2166136261
    for ch in text.encode("utf-8"):
        h ^= ch
        h *= 16777619
        h &= 0xFFFFFFFF
    return (h % 10_000) / 10_000.0


def ensure_synthetic_baseline(db: Session, year: int, period: str) -> None:
    existing = db.execute(
        select(CountyIndicator.id).where(CountyIndicator.year == year, CountyIndicator.period == period).limit(1)
    ).first()
    if existing is not None:
        return

    now = datetime.now(UTC)
    counties = db.scalars(select(County)).all()
    for c in counties:
        r = _hash01(c.code)

        water_access = _clamp(35 + 55 * r + 10 * math.sin(int(c.code) / 7))
        sanitation_improved = _clamp(20 + 60 * r + 5 * math.cos(int(c.code) / 5))
        open_defecation = _clamp(60 - sanitation_improved + 10 * (1 - r), 0, 70)

        quality_compliance = _clamp(40 + 50 * r - 10 * (open_defecation / 70))

        nrv = _clamp(20 + 55 * (1 - r), 10, 80)
        hours_supply = _clamp(6 + 18 * r, 0, 24)
        billing_eff = _clamp(55 + 40 * r, 0, 100)
        lpcd = _clamp(15 + 55 * r, 0, 120)

        governance_policy = 1 if r > 0.35 else 0
        participation = _clamp(30 + 70 * r, 0, 100) / 100.0

        drought_risk = _clamp(25 + 70 * (1 - r), 0, 100) / 100.0
        recharge_potential = _clamp(20 + 70 * r, 0, 100) / 100.0

        cholera_flag = 1 if (open_defecation > 45 and quality_compliance < 55) else 0

        db.add(
            CountyIndicator(
                county_code=c.code,
                year=year,
                period=period,
                water_access_improved_pct=water_access,
                sanitation_improved_pct=sanitation_improved,
                open_defecation_pct=open_defecation,
                water_quality_compliance_pct=quality_compliance,
                nrv_pct=nrv,
                hours_supply_per_day=hours_supply,
                billing_efficiency_pct=billing_eff,
                litres_per_capita_per_day=lpcd,
                governance_policy_present=governance_policy,
                governance_participation_index=participation,
                drought_risk_index=drought_risk,
                recharge_potential_index=recharge_potential,
                cholera_outbreak_flag=cholera_flag,
                computed_at=now,
            )
        )

    db.commit()


def ensure_synthetic_waterpoints(db: Session, target_per_county: int = 60) -> None:
    existing = db.execute(select(Waterpoint.id).limit(1)).first()
    if existing is not None:
        return

    rows = db.execute(
        select(County.code, func.ST_AsBinary(func.ST_Centroid(County.geom)).label("centroid_wkb"))
    ).all()

    types = ["borehole", "well", "piped_scheme", "surface_intake"]
    statuses = ["functioning", "partially_functioning", "broken"]

    for county_code, centroid_wkb in rows:
        centroid = wkb.loads(bytes(centroid_wkb))
        base_lon = float(centroid.x)
        base_lat = float(centroid.y)
        r0 = _hash01(county_code)

        for i in range(target_per_county):
            r = _hash01(f"{county_code}:{i}")
            angle = r * math.tau
            dist = 0.12 * (0.2 + r0) * (0.3 + _hash01(f"d:{county_code}:{i}"))
            lon = base_lon + math.cos(angle) * dist
            lat = base_lat + math.sin(angle) * dist * 0.9

            wp_type = types[int(r * len(types)) % len(types)]
            status = statuses[int((1 - r) * len(statuses)) % len(statuses)]

            db.add(
                Waterpoint(
                    id=uuid.uuid4(),
                    external_id=None,
                    source="baseline_synthetic",
                    county_code=county_code,
                    geom=WKTElement(Point(lon, lat).wkt, srid=4326),
                    type=wp_type,
                    functionality=status,
                    last_maintenance_date=None,
                )
            )

    db.commit()

