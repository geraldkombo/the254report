from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from jinja2 import Environment, select_autoescape
from sqlalchemy import select
from sqlalchemy.orm import Session
from weasyprint import CSS, HTML

from app.db.models import Alert, County, CountyIndicator, CountyScore


_env = Environment(autoescape=select_autoescape(["html", "xml"]))


def _fmt(v):
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.1f}"
    return str(v)


def render_emergency_report_pdf(db: Session, alert_id: UUID, year: int, period: str, out_dir: str) -> str:
    alert = db.scalars(select(Alert).where(Alert.id == alert_id)).first()
    if alert is None:
        raise RuntimeError("Alert not found")

    county = db.scalars(select(County).where(County.code == alert.county_code)).first()
    score = db.scalars(
        select(CountyScore).where(CountyScore.county_code == alert.county_code, CountyScore.year == year, CountyScore.period == period)
    ).first()
    ind = db.scalars(
        select(CountyIndicator)
        .where(CountyIndicator.county_code == alert.county_code, CountyIndicator.year == year, CountyIndicator.period == period)
        .order_by(CountyIndicator.computed_at.desc())
        .limit(1)
    ).first()

    now = datetime.now(UTC)
    html = _env.from_string(
        """
        <!doctype html>
        <html>
          <head>
            <meta charset="utf-8" />
            <title>MAJI Sentinel Emergency Brief</title>
          </head>
          <body>
            <div class="header">
              <div class="brand">MAJI Sentinel</div>
              <div class="tag">Emergency County Brief</div>
            </div>
            <h1>{{ county_name }}</h1>
            <div class="meta">
              <div>Alert ID: {{ alert_id }}</div>
              <div>Generated: {{ generated_at }}</div>
              <div>Period: {{ period }} {{ year }}</div>
            </div>

            <div class="cards">
              <div class="card">
                <div class="label">Composite Score</div>
                <div class="value danger">{{ composite }}</div>
                <div class="hint">0–100, lower is worse</div>
              </div>
              <div class="card">
                <div class="label">Key Trigger</div>
                <div class="value">{{ rule }}</div>
                <div class="hint">{{ message }}</div>
              </div>
            </div>

            <h2>Sub-scores</h2>
            <table class="tbl">
              <tr><th>Water Access</th><th>Sanitation</th><th>Water Quality</th><th>Utility</th><th>Governance</th><th>Resilience</th></tr>
              <tr>
                <td>{{ water_access }}</td>
                <td>{{ sanitation }}</td>
                <td>{{ water_quality }}</td>
                <td>{{ utility }}</td>
                <td>{{ governance }}</td>
                <td>{{ resilience }}</td>
              </tr>
            </table>

            <h2>Key Indicators</h2>
            <table class="tbl">
              <tr><th>Open Defecation (%)</th><th>NRW (%)</th><th>Hours Supply</th><th>Water Quality Compliance (%)</th><th>Water Supply (lpcd)</th></tr>
              <tr>
                <td>{{ od }}</td>
                <td>{{ nrv }}</td>
                <td>{{ hours }}</td>
                <td>{{ wq }}</td>
                <td>{{ lpcd }}</td>
              </tr>
            </table>

            <h2>Actions (Suggested)</h2>
            <ol>
              <li>Verify indicator coverage and last-updated timestamps; validate with county WASH teams and local labs.</li>
              <li>Prioritize immediate risk reduction: safe water distribution, chlorination, and targeted sanitation responses in hotspots.</li>
              <li>Coordinate with regulator and service provider(s) to stabilize supply (hours/lpcd) and reduce NRW where feasible.</li>
              <li>Update response evidence and resolve the alert once conditions normalize.</li>
            </ol>
          </body>
        </html>
        """
    ).render(
        county_name=county.name if county else alert.county_code,
        alert_id=str(alert_id),
        generated_at=now.strftime("%Y-%m-%d %H:%M UTC"),
        period=period,
        year=year,
        composite=_fmt(score.composite if score else None),
        rule=alert.rule,
        message=alert.message,
        water_access=_fmt(score.water_access if score else None),
        sanitation=_fmt(score.sanitation if score else None),
        water_quality=_fmt(score.water_quality if score else None),
        utility=_fmt(score.utility_performance if score else None),
        governance=_fmt(score.governance if score else None),
        resilience=_fmt(score.climate_resilience if score else None),
        od=_fmt(ind.open_defecation_pct if ind else None),
        nrv=_fmt(ind.nrv_pct if ind else None),
        hours=_fmt(ind.hours_supply_per_day if ind else None),
        wq=_fmt(ind.water_quality_compliance_pct if ind else None),
        lpcd=_fmt(ind.litres_per_capita_per_day if ind else None),
    )

    css = CSS(
        string="""
        @page { size: A4; margin: 18mm; }
        body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; color: #0B1220; }
        .header { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 2px solid #0B1220; padding-bottom: 8px; margin-bottom: 16px; }
        .brand { font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
        .tag { font-weight: 700; color: #E23B2E; }
        h1 { margin: 6px 0 4px; font-size: 28px; }
        h2 { margin-top: 18px; font-size: 16px; }
        .meta { font-size: 11px; color: #2C3444; display: flex; gap: 14px; flex-wrap: wrap; }
        .cards { display: flex; gap: 10px; margin-top: 14px; }
        .card { border: 1px solid #D8D0C6; border-radius: 12px; padding: 12px; flex: 1; background: #F7F1E6; }
        .label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: #2C3444; }
        .value { font-size: 22px; font-weight: 800; margin-top: 4px; }
        .value.danger { color: #E23B2E; }
        .hint { font-size: 11px; color: #2C3444; margin-top: 4px; }
        .tbl { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 11px; }
        .tbl th { text-align: left; background: #0B1220; color: #F7F1E6; padding: 8px; }
        .tbl td { border: 1px solid #D8D0C6; padding: 8px; }
        ol { font-size: 11px; color: #2C3444; }
        """
    )

    out = Path(out_dir) / "reports" / f"{alert_id}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(target=str(out), stylesheets=[css])
    return str(out)

