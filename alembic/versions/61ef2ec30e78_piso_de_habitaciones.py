"""piso de habitaciones

Revision ID: 61ef2ec30e78
Revises: c8057524b437
Create Date: 2026-10-11 00:39:44.113723
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op


revision: str = '61ef2ec30e78'
down_revision: str | None = 'c8057524b437'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Se agrega como nullable, se rellena a partir del numero de habitacion y
    # luego se exige NOT NULL, para no fallar en bases que ya tienen filas
    # (mismo patron que la columna limpieza).
    op.add_column('habitaciones', sa.Column('piso', sa.Integer(), nullable=True))
    op.execute(
        "UPDATE habitaciones SET piso = "
        "CASE WHEN numero / 100 >= 1 THEN numero / 100 ELSE 1 END"
    )
    op.alter_column(
        'habitaciones',
        'piso',
        existing_type=sa.Integer(),
        nullable=False,
    )

    # PostgreSQL: la restriccion piso > 0 se agrega con ALTER TABLE (SQLite no
    # permite agregar CHECK a tablas existentes y usa create_all para desarrollo).
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.create_check_constraint(
            'piso_positivo',
            'habitaciones',
            'piso > 0',
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.drop_constraint('piso_positivo', 'habitaciones', type_='check')
    op.drop_column('habitaciones', 'piso')
