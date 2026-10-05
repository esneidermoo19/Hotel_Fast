"""Utilidades de tiempo: única fuente de verdad para zona America/Bogota."""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

ZONA = ZoneInfo("America/Bogota")


def ahora_utc() -> datetime:
    """Devuelve el instante actual en UTC (aware)."""
    return datetime.now(UTC)


def hoy_bogota() -> date:
    """Devuelve la fecha de hoy en zona America/Bogota."""
    return ahora_utc().astimezone(ZONA).date()


def como_utc(dt: datetime) -> datetime:
    """Normaliza un datetime a UTC.
    - Si es aware, lo convierte a UTC.
    - Si es naive (p.ej. SQLite), lo trata como UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def obtener_hoy() -> date:
    """Dependencia FastAPI que devuelve hoy en Bogotá.
    Sobrescribible en tests con app.dependency_overrides.
    """
    return hoy_bogota()


def limites_utc_del_dia(fecha: date) -> tuple[datetime, datetime]:
    """Devuelve (inicio_utc, fin_exclusivo_utc) para un día en Bogotá.
    fin_exclusivo_utc = 00:00 del día siguiente en Bogotá, convertido a UTC.
    """
    inicio_utc = datetime.combine(fecha, time.min, tzinfo=ZONA).astimezone(UTC)
    fin_exclusivo_utc = datetime.combine(
        fecha + timedelta(days=1), time.min, tzinfo=ZONA
    ).astimezone(UTC)
    return inicio_utc, fin_exclusivo_utc


def limites_utc_de_rango(
    desde: date | None, hasta: date | None
) -> tuple[datetime | None, datetime | None]:
    """Devuelve (inicio_utc, fin_exclusivo_utc) para un rango de fechas en Bogotá.
    - Si desde es None, inicio_utc es None.
    - Si hasta es None, fin_exclusivo_utc es None.
    No valida desde <= hasta (lo hace el caller).
    """
    inicio_utc = None
    fin_exclusivo_utc = None
    if desde is not None:
        inicio_utc = datetime.combine(desde, time.min, tzinfo=ZONA).astimezone(UTC)
    if hasta is not None:
        fin_exclusivo_utc = datetime.combine(
            hasta + timedelta(days=1), time.min, tzinfo=ZONA
        ).astimezone(UTC)
    return inicio_utc, fin_exclusivo_utc


def inicio_de_semana(fecha: date) -> date:
    """Devuelve el lunes de la semana de la fecha dada."""
    return fecha - timedelta(days=fecha.weekday())


def fin_de_semana(fecha: date) -> date:
    """Devuelve el domingo de la semana de la fecha dada."""
    return fecha + timedelta(days=6 - fecha.weekday())