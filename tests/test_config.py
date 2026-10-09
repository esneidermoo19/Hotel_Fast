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


def test_cors_origins_se_sanea_desde_json() -> None:
    configurado = Settings(
        environment="development",
        cors_origins='["https://hotelfront.ttr.lat", "https://www.hotelfront.ttr.lat/"]',
    )

    assert configurado.cors_origins == [
        "https://hotelfront.ttr.lat",
        "https://www.hotelfront.ttr.lat",
    ]


def test_cors_origins_se_separa_por_comas() -> None:
    configurado = Settings(
        environment="development",
        cors_origins="https://a.ttr.lat, https://b.ttr.lat/",
    )

    assert configurado.cors_origins == ["https://a.ttr.lat", "https://b.ttr.lat"]


def test_cors_origins_vacio_o_comodin_usan_star() -> None:
    assert Settings(environment="development", cors_origins="").cors_origins == ["*"]
    assert Settings(
        environment="development", cors_origins='["*"]'
    ).cors_origins == ["*"]


def test_cors_allow_credentials_segun_comodin() -> None:
    assert (
        Settings(
            environment="development", cors_origins='["*"]'
        ).cors_allow_credentials
        is False
    )
    assert (
        Settings(
            environment="development", cors_origins='["https://a.ttr.lat"]'
        ).cors_allow_credentials
        is True
    )