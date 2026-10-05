"""Tests para app.core.tiempo."""

from datetime import UTC, date, datetime

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.tiempo import (
    ZONA,
    ahora_utc,
    como_utc,
    fin_de_semana,
    hoy_bogota,
    inicio_de_semana,
    limites_utc_de_rango,
    limites_utc_del_dia,
    obtener_hoy,
)


def test_limites_utc_del_dia_un_solo_dia() -> None:
    """Límites de un día en Bogotá convertidos a UTC."""
    fecha = date(2026, 10, 4)
    inicio_utc, fin_exclusivo_utc = limites_utc_del_dia(fecha)

    # Bogotá es UTC-5, así que 00:00 Bogotá = 05:00 UTC
    assert inicio_utc == datetime(2026, 10, 4, 5, 0, tzinfo=UTC)
    # Fin exclusivo = 00:00 del día siguiente en Bogotá = 05:00 UTC del día siguiente
    assert fin_exclusivo_utc == datetime(2026, 10, 5, 5, 0, tzinfo=UTC)


def test_limites_utc_de_rango_varios_dias() -> None:
    """Rango de varios días."""
    desde = date(2026, 10, 4)
    hasta = date(2026, 10, 6)
    inicio_utc, fin_exclusivo_utc = limites_utc_de_rango(desde, hasta)

    assert inicio_utc == datetime(2026, 10, 4, 5, 0, tzinfo=UTC)
    assert fin_exclusivo_utc == datetime(2026, 10, 7, 5, 0, tzinfo=UTC)


def test_limites_utc_de_rango_un_solo_dia() -> None:
    """Rango donde desde == hasta."""
    dia = date(2026, 10, 4)
    inicio_utc, fin_exclusivo_utc = limites_utc_de_rango(dia, dia)

    assert inicio_utc == datetime(2026, 10, 4, 5, 0, tzinfo=UTC)
    assert fin_exclusivo_utc == datetime(2026, 10, 5, 5, 0, tzinfo=UTC)


def test_limites_utc_de_rango_solo_desde() -> None:
    """Rango solo con fecha desde."""
    desde = date(2026, 10, 4)
    inicio_utc, fin_exclusivo_utc = limites_utc_de_rango(desde, None)

    assert inicio_utc == datetime(2026, 10, 4, 5, 0, tzinfo=UTC)
    assert fin_exclusivo_utc is None


def test_limites_utc_de_rango_solo_hasta() -> None:
    """Rango solo con fecha hasta."""
    hasta = date(2026, 10, 4)
    inicio_utc, fin_exclusivo_utc = limites_utc_de_rango(None, hasta)

    assert inicio_utc is None
    assert fin_exclusivo_utc == datetime(2026, 10, 5, 5, 0, tzinfo=UTC)


def test_limites_utc_de_rango_ambos_none() -> None:
    """Rango sin fechas."""
    inicio_utc, fin_exclusivo_utc = limites_utc_de_rango(None, None)
    assert inicio_utc is None
    assert fin_exclusivo_utc is None


def test_semana_cruza_mes() -> None:
    """Semana que cruza de mes (octubre a noviembre 2026)."""
    # 2026-10-31 es sábado, semana va del lunes 26 oct al domingo 1 nov
    fecha = date(2026, 10, 31)
    assert inicio_de_semana(fecha) == date(2026, 10, 26)
    assert fin_de_semana(fecha) == date(2026, 11, 1)


def test_semana_cruza_ano() -> None:
    """Semana que cruza de año (diciembre 2026 a enero 2027)."""
    # 2026-12-31 es jueves, semana va del lunes 28 dic al domingo 3 ene 2027
    fecha = date(2026, 12, 31)
    assert inicio_de_semana(fecha) == date(2026, 12, 28)
    assert fin_de_semana(fecha) == date(2027, 1, 3)


def test_cambio_dia_utc_mismo_dia_bogota() -> None:
    """Eventos a las 23:59 y 00:01 de Bogotá del mismo día caen en días UTC distintos."""
    # 2026-10-04 23:59 Bogotá = 2026-10-05 04:59 UTC
    evento_tarde = datetime(2026, 10, 4, 23, 59, tzinfo=ZONA).astimezone(UTC)
    # 2026-10-05 00:01 Bogotá = 2026-10-05 05:01 UTC
    evento_temprano = datetime(2026, 10, 5, 0, 1, tzinfo=ZONA).astimezone(UTC)

    # Ambos eventos pertenecen al día 2026-10-04 en Bogotá
    inicio_dia, fin_dia = limites_utc_del_dia(date(2026, 10, 4))

    assert inicio_dia <= evento_tarde < fin_dia
    # El evento a las 00:01 de Bogotá del 5 de octubre NO está en el día 4
    assert not (inicio_dia <= evento_temprano < fin_dia)


def test_como_utc_con_aware() -> None:
    """como_utc convierte datetime aware a UTC."""
    dt_bogota = datetime(2026, 10, 4, 12, 0, tzinfo=ZONA)
    dt_utc = como_utc(dt_bogota)
    assert dt_utc.tzinfo == UTC
    # 12:00 Bogotá = 17:00 UTC
    assert dt_utc == datetime(2026, 10, 4, 17, 0, tzinfo=UTC)


def test_como_utc_con_naive() -> None:
    """como_utc trata datetime naive como UTC."""
    dt_naive = datetime(2026, 10, 4, 17, 0)
    dt_utc = como_utc(dt_naive)
    assert dt_utc.tzinfo == UTC
    assert dt_utc == datetime(2026, 10, 4, 17, 0, tzinfo=UTC)


def test_obtener_hoy_sobrescrita_dependency_override() -> None:
    """obtener_hoy puede sobrescribirse con FastAPI dependency_overrides."""
    app = FastAPI()

    @app.get("/hoy")
    def leer_hoy(hoy: date = Depends(obtener_hoy)) -> dict[str, str]:  # noqa: B008
        return {"hoy": hoy.isoformat()}

    client = TestClient(app)

    # Sin override: usa la implementación real (hoy en Bogotá)
    response = client.get("/hoy")
    assert response.status_code == 200
    assert response.json() == {"hoy": hoy_bogota().isoformat()}

    # Con override
    fecha_fija = date(2026, 1, 1)
    app.dependency_overrides[obtener_hoy] = lambda: fecha_fija
    try:
        response = client.get("/hoy")
        assert response.status_code == 200
        assert response.json() == {"hoy": "2026-01-01"}
    finally:
        app.dependency_overrides.clear()

    # Sin override de nuevo: vuelve a la implementación real
    response = client.get("/hoy")
    assert response.status_code == 200
    assert response.json() == {"hoy": hoy_bogota().isoformat()}


def test_ahora_utc_es_aware() -> None:
    """ahora_utc devuelve datetime aware en UTC."""
    dt = ahora_utc()
    assert dt.tzinfo == UTC


def test_hoy_bogota_consistente_con_ahora_utc() -> None:
    """hoy_bogota() == ahora_utc().astimezone(ZONA).date()."""
    assert hoy_bogota() == ahora_utc().astimezone(ZONA).date()


def test_zona_es_bogota() -> None:
    """ZONA es America/Bogota."""
    assert str(ZONA) == "America/Bogota"