import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def test_health_consulta_la_base_de_datos(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_devuelve_503_si_falla_la_base_de_datos(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_execute(
        session: Session,
        statement: object,
        *args: object,
        **kwargs: object,
    ) -> None:
        raise SQLAlchemyError("fallo simulado")

    monkeypatch.setattr(Session, "execute", fail_execute)
    response = client.get("/api/health")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Base de datos no disponible",
        "code": "NO_DISPONIBLE",
    }