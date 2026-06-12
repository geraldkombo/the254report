import json
import unicodedata
from datetime import UTC, datetime
from pathlib import Path

import httpx
from geoalchemy2.elements import WKTElement
from shapely.geometry import MultiPolygon, Polygon, shape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Base, County, Datasource
from app.db.session import engine
from app.geo.kenya_counties import COUNTY_CODE_BY_NAME


def _norm_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().strip()
    value = value.replace("&", "and")
    value = value.replace("-", " ")
    value = " ".join(value.split())
    return value


def ensure_data_dirs() -> None:
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.data_dir, "downloads").mkdir(parents=True, exist_ok=True)
    Path(settings.data_dir, "reports").mkdir(parents=True, exist_ok=True)


def migrate_if_enabled() -> None:
    if settings.app_auto_migrate:
        Base.metadata.create_all(engine)


def seed_datasources(db: Session) -> None:
    items = [
        Datasource(id="baseline_synthetic", name="Synthetic baseline bundle (bootstrap sample)", license="Internal/demo", homepage=None),
        Datasource(id="geoboundaries_adm1", name="geoBoundaries ADM1 (Kenya counties)", license="CC BY 4.0", homepage="https://www.geoboundaries.org/"),
        Datasource(id="hdx_ken_admin", name="Kenya Administrative Boundaries (HDX)", license="Varies (check dataset)", homepage="https://data.humdata.org/"),

        Datasource(id="wasreb_impact", name="WASREB Impact Reports", license="Public", homepage="https://wasreb.go.ke/"),
        Datasource(id="wasreb_performance", name="WASREB Performance Reports (WSP benchmarking)", license="Public", homepage="https://wasreb.go.ke/"),
        Datasource(id="wasreb_tariffs", name="WASREB Tariff Guidelines & Approvals (where published)", license="Public", homepage="https://wasreb.go.ke/"),
        Datasource(id="majidata", name="Majidata (WASREB monitoring dashboards)", license="Public", homepage="https://majidata.go.ke/"),

        Datasource(id="wra_waterpoints", name="Water Resources Authority (WRA) water points", license="Public", homepage="https://wra.go.ke/"),
        Datasource(id="wra_borehole_permits", name="WRA borehole & well permits", license="Public", homepage="https://wra.go.ke/"),
        Datasource(id="wra_abstraction", name="WRA water abstraction & permits", license="Public", homepage="https://wra.go.ke/"),
        Datasource(id="wra_catchments", name="WRA catchment boundaries (6 major catchments)", license="Public", homepage="https://wra.go.ke/"),
        Datasource(id="wra_water_quality", name="WRA water quality monitoring summaries", license="Public", homepage="https://wra.go.ke/"),

        Datasource(id="wpdx", name="Water Point Data Exchange (WPDx)", license="CC BY 4.0", homepage="https://www.waterpointdata.org/"),
        Datasource(id="osm_hydro", name="OpenStreetMap Hydrography (Kenya)", license="ODbL 1.0", homepage="https://www.openstreetmap.org/"),

        Datasource(id="knbs_census_2019", name="KNBS Census 2019 (water & sanitation)", license="Public (check)", homepage="https://www.knbs.or.ke/"),
        Datasource(id="knbs_housing_2023_24", name="Kenya Housing Survey 2023/24 (sanitation)", license="Public (check)", homepage="https://www.knbs.or.ke/"),
        Datasource(id="kenya_water_master_plan_2030", name="Kenya National Water Master Plan 2030", license="Public", homepage="https://www.knbs.or.ke/"),

        Datasource(id="chirps", name="CHIRPS Rainfall", license="Free for research/use (see source terms)", homepage="https://www.chc.ucsb.edu/data/chirps"),
        Datasource(id="ndma_drought", name="NDMA Drought Bulletins", license="Public", homepage="https://www.ndma.go.ke/"),
        Datasource(id="kmd_forecasts", name="Kenya Meteorological Department seasonal forecasts", license="Public", homepage="https://meteo.go.ke/"),

        Datasource(id="wasreb_impact", name="WASREB Impact Reports", license="Public", homepage="https://wasreb.go.ke/"),
        Datasource(id="moh_wq_surveillance", name="Ministry of Health drinking water surveillance (public aggregates)", license="Public", homepage="https://hiskenya.org/"),

        Datasource(id="hiskenya", name="HisKenya DHIS2 API (public aggregates)", license="Public", homepage="https://hiskenya.org/"),
        Datasource(id="unicef_data_wash", name="UNICEF Data (WASH indicators)", license="Public (check)", homepage="https://data.unicef.org/"),
        Datasource(id="un_sdg6", name="UN SDG 6 Global Database", license="Public (check)", homepage="https://sdg6data.org/"),
        Datasource(id="worldbank_wdi", name="World Bank WDI (WASH indicators)", license="World Bank Open Data", homepage="https://data.worldbank.org/"),

        Datasource(id="jmp", name="WHO/UNICEF JMP", license="CC BY 4.0 (verify download)", homepage="https://washdata.org/"),
        Datasource(id="jrc_surface_water", name="JRC Global Surface Water", license="Open (verify)", homepage="https://global-surface-water.appspot.com/"),
        Datasource(id="copernicus_climate", name="Copernicus Climate Data Store (context)", license="Open (check)", homepage="https://cds.climate.copernicus.eu/"),
        Datasource(id="nasa_modis", name="NASA MODIS (vegetation/land surface proxies)", license="Open", homepage="https://modis.gsfc.nasa.gov/"),
        Datasource(id="servir", name="SERVIR (regional geospatial decision support)", license="Open (check)", homepage="https://servirglobal.net/"),

        Datasource(id="county_cidps", name="County Integrated Development Plans (CIDPs)", license="Public", homepage="https://www.cog.go.ke/"),
        Datasource(id="water_act_2016", name="Water Act 2016 implementation references", license="Public", homepage="https://www.kenyalaw.org/"),
        Datasource(id="kewasnet", name="KEWASNET reports (periodic)", license="Public", homepage="https://kewasnet.or.ke/"),

        Datasource(id="fao_aquastat", name="FAO AQUASTAT (water resources context)", license="Open (check)", homepage="https://www.fao.org/aquastat/"),
        Datasource(id="unep", name="UNEP (water ecosystems context)", license="Open (check)", homepage="https://www.unep.org/"),
        Datasource(id="openalex_wash_research", name="OpenAlex (WASH research signals)", license="Open", homepage="https://openalex.org/"),
        Datasource(id="grace", name="GRACE / GRACE-FO mass anomalies", license="Open (verify)", homepage="https://grace.jpl.nasa.gov/"),

    existing = {row[0] for row in db.execute(select(Datasource.id)).all()}
    for item in items:
        if item.id not in existing:
            db.add(item)
    db.commit()


def seed_counties_from_geoboundaries(db: Session) -> None:
    existing = db.execute(select(County.code).limit(1)).first()
    if existing is not None:
        return

    fallback_path = Path(__file__).resolve().parent / "geo" / "kenya_adm1_simplified.geojson"
    if fallback_path.exists():
        data = fallback_path.read_text(encoding="utf-8")
    else:
        api_url = "https://www.geoboundaries.org/api/current/gbOpen/KEN/ADM1/"
        with httpx.Client(timeout=60) as client:
            meta = client.get(api_url).json()
            meta_item = meta[0] if isinstance(meta, list) else meta
            geojson_url = meta_item.get("gjDownloadURL") or meta_item.get("gjDownloadUrl")
            if not geojson_url:
                raise RuntimeError("geoBoundaries response missing GeoJSON download URL")

            data = client.get(geojson_url).text

    obj = json.loads(data)
    features = obj.get("features", [])
    if not features:
        raise RuntimeError("No features found in counties GeoJSON")

    now = datetime.now(UTC)
    inserted = 0
    for f in features:
        props = f.get("properties") or {}
        name = props.get("shapeName") or props.get("NAME_1") or props.get("name") or props.get("ADM1_NAME") or ""
        name_norm = _norm_name(str(name))
        code = COUNTY_CODE_BY_NAME.get(name_norm)
        if not code:
            continue

        geom = shape(f.get("geometry"))
        if isinstance(geom, Polygon):
            geom = MultiPolygon([geom])
        if not isinstance(geom, MultiPolygon):
            continue

        db.add(
            County(
                code=code,
                name=str(name),
                geom=WKTElement(geom.wkt, srid=4326),
                population=None,
            )
        )
        inserted += 1

    if inserted < 47:
        missing = 47 - inserted
        raise RuntimeError(f"County seeding incomplete ({inserted}/47). Missing {missing}.")

    db.commit()
    _ = now


def bootstrap(db: Session) -> None:
    ensure_data_dirs()
    migrate_if_enabled()
    seed_datasources(db)
    seed_counties_from_geoboundaries(db)
