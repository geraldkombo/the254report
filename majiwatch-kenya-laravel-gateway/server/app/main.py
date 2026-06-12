import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import router as api_router
from app.bootstrap import bootstrap
from app.core.config import settings
from app.db.session import SessionLocal


app = FastAPI(title="MajiWatch Kenya API", version="0.2.0")

allow_origins = [o.strip() for o in (settings.cors_allow_origins or "").split(",") if o.strip()]
if not allow_origins:
    allow_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
if "*" in allow_origins:
    allow_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)

app.include_router(api_router)

app.mount("/reports", StaticFiles(directory=f"{settings.data_dir}/reports"), name="reports")


@app.on_event("startup")
def _startup() -> None:
    last_err: Exception | None = None
    for _ in range(60):
        db = SessionLocal()
        try:
            bootstrap(db)
            return
        except Exception as e:
            last_err = e
            time.sleep(1.0)
        finally:
            db.close()
    if last_err:
        raise last_err
