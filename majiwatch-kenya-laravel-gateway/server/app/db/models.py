import uuid
from datetime import date, datetime

from geoalchemy2 import Geometry
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class County(Base):
    __tablename__ = "counties"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    geom: Mapped[str] = mapped_column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)

    scores: Mapped[list["CountyScore"]] = relationship(back_populates="county")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="county")


class Waterpoint(Base):
    __tablename__ = "waterpoints"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    county_code: Mapped[str | None] = mapped_column(ForeignKey("counties.code"), nullable=True)
    geom: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    functionality: Mapped[str | None] = mapped_column(String, nullable=True)
    last_maintenance_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class CountyScore(Base):
    __tablename__ = "county_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    county_code: Mapped[str] = mapped_column(ForeignKey("counties.code"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    period: Mapped[str] = mapped_column(String, nullable=False)

    water_access: Mapped[float] = mapped_column(Float, nullable=False)
    sanitation: Mapped[float] = mapped_column(Float, nullable=False)
    water_quality: Mapped[float] = mapped_column(Float, nullable=False)
    utility_performance: Mapped[float] = mapped_column(Float, nullable=False)
    governance: Mapped[float] = mapped_column(Float, nullable=False)
    climate_resilience: Mapped[float] = mapped_column(Float, nullable=False)
    composite: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    county: Mapped["County"] = relationship(back_populates="scores")


class CountyIndicator(Base):
    __tablename__ = "county_indicators"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    county_code: Mapped[str] = mapped_column(ForeignKey("counties.code"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    period: Mapped[str] = mapped_column(String, nullable=False)

    water_access_improved_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    sanitation_improved_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    open_defecation_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_quality_compliance_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    nrv_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    hours_supply_per_day: Mapped[float | None] = mapped_column(Float, nullable=True)
    billing_efficiency_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    litres_per_capita_per_day: Mapped[float | None] = mapped_column(Float, nullable=True)

    governance_policy_present: Mapped[int | None] = mapped_column(Integer, nullable=True)
    governance_participation_index: Mapped[float | None] = mapped_column(Float, nullable=True)

    drought_risk_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    recharge_potential_index: Mapped[float | None] = mapped_column(Float, nullable=True)

    cholera_outbreak_flag: Mapped[int | None] = mapped_column(Integer, nullable=True)

    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    county_code: Mapped[str] = mapped_column(ForeignKey("counties.code"), nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    rule: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pdf_report_path: Mapped[str | None] = mapped_column(String, nullable=True)

    county: Mapped["County"] = relationship(back_populates="alerts")


class Datasource(Base):
    __tablename__ = "datasources"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    license: Mapped[str | None] = mapped_column(String, nullable=True)
    homepage: Mapped[str | None] = mapped_column(String, nullable=True)

    ingest_runs: Mapped[list["IngestRun"]] = relationship(back_populates="datasource")


class IngestRun(Base):
    __tablename__ = "ingest_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    datasource_id: Mapped[str] = mapped_column(ForeignKey("datasources.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    datasource: Mapped["Datasource"] = relationship(back_populates="ingest_runs")
    artifacts: Mapped[list["IngestArtifact"]] = relationship(back_populates="ingest_run")


class IngestArtifact(Base):
    __tablename__ = "ingest_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ingest_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingest_runs.id"), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    checksum: Mapped[str | None] = mapped_column(String, nullable=True)

    ingest_run: Mapped["IngestRun"] = relationship(back_populates="artifacts")
