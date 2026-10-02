from collections.abc import Generator, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.limiter import limiter
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models import RolUsuario, Usuario

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def isolate_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    # El limite de intentos se prueba explicitamente, no en cada test.
    limiter.enabled = False
    yield
    limiter.enabled = True
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session() -> Iterator[Session]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def _create_user(role: RolUsuario) -> Usuario:
    db = TestingSessionLocal()
    try:
        user = Usuario(
            username="admin" if role == RolUsuario.ADMIN else "recepcion",
            email=(
                "admin@example.com"
                if role == RolUsuario.ADMIN
                else "recepcion@example.com"
            ),
            nombre="Administrador" if role == RolUsuario.ADMIN else "Recepcion",
            password_hash=hash_password("test-password-123"),
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


@pytest.fixture
def admin_user() -> Usuario:
    return _create_user(RolUsuario.ADMIN)


@pytest.fixture
def recepcion_user() -> Usuario:
    return _create_user(RolUsuario.RECEPCION)


@pytest.fixture
def admin_headers(admin_user: Usuario) -> dict[str, str]:
    token = create_access_token(admin_user.id, admin_user.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def recepcion_headers(recepcion_user: Usuario) -> dict[str, str]:
    token = create_access_token(recepcion_user.id, recepcion_user.role.value)
    return {"Authorization": f"Bearer {token}"}
