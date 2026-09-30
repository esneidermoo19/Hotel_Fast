"""usuarios y habitaciones

Revision ID: 487525d6a687
Revises:
Create Date: 2026-09-30 15:26:48.399435
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = '487525d6a687'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### comandos generados automaticamente por Alembic; revisar antes de aplicar ###
    op.create_table('habitaciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('numero', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.Enum('SIMPLE', 'DOBLE', 'SUITE', 'PRESIDENCIAL', name='tipo_habitacion'), nullable=False),
    sa.Column('capacidad', sa.Integer(), nullable=False),
    sa.Column('precio_por_noche', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('estado', sa.Enum('DISPONIBLE', 'OCUPADA', 'MANTENIMIENTO', name='estado_habitacion'), nullable=False),
    sa.Column('descripcion', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('capacidad >= 1', name=op.f('ck_habitaciones_capacidad_positiva')),
    sa.CheckConstraint('numero > 0', name=op.f('ck_habitaciones_numero_positivo')),
    sa.CheckConstraint('precio_por_noche > 0', name=op.f('ck_habitaciones_precio_positivo')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_habitaciones')),
    sa.UniqueConstraint('numero', name=op.f('uq_habitaciones_numero'))
    )
    op.create_table('usuarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=254), nullable=False),
    sa.Column('nombre', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('ADMIN', 'RECEPCION', name='rol_usuario'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_usuarios')),
    sa.UniqueConstraint('email', name=op.f('uq_usuarios_email')),
    sa.UniqueConstraint('username', name=op.f('uq_usuarios_username'))
    )
    # ### fin de los comandos Alembic ###


def downgrade() -> None:
    # ### comandos generados automaticamente por Alembic ###
    op.drop_table('usuarios')
    op.drop_table('habitaciones')
    # ### fin de los comandos Alembic ###