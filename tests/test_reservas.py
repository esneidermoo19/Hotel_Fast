from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.tiempo import obtener_hoy
from app.main import app
from app.models import EstadoHabitacion, EstadoReserva, TipoHabitacion
from app.routers.reservas import router
from app.services import reserva_service
from tests.factories import crear_habitacion, crear_huesped, crear_reserva, crear_usuario

HOY = date(2026, 10, 1)


@pytest.fixture
def hoy_fijo():
    """Fija hoy en Bogota para poder crear reservas con fechas concretas."""
    app.dependency_overrides[obtener_hoy] = lambda: HOY
    yield HOY
    app.dependency_overrides.pop(obtener_hoy, None)


def _payload(
    huesped_id: int,
    habitacion_id: int,
    entrada: date = HOY,
    salida: date = HOY + timedelta(days=3),
    numero_huespedes: int = 2,
) -> dict[str, object]:
    return {
        "huespedId": huesped_id,
        "habitacionId": habitacion_id,
        "fechaEntrada": entrada.isoformat(),
        "fechaSalida": salida.isoformat(),
        "numeroHuespedes": numero_huespedes,
    }


def _rango(desde: int, hasta: int) -> dict[str, str]:
    return {
        "entrada": (HOY + timedelta(days=desde)).isoformat(),
        "salida": (HOY + timedelta(days=hasta)).isoformat(),
    }


def _crear(
    db: Session,
    numero: int = 101,
    huesped=None,
    entrada: date = HOY,
    salida: date = HOY + timedelta(days=3),
    estado: EstadoReserva = EstadoReserva.PENDIENTE,
    codigo: str | None = None,
    precio: Decimal = Decimal("150000.00"),
):
    habitacion = crear_habitacion(db, numero=numero, precio_por_noche=precio)
    huesped = huesped or crear_huesped(db, numero_documento=f"1000{numero}")
    usuario = crear_usuario(
        db, username=f"user{numero}", email=f"user{numero}@example.com"
    )
    reserva = crear_reserva(
        db,
        huesped=huesped,
        habitacion=habitacion,
        usuario=usuario,
        codigo=codigo or f"RES-2026-{numero:06d}",
        fecha_entrada=entrada,
        fecha_salida=salida,
        estado=estado,
    )
    return reserva, huesped, habitacion, usuario


def test_reservas_router_prefix() -> None:
    assert router.prefix == "/api/reservas"


# --- Disponibilidad -------------------------------------------------------


def test_disponibilidad_habitacion_libre(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    habitacion = crear_habitacion(db_session, numero=101)

    response = client.get(
        "/api/reservas/disponibilidad",
        params={"entrada": HOY.isoformat(), "salida": (HOY + timedelta(days=2)).isoformat()},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [habitacion.id]
    assert response.json()[0]["precioPorNoche"] == 150000.0


def test_disponibilidad_excluye_habitacion_ocupada(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    _crear(
        db=db_session,
        numero=102,
        entrada=HOY + timedelta(days=1),
        salida=HOY + timedelta(days=4),
    )

    response = client.get(
        "/api/reservas/disponibilidad",
        params=_rango(2, 3),
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_disponibilidad_ignora_habitacion_fuera_de_rango(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    """Una reserva que termina el mismo dia de la entrada no bloquea."""
    _crear(
        db=db_session,
        numero=103,
        entrada=HOY + timedelta(days=1),
        salida=HOY + timedelta(days=3),
    )

    response = client.get(
        "/api/reservas/disponibilidad",
        params=_rango(3, 4),
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert [item["numero"] for item in response.json()] == [103]


def test_disponibilidad_no_bloquean_canceladas(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    _crear(
        db=db_session,
        numero=104,
        estado=EstadoReserva.CANCELADA,
        entrada=HOY + timedelta(days=1),
        salida=HOY + timedelta(days=4),
    )

    response = client.get(
        "/api/reservas/disponibilidad",
        params={"entrada": HOY.isoformat(), "salida": (HOY + timedelta(days=2)).isoformat()},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert [item["numero"] for item in response.json()] == [104]


def test_disponibilidad_filtra_por_capacidad(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    crear_habitacion(db_session, numero=105, capacidad=2)
    crear_habitacion(db_session, numero=106, capacidad=4)

    response = client.get(
        "/api/reservas/disponibilidad",
        params={**_rango(0, 1), "huespedes": 3},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert [item["numero"] for item in response.json()] == [106]


def test_disponibilidad_filtra_por_tipo(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    crear_habitacion(db_session, numero=107, tipo=TipoHabitacion.DOBLE)
    crear_habitacion(db_session, numero=108, tipo=TipoHabitacion.SUITE)

    response = client.get(
        "/api/reservas/disponibilidad",
        params={**_rango(0, 1), "tipo": "SUITE"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert [item["numero"] for item in response.json()] == [108]


def test_disponibilidad_excluye_habitacion_en_mantenimiento(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    crear_habitacion(db_session, numero=109, estado=EstadoHabitacion.MANTENIMIENTO)

    response = client.get(
        "/api/reservas/disponibilidad",
        params={"entrada": HOY.isoformat(), "salida": (HOY + timedelta(days=1)).isoformat()},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_disponibilidad_rango_invalido(
    client: TestClient, admin_headers: dict[str, str], hoy_fijo
) -> None:
    response = client.get(
        "/api/reservas/disponibilidad",
        params={"entrada": (HOY + timedelta(days=3)).isoformat(), "salida": HOY.isoformat()},
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "RANGO_FECHAS_INVALIDO"


# --- Creacion -------------------------------------------------------------


def test_crear_reserva_congela_precio_y_calcula_total(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    habitacion = crear_habitacion(db_session, numero=201, precio_por_noche=Decimal("150000.00"))
    huesped = crear_huesped(db_session)

    response = client.post(
        "/api/reservas", json=_payload(huesped.id, habitacion.id), headers=admin_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["estado"] == "PENDIENTE"
    assert data["precioNocheAplicado"] == 150000.0
    assert data["totalEstimado"] == 450000.0
    assert data["numeroHuespedes"] == 2
    assert data["huesped"]["id"] == huesped.id
    assert data["habitacion"]["numero"] == 201
    assert data["creadaPor"] == 1


def test_crear_reserva_registra_codigo_consecutivo(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)
    primera_habitacion = crear_habitacion(db_session, numero=202)
    segunda_habitacion = crear_habitacion(db_session, numero=203)

    primera = client.post(
        "/api/reservas",
        json=_payload(huesped.id, primera_habitacion.id),
        headers=admin_headers,
    )
    segunda = client.post(
        "/api/reservas",
        json=_payload(huesped.id, segunda_habitacion.id, salida=HOY + timedelta(days=5)),
        headers=admin_headers,
    )

    assert primera.status_code == 201
    assert segunda.status_code == 201
    assert primera.json()["codigo"] == f"RES-{HOY.year}-000001"
    assert segunda.json()["codigo"] == f"RES-{HOY.year}-000002"


def test_codigo_anterior_de_otro_ancho(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    """Un codigo previo mas corto no debe romper el calculo del siguiente."""
    _crear(db=db_session, numero=204, codigo=f"RES-{HOY.year}-9")
    huesped = crear_huesped(db_session)
    otra = crear_habitacion(db_session, numero=205)

    response = client.post(
        "/api/reservas", json=_payload(huesped.id, otra.id), headers=admin_headers
    )

    assert response.status_code == 201
    assert response.json()["codigo"] == f"RES-{HOY.year}-000010"


def test_reintenta_cuando_el_codigo_ya_existe(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
    hoy_fijo,
    monkeypatch,
) -> None:
    _crear(db=db_session, numero=206, codigo=f"RES-{HOY.year}-000001")
    huesped = crear_huesped(db_session)
    otra = crear_habitacion(db_session, numero=207)

    original = reserva_service.generar_codigo
    intentos: list[str] = []

    def generar_con_colision(session, anio: int) -> str:
        if not intentos:
            intentos.append("colision")
            return f"RES-{anio}-000001"
        intentos.append("real")
        return original(session, anio)

    monkeypatch.setattr(reserva_service, "generar_codigo", generar_con_colision)

    response = client.post(
        "/api/reservas", json=_payload(huesped.id, otra.id), headers=admin_headers
    )

    assert response.status_code == 201
    assert intentos == ["colision", "real"]
    assert response.json()["codigo"] == f"RES-{HOY.year}-000002"


def test_agotados_los_reintentos_devuelve_codigo_no_disponible(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
    hoy_fijo,
    monkeypatch,
) -> None:
    huesped = crear_huesped(db_session)
    habitacion = crear_habitacion(db_session, numero=208)
    monkeypatch.setattr(
        reserva_service, "generar_codigo", lambda session, anio: f"RES-{anio}-000001"
    )

    primera = client.post(
        "/api/reservas", json=_payload(huesped.id, habitacion.id), headers=admin_headers
    )
    assert primera.status_code == 201

    otra = crear_habitacion(db_session, numero=209)
    response = client.post(
        "/api/reservas",
        json=_payload(
            huesped.id, otra.id, entrada=HOY + timedelta(days=20), salida=HOY + timedelta(days=22)
        ),
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "CODIGO_RESERVA_NO_DISPONIBLE"


def test_solape_exacto(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)
    _, _, habitacion, _ = _crear(
        db=db_session,
        numero=301,
        huesped=huesped,
        entrada=HOY + timedelta(days=2),
        salida=HOY + timedelta(days=5),
    )

    response = client.post(
        "/api/reservas",
        json=_payload(
            huesped.id,
            habitacion.id,
            entrada=HOY + timedelta(days=2),
            salida=HOY + timedelta(days=5),
        ),
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "RESERVA_SOLAPADA"


def test_solape_parcial_al_final(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huespend = crear_huesped(db_session)
    _, _, habitacion, _ = _crear(
        db=db_session,
        numero=302,
        huesped=huespend,
        entrada=HOY + timedelta(days=2),
        salida=HOY + timedelta(days=5),
    )

    response = client.post(
        "/api/reservas",
        json=_payload(
            huespend.id,
            habitacion.id,
            entrada=HOY + timedelta(days=4),
            salida=HOY + timedelta(days=7),
        ),
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "RESERVA_SOLAPADA"


def test_solape_parcial_al_inicio(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)
    _, _, habitacion, _ = _crear(
        db=db_session,
        numero=303,
        huesped=huesped,
        entrada=HOY + timedelta(days=4),
        salida=HOY + timedelta(days=7),
    )

    response = client.post(
        "/api/reservas",
        json=_payload(
            huesped.id,
            habitacion.id,
            entrada=HOY + timedelta(days=2),
            salida=HOY + timedelta(days=5),
        ),
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "RESERVA_SOLAPADA"


def test_salida_el_mismo_dia_que_otra_entrada_no_solapa(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)
    _, _, habitacion, _ = _crear(
        db=db_session,
        numero=304,
        huesped=huesped,
        entrada=HOY + timedelta(days=2),
        salida=HOY + timedelta(days=5),
    )

    response = client.post(
        "/api/reservas",
        json=_payload(
            huesped.id,
            habitacion.id,
            entrada=HOY + timedelta(days=5),
            salida=HOY + timedelta(days=8),
        ),
        headers=admin_headers,
    )

    assert response.status_code == 201


def test_reservas_canceladas_y_no_show_no_bloquean(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)
    _, _, cancelada_habitacion, _ = _crear(
        db=db_session,
        numero=305,
        huesped=huesped,
        estado=EstadoReserva.CANCELADA,
        entrada=HOY,
        salida=HOY + timedelta(days=3),
    )
    _, _, no_show_habitacion, _ = _crear(
        db=db_session,
        numero=306,
        huesped=huesped,
        estado=EstadoReserva.NO_SHOW,
        entrada=HOY,
        salida=HOY + timedelta(days=3),
    )

    cancelada = client.post(
        "/api/reservas", json=_payload(huesped.id, cancelada_habitacion.id), headers=admin_headers
    )
    no_show = client.post(
        "/api/reservas", json=_payload(huesped.id, no_show_habitacion.id), headers=admin_headers
    )

    assert cancelada.status_code == 201
    assert no_show.status_code == 201


def test_capacidad_excedida(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    habitacion = crear_habitacion(db_session, numero=401, capacidad=2)
    huesped = crear_huesped(db_session)

    response = client.post(
        "/api/reservas",
        json=_payload(huesped.id, habitacion.id, numero_huespedes=5),
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "CAPACIDAD_EXCEDIDA"


def test_habitacion_inexistente(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)

    response = client.post(
        "/api/reservas", json=_payload(huesped.id, 9999), headers=admin_headers
    )

    assert response.status_code == 404
    assert response.json()["code"] == "HABITACION_NO_ENCONTRADA"


def test_huesped_inexistente(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    habitacion = crear_habitacion(db_session, numero=402)

    response = client.post(
        "/api/reservas", json=_payload(9999, habitacion.id), headers=admin_headers
    )

    assert response.status_code == 404
    assert response.json()["code"] == "HUESPED_NO_ENCONTRADO"


def test_habitacion_inactiva(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    habitacion = crear_habitacion(db_session, numero=403, estado=EstadoHabitacion.MANTENIMIENTO)
    huesped = crear_huesped(db_session)

    response = client.post(
        "/api/reservas", json=_payload(huesped.id, habitacion.id), headers=admin_headers
    )

    assert response.status_code == 409
    assert response.json()["code"] == "HABITACION_INACTIVA"


def test_entrada_anterior_a_hoy(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    habitacion = crear_habitacion(db_session, numero=404)
    huesped = crear_huesped(db_session)

    response = client.post(
        "/api/reservas",
        json=_payload(huesped.id, habitacion.id, entrada=HOY - timedelta(days=1)),
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "ENTRADA_EN_PASADO"


def test_salida_no_posterior_a_entrada(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    habitacion = crear_habitacion(db_session, numero=405)
    huesped = crear_huesped(db_session)

    response = client.post(
        "/api/reservas",
        json=_payload(
            huesped.id,
            habitacion.id,
            entrada=HOY + timedelta(days=3),
            salida=HOY + timedelta(days=3),
        ),
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "RANGO_FECHAS_INVALIDO"


# --- Consulta -------------------------------------------------------------


def test_obtener_reserva_con_resumenes(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    reserva, huesped, habitacion, _ = _crear(db=db_session, numero=501)

    response = client.get(f"/api/reservas/{reserva.id}", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["huesped"] == {
        "id": huesped.id,
        "nombres": "Juan",
        "apellidos": "Perez",
        "tipoDocumento": "CC",
        "numeroDocumento": huesped.numero_documento,
    }
    assert data["habitacion"]["id"] == habitacion.id
    assert data["habitacion"]["tipo"] == "DOBLE"


def test_obtener_reserva_inexistente(
    client: TestClient, admin_headers: dict[str, str], hoy_fijo
) -> None:
    response = client.get("/api/reservas/9999", headers=admin_headers)

    assert response.status_code == 404
    assert response.json()["code"] == "RESERVA_NO_ENCONTRADA"


def test_listar_reservas_ordenado_por_entrada_desc(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)
    for offset in range(3):
        _crear(
            db=db_session,
            numero=600 + offset,
            huesped=huesped,
            entrada=HOY + timedelta(days=offset),
            salida=HOY + timedelta(days=offset + 2),
        )

    response = client.get("/api/reservas", headers=admin_headers)

    assert response.status_code == 200
    fechas = [item["fechaEntrada"] for item in response.json()["items"]]
    assert fechas == sorted(fechas, reverse=True)


def test_listar_reservas_paginacion(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)
    for offset in range(5):
        _crear(
            db=db_session,
            numero=610 + offset,
            huesped=huesped,
            entrada=HOY + timedelta(days=offset),
            salida=HOY + timedelta(days=offset + 2),
        )

    primera = client.get(
        "/api/reservas", params={"pagina": 1, "tamano": 2}, headers=admin_headers
    )
    segunda = client.get(
        "/api/reservas", params={"pagina": 2, "tamano": 2}, headers=admin_headers
    )

    assert primera.status_code == 200
    assert primera.json()["total"] == 5
    assert len(primera.json()["items"]) == 2
    assert primera.json()["pagina"] == 1
    assert primera.json()["tamano"] == 2
    assert len(segunda.json()["items"]) == 2
    assert {i["id"] for i in primera.json()["items"]}.isdisjoint(
        {i["id"] for i in segunda.json()["items"]}
    )


def test_listar_reservas_filtros(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)
    otro_huesped = crear_huesped(db_session, numero_documento="9876543210")
    confirmada, _, habitacion_confirmada, _ = _crear(
        db=db_session, numero=701, huesped=huesped, estado=EstadoReserva.CONFIRMADA
    )
    pendiente, _, habitacion_pendiente, _ = _crear(
        db=db_session,
        numero=702,
        huesped=otro_huesped,
        entrada=HOY + timedelta(days=10),
        salida=HOY + timedelta(days=12),
    )

    por_estado = client.get(
        "/api/reservas", params={"estado": "CONFIRMADA"}, headers=admin_headers
    )
    por_habitacion = client.get(
        "/api/reservas",
        params={"habitacionId": habitacion_pendiente.id},
        headers=admin_headers,
    )
    por_huesped = client.get(
        "/api/reservas", params={"huespedId": otro_huesped.id}, headers=admin_headers
    )
    por_fechas = client.get(
        "/api/reservas",
        params={"desde": HOY.isoformat(), "hasta": HOY.isoformat()},
        headers=admin_headers,
    )

    assert por_estado.json()["total"] == 1
    assert por_estado.json()["items"][0]["id"] == confirmada.id
    assert por_habitacion.json()["total"] == 1
    assert por_habitacion.json()["items"][0]["id"] == pendiente.id
    assert por_huesped.json()["total"] == 1
    assert por_huesped.json()["items"][0]["id"] == pendiente.id
    assert por_fechas.json()["total"] == 1
    assert por_fechas.json()["items"][0]["id"] == confirmada.id
    assert habitacion_confirmada.id != habitacion_pendiente.id


def test_listar_reservas_rango_de_fechas_invalido(
    client: TestClient, admin_headers: dict[str, str], hoy_fijo
) -> None:
    response = client.get(
        "/api/reservas",
        params={"desde": (HOY + timedelta(days=5)).isoformat(), "hasta": HOY.isoformat()},
        headers=admin_headers,
    )

    assert response.status_code == 422
    assert response.json()["code"] == "RANGO_FILTROS_INVALIDO"


# --- Actualizacion ---------------------------------------------------------


def test_editar_excluye_la_propia_reserva(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)
    reserva, _, _, _ = _crear(db=db_session, numero=801, huesped=huesped)

    response = client.put(
        f"/api/reservas/{reserva.id}",
        json={"numeroHuespedes": 2, "observaciones": "Sin cambios de fechas"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["observaciones"] == "Sin cambios de fechas"


def test_editar_detecta_solapamiento_con_otra_reserva(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)
    _, _, ocupada, _ = _crear(
        db=db_session,
        numero=802,
        huesped=huesped,
        entrada=HOY + timedelta(days=10),
        salida=HOY + timedelta(days=13),
    )
    editable, _, _, _ = _crear(db=db_session, numero=803, huesped=huesped)

    response = client.put(
        f"/api/reservas/{editable.id}",
        json={
            "habitacionId": ocupada.id,
            "fechaEntrada": (HOY + timedelta(days=11)).isoformat(),
            "fechaSalida": (HOY + timedelta(days=14)).isoformat(),
        },
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "RESERVA_SOLAPADA"


def test_editar_recalcula_precio_con_tarifa_vigente(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    habitacion = crear_habitacion(db_session, numero=804, precio_por_noche=Decimal("200000.00"))
    huesped = crear_huesped(db_session)
    creada = client.post(
        "/api/reservas", json=_payload(huesped.id, habitacion.id), headers=admin_headers
    )
    assert creada.json()["precioNocheAplicado"] == 200000.0
    assert creada.json()["totalEstimado"] == 600000.0

    habitacion.precio_por_noche = Decimal("250000.00")
    db_session.commit()

    response = client.put(
        f"/api/reservas/{creada.json()['id']}",
        json={"fechaSalida": (HOY + timedelta(days=5)).isoformat()},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["precioNocheAplicado"] == 250000.0
    assert response.json()["totalEstimado"] == 1250000.0


def test_editar_conserva_precio_si_no_cambian_fechas_ni_habitacion(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    habitacion = crear_habitacion(db_session, numero=805, precio_por_noche=Decimal("200000.00"))
    huesped = crear_huesped(db_session)
    creada = client.post(
        "/api/reservas", json=_payload(huesped.id, habitacion.id), headers=admin_headers
    )

    habitacion.precio_por_noche = Decimal("999000.00")
    db_session.commit()

    response = client.put(
        f"/api/reservas/{creada.json()['id']}",
        json={"observaciones": "Solo nota"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["precioNocheAplicado"] == 200000.0
    assert response.json()["totalEstimado"] == 600000.0


def test_editar_a_habitacion_mas_carosa_recalcula(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    barata = crear_habitacion(db_session, numero=806, precio_por_noche=Decimal("100000.00"))
    cara = crear_habitacion(db_session, numero=807, precio_por_noche=Decimal("400000.00"))
    huesped = crear_huesped(db_session)
    creada = client.post(
        "/api/reservas", json=_payload(huesped.id, barata.id), headers=admin_headers
    )

    response = client.put(
        f"/api/reservas/{creada.json()['id']}",
        json={"habitacionId": cara.id},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["habitacion"]["id"] == cara.id
    assert response.json()["precioNocheAplicado"] == 400000.0
    assert response.json()["totalEstimado"] == 1200000.0


def test_editar_en_estado_no_editable(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)
    reserva, _, _, _ = _crear(
        db=db_session, numero=808, huesped=huesped, estado=EstadoReserva.CHECK_IN
    )

    response = client.put(
        f"/api/reservas/{reserva.id}",
        json={"numeroHuespedes": 1},
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "RESERVA_NO_EDITABLE"


def test_editar_confirmada_si_se_permite(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)
    reserva, _, _, _ = _crear(
        db=db_session, numero=809, huesped=huesped, estado=EstadoReserva.CONFIRMADA
    )

    response = client.put(
        f"/api/reservas/{reserva.id}",
        json={"observaciones": "Confirmada editable"},
        headers=admin_headers,
    )

    assert response.status_code == 200


def test_editar_capacidad_excedida(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    habitacion = crear_habitacion(db_session, numero=810, capacidad=2)
    huesped = crear_huesped(db_session)
    creada = client.post(
        "/api/reservas", json=_payload(huesped.id, habitacion.id), headers=admin_headers
    )

    response = client.put(
        f"/api/reservas/{creada.json()['id']}",
        json={"numeroHuespedes": 4},
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "CAPACIDAD_EXCEDIDA"


def test_editar_entrada_en_el_pasado(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    huesped = crear_huesped(db_session)
    reserva, _, _, _ = _crear(db=db_session, numero=811, huesped=huesped)

    response = client.put(
        f"/api/reservas/{reserva.id}",
        json={"fechaEntrada": (HOY - timedelta(days=1)).isoformat()},
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "ENTRADA_EN_PASADO"


def test_editar_reserva_ya_iniciada_sin_tocar_la_entrada(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    """Una reserva cuyo ingreso ya paso sigue siendo editable en lo demas.

    El chequeo de fecha pasada solo debe aplicarse cuando la entrada cambia de
    verdad, no cuando ya estaba en el pasado y se reenvia igual.
    """
    huesped = crear_huesped(db_session)
    reserva, _, _, _ = _crear(
        db=db_session,
        numero=812,
        huesped=huesped,
        estado=EstadoReserva.CONFIRMADA,
        entrada=HOY - timedelta(days=2),
        salida=HOY + timedelta(days=2),
    )
    precio_congelado = reserva.precio_noche_aplicado
    total_congelado = reserva.total_estimado

    solo_observaciones = client.put(
        f"/api/reservas/{reserva.id}",
        json={"observaciones": "Ajuste posterior al ingreso"},
        headers=admin_headers,
    )
    misma_entrada = client.put(
        f"/api/reservas/{reserva.id}",
        json={"fechaEntrada": (HOY - timedelta(days=2)).isoformat()},
        headers=admin_headers,
    )

    assert solo_observaciones.status_code == 200
    assert solo_observaciones.json()["precioNocheAplicado"] == float(precio_congelado)
    assert solo_observaciones.json()["totalEstimado"] == float(total_congelado)
    assert solo_observaciones.json()["observaciones"] == "Ajuste posterior al ingreso"
    assert misma_entrada.status_code == 200
    assert misma_entrada.json()["precioNocheAplicado"] == float(precio_congelado)
    assert misma_entrada.json()["totalEstimado"] == float(total_congelado)
    assert misma_entrada.json()["fechaEntrada"] == (HOY - timedelta(days=2)).isoformat()


def test_editar_reserva_inexistente(
    client: TestClient, admin_headers: dict[str, str], hoy_fijo
) -> None:
    response = client.put(
        "/api/reservas/9999", json={"observaciones": "No existe"}, headers=admin_headers
    )

    assert response.status_code == 404
    assert response.json()["code"] == "RESERVA_NO_ENCONTRADA"


# --- Auditoria ------------------------------------------------------------


def test_auditoria_al_crear(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    habitacion = crear_habitacion(db_session, numero=901)
    huesped = crear_huesped(db_session)

    client.post(
        "/api/reservas", json=_payload(huesped.id, habitacion.id), headers=admin_headers
    )

    response = client.get(
        "/api/auditoria",
        params={"entidad": "Reserva", "accion": "CREATE"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert "password" not in str(response.json())


def test_auditoria_al_editar(
    client: TestClient, admin_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    habitacion = crear_habitacion(db_session, numero=902)
    huesped = crear_huesped(db_session)
    creada = client.post(
        "/api/reservas", json=_payload(huesped.id, habitacion.id), headers=admin_headers
    )

    client.put(
        f"/api/reservas/{creada.json()['id']}",
        json={"observaciones": "Cambio"},
        headers=admin_headers,
    )

    response = client.get(
        "/api/auditoria",
        params={"entidad": "Reserva", "accion": "UPDATE"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1


# --- Permisos -------------------------------------------------------------


def test_recepcion_puede_gestionar_reservas(
    client: TestClient, recepcion_headers: dict[str, str], db_session: Session, hoy_fijo
) -> None:
    habitacion = crear_habitacion(db_session, numero=1001)
    huesped = crear_huesped(db_session)

    creada = client.post(
        "/api/reservas", json=_payload(huesped.id, habitacion.id), headers=recepcion_headers
    )

    assert creada.status_code == 201
    listado = client.get("/api/reservas", headers=recepcion_headers)
    detalle = client.get(f"/api/reservas/{creada.json()['id']}", headers=recepcion_headers)
    editar = client.put(
        f"/api/reservas/{creada.json()['id']}",
        json={"observaciones": "Recepcion"},
        headers=recepcion_headers,
    )
    disponibilidad = client.get(
        "/api/reservas/disponibilidad",
        params={"entrada": HOY.isoformat(), "salida": (HOY + timedelta(days=1)).isoformat()},
        headers=recepcion_headers,
    )

    assert listado.status_code == 200
    assert detalle.status_code == 200
    assert editar.status_code == 200
    assert disponibilidad.status_code == 200


def test_rutas_requieren_token(client: TestClient) -> None:
    assert client.get("/api/reservas").status_code == 401
    assert client.get(
        "/api/reservas/disponibilidad",
        params={"entrada": HOY.isoformat(), "salida": (HOY + timedelta(days=1)).isoformat()},
    ).status_code == 401
    assert client.post("/api/reservas", json={}).status_code == 401