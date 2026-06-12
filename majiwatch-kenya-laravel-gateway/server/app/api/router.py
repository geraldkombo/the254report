import csv
import hashlib
import hmac
import io
import json
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import case, func, select, text
from sqlalchemy.orm import Session

from app.api.schemas import (
    AlertOut,
    ComputeRequest,
    ComputeResponse,
    CountyScoreOut,
    HealthOut,
    ResolveAlertOut,
    WaterpointLookupIn,
    WaterpointLookupOut,
)
from app.core.config import settings
from app.core.security import require_api_key
from app.db.models import Alert, County, CountyIndicator, CountyScore, Datasource, Waterpoint
from app.db.session import get_db
from app.tasks.jobs import run_compute_manual


router = APIRouter()


def _etag_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _set_cache_headers(response: Response, payload: bytes, max_age_s: int) -> None:
    response.headers["Cache-Control"] = f"public, max-age={max_age_s}"
    response.headers["ETag"] = _etag_bytes(payload)


def _scores_latest(db: Session) -> list[CountyScore]:
    rn = func.row_number().over(partition_by=CountyScore.county_code, order_by=CountyScore.computed_at.desc()).label("rn")
    subq = select(CountyScore.id.label("id"), rn).subquery()
    return db.scalars(select(CountyScore).join(subq, CountyScore.id == subq.c.id).where(subq.c.rn == 1)).all()


def _alerts_active(db: Session) -> list[Alert]:
    return db.scalars(
        select(Alert)
        .where(Alert.resolved_at.is_(None))
        .order_by(
            case(
                (Alert.severity == "emergency", 0),
                (Alert.severity == "warning", 1),
                (Alert.severity == "watch", 2),
                else_=3,
            ),
            Alert.triggered_at.desc(),
        )
    ).all()


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(ok=True, name=settings.app_name, env=settings.app_env)


@router.get("/counties")
def counties(response: Response, simplify: float | None = None, db: Session = Depends(get_db)) -> dict[str, Any]:
    geom_expr = County.geom
    if simplify is not None and simplify > 0:
        geom_expr = func.ST_SimplifyPreserveTopology(County.geom, simplify)

    rows = db.execute(select(County.code, County.name, func.ST_AsGeoJSON(geom_expr))).all()
    features: list[dict[str, Any]] = []
    for code, name, geom_json in rows:
        features.append(
            {
                "type": "Feature",
                "geometry": None if geom_json is None else json.loads(geom_json),
                "properties": {"code": code, "name": name},
            }
        )
    out = {"type": "FeatureCollection", "features": features}
    payload = json.dumps(out, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    _set_cache_headers(response, payload, max_age_s=3600)
    return out


@router.get("/datasources")
def datasources(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.scalars(select(Datasource).order_by(Datasource.name)).all()
    return [{"id": r.id, "name": r.name, "license": r.license, "homepage": r.homepage} for r in rows]


@router.get("/scores/latest", response_model=list[CountyScoreOut])
def scores_latest(response: Response, db: Session = Depends(get_db)) -> list[CountyScoreOut]:
    rows = _scores_latest(db)
    items = [CountyScoreOut.model_validate(r) for r in rows]
    payload = json.dumps([i.model_dump(mode="json") for i in items], separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    _set_cache_headers(response, payload, max_age_s=120)
    return items


@router.get("/scores/{county_code}", response_model=CountyScoreOut)
def latest_score(county_code: str, db: Session = Depends(get_db)) -> CountyScoreOut:
    s = db.scalars(select(CountyScore).where(CountyScore.county_code == county_code).order_by(CountyScore.computed_at.desc()).limit(1)).first()
    if s is None:
        raise HTTPException(status_code=404, detail="Score not found")
    return CountyScoreOut.model_validate(s)


@router.get("/scores", response_model=list[CountyScoreOut])
def scores(response: Response, year: int | None = None, db: Session = Depends(get_db)) -> list[CountyScoreOut]:
    if year is None:
        return scores_latest(response=response, db=db)
    q = select(CountyScore).where(CountyScore.year == year).order_by(CountyScore.county_code, CountyScore.period.asc())
    rows = db.scalars(q).all()
    return [CountyScoreOut.model_validate(r) for r in rows]


@router.get("/alerts", response_model=list[AlertOut])
def alerts(db: Session = Depends(get_db)) -> list[AlertOut]:
    rows = _alerts_active(db)
    out: list[AlertOut] = []
    for a in rows:
        url = None
        if a.pdf_report_path:
            filename = a.pdf_report_path.split("/")[-1]
            url = f"{settings.public_base_url}/reports/{filename}"
        out.append(
            AlertOut(
                id=a.id,
                county_code=a.county_code,
                severity=a.severity,
                rule=a.rule,
                message=a.message,
                triggered_at=a.triggered_at,
                resolved_at=a.resolved_at,
                pdf_report_url=url,
            )
        )
    return out


@router.get("/alerts/active", response_model=list[AlertOut])
def alerts_active(response: Response, db: Session = Depends(get_db)) -> list[AlertOut]:
    items = alerts(db=db)
    payload = json.dumps([i.model_dump(mode="json") for i in items], separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    _set_cache_headers(response, payload, max_age_s=60)
    return items


@router.patch("/alerts/{alert_id}/resolve", response_model=ResolveAlertOut, dependencies=[Depends(require_api_key)])
def resolve_alert(alert_id: str, db: Session = Depends(get_db)) -> ResolveAlertOut:
    a = db.scalars(select(Alert).where(Alert.id == alert_id)).first()
    if a is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    if a.resolved_at is not None:
        return ResolveAlertOut(id=a.id, resolved_at=a.resolved_at)
    a.resolved_at = datetime.now(UTC)
    db.commit()
    return ResolveAlertOut(id=a.id, resolved_at=a.resolved_at)


@router.get("/export/scores")
def export_scores(year: int, db: Session = Depends(get_db)) -> Response:
    rows = db.scalars(select(CountyScore).where(CountyScore.year == year).order_by(CountyScore.county_code, CountyScore.computed_at.desc())).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        [
            "county_code",
            "year",
            "period",
            "water_access",
            "sanitation",
            "water_quality",
            "utility_performance",
            "governance",
            "climate_resilience",
            "composite",
            "confidence",
            "computed_at",
        ]
    )
    for r in rows:
        w.writerow(
            [
                r.county_code,
                r.year,
                r.period,
                f"{r.water_access:.2f}",
                f"{r.sanitation:.2f}",
                f"{r.water_quality:.2f}",
                f"{r.utility_performance:.2f}",
                f"{r.governance:.2f}",
                f"{r.climate_resilience:.2f}",
                f"{r.composite:.2f}",
                f"{r.confidence:.2f}",
                r.computed_at.isoformat(),
            ]
        )
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="maji_scores_{year}.csv"'},
    )


@router.get("/export/waterpoints")
def export_waterpoints(county: str | None = None, db: Session = Depends(get_db)) -> Response:
    q = select(
        Waterpoint.id,
        Waterpoint.county_code,
        Waterpoint.source,
        Waterpoint.type,
        Waterpoint.functionality,
        func.ST_Y(Waterpoint.geom).label("lat"),
        func.ST_X(Waterpoint.geom).label("lng"),
    )
    if county is not None:
        q = q.where(Waterpoint.county_code == county)
    rows = db.execute(q).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "county_code", "source", "type", "functionality", "lat", "lng"])
    for r in rows:
        w.writerow([str(r.id), r.county_code, r.source, r.type, r.functionality, r.lat, r.lng])
    suffix = county or "all"
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="maji_waterpoints_{suffix}.csv"'},
    )


@router.get("/waterpoints")
def waterpoints(
    county: str | None = None,
    bbox: str | None = None,
    wptype: str | None = None,
    functionality: str | None = None,
    limit: int = 2000,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    q = select(
        Waterpoint.id,
        Waterpoint.county_code,
        Waterpoint.source,
        Waterpoint.type,
        Waterpoint.functionality,
        func.ST_AsGeoJSON(Waterpoint.geom).label("geom_json"),
    )
    if county is not None:
        q = q.where(Waterpoint.county_code == county)
    if wptype is not None:
        q = q.where(Waterpoint.type == wptype)
    if functionality is not None:
        q = q.where(Waterpoint.functionality == functionality)
    if bbox is not None:
        parts = bbox.split(",")
        if len(parts) != 4:
            raise HTTPException(status_code=400, detail="Invalid bbox format")
        min_lng, min_lat, max_lng, max_lat = (float(p) for p in parts)
        env = func.ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)
        q = q.where(func.ST_Intersects(Waterpoint.geom, env))
    q = q.limit(min(limit, 20000))
    rows = db.execute(q).all()

    features: list[dict[str, Any]] = []
    for r in rows:
        features.append(
            {
                "type": "Feature",
                "geometry": None if r.geom_json is None else json.loads(r.geom_json),
                "properties": {
                    "id": str(r.id),
                    "county_code": r.county_code,
                    "source": r.source,
                    "type": r.type,
                    "functionality": r.functionality,
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}


@router.get("/tiles/waterpoints/{z}/{x}/{y}.pbf")
def waterpoints_tile(z: int, x: int, y: int, response: Response, county: str | None = None, db: Session = Depends(get_db)) -> Response:
    q = text(
        """
        WITH bounds AS (
          SELECT ST_TileEnvelope(:z, :x, :y) AS geom
        ),
        mvtgeom AS (
          SELECT
            (w.id::text) AS id,
            w.county_code,
            w.source,
            w.type,
            w.functionality,
            ST_AsMVTGeom(ST_Transform(w.geom, 3857), bounds.geom, 4096, 64, true) AS geom
          FROM waterpoints w, bounds
          WHERE ST_Intersects(ST_Transform(w.geom, 3857), bounds.geom)
            AND (:county IS NULL OR w.county_code = :county)
        )
        SELECT ST_AsMVT(mvtgeom, 'waterpoints', 4096, 'geom') FROM mvtgeom;
        """
    )
    data = db.execute(q, {"z": z, "x": x, "y": y, "county": county}).scalar()
    tile = bytes(data) if data is not None else b""
    _set_cache_headers(response, tile, max_age_s=3600)
    return Response(content=tile, media_type="application/x-protobuf", headers=dict(response.headers))


@router.post("/compute/scores", response_model=ComputeResponse, dependencies=[Depends(require_api_key)])
def compute_scores(req: ComputeRequest, db: Session = Depends(get_db)) -> ComputeResponse:
    now = datetime.now(UTC)
    year = req.year or now.year
    period = req.period or now.date().isoformat()
    async_result = run_compute_manual.delay(year=year, period=period)
    return ComputeResponse(enqueued=True, year=year, period=period, task_id=async_result.id)


@router.post("/lookup/waterpoint", response_model=WaterpointLookupOut)
def lookup_nearest_waterpoint(body: WaterpointLookupIn, db: Session = Depends(get_db)) -> WaterpointLookupOut:
    point = func.ST_SetSRID(func.ST_MakePoint(body.lng, body.lat), 4326)
    q = (
        select(
            Waterpoint.id,
            Waterpoint.county_code,
            Waterpoint.source,
            Waterpoint.type,
            Waterpoint.functionality,
            func.ST_Y(Waterpoint.geom).label("lat"),
            func.ST_X(Waterpoint.geom).label("lng"),
            func.ST_DistanceSphere(Waterpoint.geom, point).label("dist_m"),
        )
        .order_by(func.ST_DistanceSphere(Waterpoint.geom, point))
        .limit(1)
    )
    r = db.execute(q).first()
    if r is None:
        raise HTTPException(status_code=404, detail="No water points available")
    return WaterpointLookupOut(
        id=r.id,
        county_code=r.county_code,
        source=r.source,
        type=r.type,
        functionality=r.functionality,
        lat=float(r.lat),
        lng=float(r.lng),
        distance_m=float(r.dist_m),
    )


@router.get("/oracle/water-quality/latest")
def oracle_water_quality_latest(db: Session = Depends(get_db)) -> dict[str, Any]:
    if not settings.oracle_signing_secret:
        raise HTTPException(status_code=501, detail="Oracle not configured")

    subq = (
        select(
            CountyIndicator.county_code,
            func.max(CountyIndicator.computed_at).label("max_ts"),
        )
        .group_by(CountyIndicator.county_code)
        .subquery()
    )
    rows = db.execute(
        select(
            CountyIndicator.county_code,
            CountyIndicator.year,
            CountyIndicator.period,
            CountyIndicator.water_quality_compliance_pct,
            CountyIndicator.computed_at,
        ).join(
            subq,
            (CountyIndicator.county_code == subq.c.county_code) & (CountyIndicator.computed_at == subq.c.max_ts),
        )
    ).all()

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source_ids": ["wra", "hiskenya", "baseline_synthetic"],
        "counties": [
            {
                "county_code": r.county_code,
                "year": r.year,
                "period": r.period,
                "water_quality_compliance_pct": float(r.water_quality_compliance_pct) if r.water_quality_compliance_pct is not None else None,
                "computed_at": r.computed_at.isoformat() if r.computed_at else None,
            }
            for r in rows
        ],
    }

    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    signature = hmac.new(settings.oracle_signing_secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()
    return {"payload": payload, "sha256": _etag_bytes(raw), "signature": signature}
