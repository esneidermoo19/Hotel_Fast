import pytest
from pydantic import ValidationError

from app.core.config import DEFAULT_SECRET_KEY, Settings


def test_produccion_rechaza_la_clave_por_defecto() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="production", secret_key=DEFAULT_SECRET_KEY)


def test_cors_origin_regex_segun_entorno() -> None:
    desarrollo = Settings(environment="development")

    assert desarrollo.resolved_cors_origin_regex is not None

    produccion = Settings(
        environment="production",
        secret_key="clave-segura-de-pruebas-con-longitud-1234",
        database_url="postgresql+psycopg://u:p@h:5432/db",
    )
    assert produccion.resolved_cors_origin_regex is None


def test_cors_origin_regex_explicito_precede_al_valor_por_defecto() -> None:
    configurado = Settings(
        environment="production",
        cors_origin_regex=r"^https://app\.hotel\.com$",
        secret_key="clave-segura-de-pruebas-con-longitud-1234",
        database_url="postgresql+psycopg://u:p@h:5432/db",
    )

    assert configurado.resolved_cors_origin_regex == r"^https://app\.hotel\.com$"