"""Bloqueo temporal de cuentas tras intentos fallidos de autenticacion.

Complementa al limite por IP: un atacante que rota de IP igual enfrenta un
tope de intentos por identificador. La ventana es deslizante y el estado vive
en memoria del proceso (suficiente para un despliegue de un solo worker); al
reiniciar, los contadores se limpian. Se registra el identificador tal como lo
normaliza el servicio de autenticacion (minusculas).
"""

import threading
import time
from collections import deque

from app.core.config import settings

_lock = threading.Lock()
_intentos: dict[str, deque[float]] = {}


def _ahora() -> float:
    return time.time()


def _ventana_segundos() -> float:
    return settings.login_lockout_minutes * 60


def _purgar(cola: deque[float], limite: float) -> None:
    while cola and cola[0] < limite:
        cola.popleft()


def registrar_intento_fallido(identificador: str) -> None:
    """Anota un intento fallido y descarta los que salieron de la ventana."""
    if not settings.login_lockout_enabled:
        return
    limite = _ahora() - _ventana_segundos()
    with _lock:
        cola = _intentos.setdefault(identificador, deque())
        _purgar(cola, limite)
        cola.append(_ahora())


def esta_bloqueado(identificador: str) -> bool:
    """True si el identificador alcanzo el maximo de intentos en la ventana."""
    if not settings.login_lockout_enabled:
        return False
    limite = _ahora() - _ventana_segundos()
    with _lock:
        cola = _intentos.get(identificador)
        if not cola:
            return False
        _purgar(cola, limite)
        return len(cola) >= settings.login_max_attempts


def limpiar_intentos(identificador: str) -> None:
    """Descarta los intentos de un identificador (autenticacion correcta)."""
    with _lock:
        _intentos.pop(identificador, None)


def reiniciar() -> None:
    """Limpia todo el estado (uso en pruebas y reinicios controlados)."""
    with _lock:
        _intentos.clear()
