"""Pobla la base de datos con datos ficticios para desarrollo/demo.

Uso (desde la raiz del proyecto, con DATABASE_URL apuntando a la BD destino):
    python seed_faker.py

Es idempotente: si ya existen habitaciones, no inserta nada.
"""
import os
import random
import shutil
import sys
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import func, select

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.core.tiempo import hoy_bogota
from app.models import (
    Consumo,
    EstadoHabitacion,
    EstadoLimpieza,
    EstadoReserva,
    Habitacion,
    HabitacionImagen,
    Huesped,
    MetodoPago,
    Pago,
    Reserva,
    RolUsuario,
    TipoDocumento,
    TipoHabitacion,
    TipoPago,
    Usuario,
)

NOMBRES = ["Ana", "Luis", "Maria", "Carlos", "Laura", "Jorge", "Sofia", "Andres"]
APELLIDOS = ["Gomez", "Rojas", "Perez", "Diaz", "Lopez", "Castro", "Vargas", "Mora"]
NACIONALIDADES = ["Colombia", "Mexico", "Espana", "Argentina", "Chile"]
DIRECCIONES = ["Calle 1 #10-20", "Av. 5 #30-40", "Carrera 7 #15-25", "Diagonal 12 #5-6"]

# Carpeta con imagenes de ejemplo, una por tipo de habitacion. Si no existe
# (o no hay archivos), el seed sigue funcionando sin imagenes.
SEED_IMAGENES_DIR = Path(__file__).parent / "app" / "static" / "seed"
EXTENSIONES_IMAGEN = ("jpg", "jpeg", "png", "webp")

# (numero, tipo, capacidad, precio por noche)
HABITACIONES = [
    (101, TipoHabitacion.SIMPLE, 1, "120.00"),
    (102, TipoHabitacion.SIMPLE, 1, "120.00"),
    (201, TipoHabitacion.DOBLE, 2, "180.00"),
    (202, TipoHabitacion.DOBLE, 2, "180.00"),
    (301, TipoHabitacion.SUITE, 3, "280.00"),
    (302, TipoHabitacion.SUITE, 3, "280.00"),
    (401, TipoHabitacion.PRESIDENCIAL, 4, "450.00"),
    (402, TipoHabitacion.PRESIDENCIAL, 4, "450.00"),
]


def _huesped(nombres, apellidos, numero_documento, tipo) -> Huesped:
    return Huesped(
        tipo_documento=tipo,
        numero_documento=numero_documento,
        nombres=nombres,
        apellidos=apellidos,
        email=f"{nombres.lower()}.{apellidos.lower()}.{random.randint(1, 99)}@example.com",
        telefono=f"+57{random.randint(3000000000, 3199999999)}",
        nacionalidad=random.choice(NACIONALIDADES),
        fecha_nacimiento=date(
            random.randint(1970, 2005), random.randint(1, 12), random.randint(1, 28)
        ),
        direccion=random.choice(DIRECCIONES),
    )


def _imagenes_del_tipo(tipo: str) -> list[Path]:
    """Imagenes de ejemplo del tipo, ordenadas (p. ej. doble-1, doble-2)."""
    encontradas: list[Path] = []
    for extension in EXTENSIONES_IMAGEN:
        encontradas.extend(sorted(SEED_IMAGENES_DIR.glob(f"{tipo}-*.{extension}")))
    return encontradas


def _asignar_imagenes(db, habitaciones) -> None:
    """Copia imagenes de ejemplo a MEDIA_DIR y las asocia a cada habitacion.

    Busca, por tipo de habitacion, los archivos `{tipo}-*.{ext}` en
    app/static/seed y los asigna todos (el primero queda como principal). Si no
    hay imagenes del tipo, la habitacion queda sin imagenes.
    """
    directorio_media = Path(settings.media_dir)
    directorio_media.mkdir(parents=True, exist_ok=True)
    for habitacion in habitaciones:
        tipo = habitacion.tipo.value.lower()
        for orden, origen in enumerate(_imagenes_del_tipo(tipo), start=1):
            nombre = f"{uuid4().hex}{origen.suffix}"
            shutil.copyfile(origen, directorio_media / nombre)
            db.add(
                HabitacionImagen(
                    habitacion_id=habitacion.id,
                    ruta=nombre,
                    orden=orden,
                    es_principal=(orden == 1),
                )
            )


def _asignar_imagenes_faltantes(db) -> None:
    """Asigna imagenes de ejemplo a las habitaciones que aun no tienen ninguna.

    Sirve para bases ya pobladas (idempotente: solo toca las que estan sin foto).
    """
    habitaciones = list(db.scalars(select(Habitacion).order_by(Habitacion.numero)))
    pendientes = [h for h in habitaciones if not h.imagenes]
    if not pendientes:
        print("Ya hay datos e imagenes; no se inserta nada.")
        return
    _asignar_imagenes(db, pendientes)
    db.commit()
    print(f"Imagenes de ejemplo asignadas a {len(pendientes)} habitaciones.")


def generar_datos() -> None:
    db = SessionLocal()
    try:
        total = db.scalar(select(func.count()).select_from(Habitacion)) or 0
        if total > 0:
            _asignar_imagenes_faltantes(db)
            return

        usuario = db.scalars(
            select(Usuario).where(Usuario.role == RolUsuario.ADMIN).limit(1)
        ).first()
        if usuario is None:
            usuario = Usuario(
                username="demo.admin",
                email="demo.admin@hotel.local",
                nombre="Demo Admin",
                password_hash=hash_password("DemoAdmin123"),
                role=RolUsuario.ADMIN,
            )
            db.add(usuario)
            db.flush()
            print("Usuario demo creado: demo.admin / DemoAdmin123")

        habitaciones = []
        for numero, tipo, capacidad, precio in HABITACIONES:
            habitacion = Habitacion(
                numero=numero,
                piso=max(1, numero // 100),
                tipo=tipo,
                capacidad=capacidad,
                precio_por_noche=Decimal(precio),
                estado=EstadoHabitacion.DISPONIBLE,
                limpieza=EstadoLimpieza.LIMPIA,
                descripcion=f"Habitacion {tipo.value.lower()} numero {numero}",
            )
            db.add(habitacion)
            habitaciones.append(habitacion)
        db.flush()

        _asignar_imagenes(db, habitaciones)

        huespedes = []
        for i, (nombres, apellidos) in enumerate(zip(NOMBRES, APELLIDOS, strict=True)):
            huesped = _huesped(
                nombres,
                apellidos,
                numero_documento=f"{10000000 + i}",
                tipo=TipoDocumento.PASAPORTE if i % 3 == 0 else TipoDocumento.CC,
            )
            db.add(huesped)
            huespedes.append(huesped)
        db.flush()

        hoy = hoy_bogota()
        for i in range(6):
            entrada = hoy + timedelta(days=random.randint(-3, 10))
            salida = entrada + timedelta(days=random.randint(1, 5))
            habitacion = habitaciones[i % len(habitaciones)]
            noches = (salida - entrada).days
            estado = random.choice(
                [EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA, EstadoReserva.CHECK_IN]
            )
            reserva = Reserva(
                codigo=f"RES-{1000 + i}",
                huesped_id=huespedes[i].id,
                habitacion_id=habitacion.id,
                fecha_entrada=entrada,
                fecha_salida=salida,
                numero_huespedes=min(2, habitacion.capacidad),
                estado=estado,
                precio_noche_aplicado=habitacion.precio_por_noche,
                total_estimado=habitacion.precio_por_noche * noches,
                creada_por=usuario.id,
                check_in_real=datetime.now(UTC) if estado == EstadoReserva.CHECK_IN else None,
            )
            db.add(reserva)
            db.flush()

            if estado == EstadoReserva.CHECK_IN:
                db.add(
                    Consumo(
                        reserva_id=reserva.id,
                        descripcion="Minibar",
                        cantidad=1,
                        precio_unitario=Decimal("15.00"),
                        registrado_por=usuario.id,
                    )
                )
                db.add(
                    Pago(
                        reserva_id=reserva.id,
                        monto=habitacion.precio_por_noche,
                        metodo=MetodoPago.TARJETA,
                        tipo=TipoPago.ABONO,
                        fecha_pago=datetime.now(UTC),
                        registrado_por=usuario.id,
                    )
                )

        db.commit()
        print("Datos ficticios insertados correctamente.")
    except Exception as error:  # noqa: BLE001
        db.rollback()
        print(f"Error al poblar la base de datos: {error}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generar_datos()
