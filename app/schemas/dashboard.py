from pydantic import Field

from app.schemas.base import CamelCaseSchema


class DashboardRead(CamelCaseSchema):
    """Resumen operativo del hotel para un día concreto."""

    reservas_activas: int = Field(
        description="Reservas en PENDIENTE, CONFIRMADA o CHECK_IN"
    )
    reservas_pendientes_check_in: int = Field(
        description="Reservas que aun no han hecho check-in (PENDIENTE o CONFIRMADA)"
    )
    huespedes_alojados: int = Field(
        description="Suma de numero_huespedes de las reservas en CHECK_IN"
    )
    check_outs_del_dia: int = Field(
        description="Check-outs con check_out_real dentro del dia en America/Bogota"
    )
    habitaciones_disponibles: int = Field(
        description="Habitaciones en estado DISPONIBLE"
    )
    habitaciones_ocupadas: int = Field(description="Habitaciones en estado OCUPADA")
    habitaciones_en_mantenimiento: int = Field(
        description="Habitaciones en estado MANTENIMIENTO"
    )
    cuentas_con_saldo_pendiente: int = Field(
        description="Reservas con saldo pendiente mayor que cero"
    )
