import hashlib
from datetime import UTC, datetime
from pathlib import Path

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Datasource, IngestArtifact, IngestRun


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ingest_all_sources(db: Session) -> dict:
    started = datetime.now(UTC)
    downloads_dir = Path(settings.data_dir) / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)

    sources = db.scalars(select(Datasource).order_by(Datasource.id)).all()
    ok = 0
    failed = 0

    with httpx.Client(timeout=60, follow_redirects=True) as client:
        for s in sources:
            run = IngestRun(
                datasource_id=s.id,
                started_at=datetime.now(UTC),
                finished_at=None,
                status="running",
                notes=None,
            )
            db.add(run)
            db.flush()

            try:
                if not s.homepage:
                    run.status = "skipped"
                    run.notes = "No homepage configured"
                    run.finished_at = datetime.now(UTC)
                    db.commit()
                    continue

                res = client.get(s.homepage)
                content = res.content
                ext = "json" if "application/json" in (res.headers.get("content-type") or "") else "html"
                out_dir = downloads_dir / s.id / started.date().isoformat()
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / f"homepage.{ext}"
                out_path.write_bytes(content)

                db.add(
                    IngestArtifact(
                        ingest_run_id=run.id,
                        artifact_type="homepage",
                        path=str(out_path),
                        checksum=_sha256_bytes(content),
                    )
                )
                run.status = "ok"
                run.finished_at = datetime.now(UTC)
                ok += 1
                db.commit()
            except Exception as e:
                run.status = "failed"
                run.notes = str(e)
                run.finished_at = datetime.now(UTC)
                failed += 1
                db.commit()

    return {"ok": ok, "failed": failed}

