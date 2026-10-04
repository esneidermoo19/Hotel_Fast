"""Reglas de fortaleza de contraseña.

Se viven aparte porque las aplican tanto los schemas (que devuelven 422 con
el detalle por campo) como los servicios (que lanzan error de dominio).
"""

import re

LONGITUD_MINIMA = 8
LONGITUD_MAXIMA = 128


def problemas_de_fortaleza(password: str) -> list[str]:
    """Devuelve la lista de requisitos incumplidos (vacía si es válida)."""
    problemas: list[str] = []
    if len(password) < LONGITUD_MINIMA:
        problemas.append(f"debe tener al menos {LONGITUD_MINIMA} caracteres")
    if len(password) > LONGITUD_MAXIMA:
        problemas.append(f"no puede superar {LONGITUD_MAXIMA} caracteres")
    if not re.search(r"[A-Za-z]", password):
        problemas.append("debe incluir al menos una letra")
    if not re.search(r"\d", password):
        problemas.append("debe incluir al menos un numero")
    return problemas


def es_valida(password: str) -> bool:
    return not problemas_de_fortaleza(password)


def mensaje_de_fortaleza(password: str) -> str:
    problemas = problemas_de_fortaleza(password)
    if not problemas:
        return ""
    return "La contraseña " + ", ".join(problemas)
