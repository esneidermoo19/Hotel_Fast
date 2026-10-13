import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.seguridad_http import cabeceras_de_seguridad, excede_limite_cuerpo


def test_cabeceras_de_seguridad_incluye_hsts_solo_en_produccion() -> None:
    desarrollo = cabeceras_de_seguridad(produccion=False)
    produccion = cabeceras_de_seguridad(produccion=True)

    assert "Strict-Transport-Security" not in desarrollo
    assert produccion["Strict-Transport-Security"] == (
        "max-age=31536000; includeSubDomains"
    )


def test_cabeceras_de_seguridad_presentes_en_cada_respuesta(
    client: TestClient,
) -> None:
    response = client.get("/api/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "x-content-type-options" in response.headers


@pytest.mark.parametrize(
    ("content_length", "limite", "esperado"),
    [
        (None, 100, False),
        ("50", 100, False),
        ("200", 100, True),
        ("no-numerico", 100, False),
        ("200", 0, False),
    ],
)
def test_excede_limite_cuerpo(
    content_length: str | None,
    limite: int,
    esperado: bool,
) -> None:
    assert excede_limite_cuerpo(content_length, limite) is esperado


def test_cuerpo_muy_grande_devuelve_413(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "max_request_body_bytes", 10)

    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "x" * 100},
        headers={"Origin": "http://localhost:5173"},
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "El cuerpo de la solicitud es demasiado grande",
        "code": "CUERPO_MUY_GRANDE",
    }
    # CORS cubre tambien las respuestas generadas por middlewares internos.
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
