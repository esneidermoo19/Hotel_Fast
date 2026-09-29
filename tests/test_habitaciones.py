from app.controllers.habitaciones import router


def test_habitaciones_router_prefix():
    assert router.prefix == "/habitaciones"
