from app.controllers.auth import router


def test_auth_router_prefix():
    assert router.prefix == "/auth"
