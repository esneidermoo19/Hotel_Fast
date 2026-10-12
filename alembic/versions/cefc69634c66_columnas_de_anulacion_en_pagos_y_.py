"""columnas de anulacion en pagos y consumos

Revision ID: cefc69634c66
Revises: 61ef2ec30e78
Create Date: 2026-10-12 14:50:09.017587
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op


revision: str = 'cefc69634c66'
down_revision: str | None = '61ef2ec30e78'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Columnas de auditoria de la anulacion: quien la hizo y cuando. El motivo
    # ya existia en pagos; en consumos se agrega.
    op.add_column('pagos', sa.Column('anulado_por', sa.Integer(), nullable=True))
    op.add_column(
        'pagos', sa.Column('anulado_en', sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column('consumos', sa.Column('motivo_anulacion', sa.Text(), nullable=True))
    op.add_column('consumos', sa.Column('anulado_por', sa.Integer(), nullable=True))
    op.add_column(
        'consumos',
        sa.Column('anulado_en', sa.DateTime(timezone=True), nullable=True),
    )

    # PostgreSQL: FK a usuarios. SQLite no permite agregar constraints a tablas
    # existentes y usa create_all para desarrollo.
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.create_foreign_key(
            op.f('fk_pagos_anulado_por_usuarios'),
            'pagos',
            'usuarios',
            ['anulado_por'],
            ['id'],
            ondelete='SET NULL',
        )
        op.create_foreign_key(
            op.f('fk_consumos_anulado_por_usuarios'),
            'consumos',
            'usuarios',
            ['anulado_por'],
            ['id'],
            ondelete='SET NULL',
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.drop_constraint(
            op.f('fk_consumos_anulado_por_usuarios'), 'consumos', type_='foreignkey'
        )
        op.drop_constraint(
            op.f('fk_pagos_anulado_por_usuarios'), 'pagos', type_='foreignkey'
        )
    op.drop_column('consumos', 'anulado_en')
    op.drop_column('consumos', 'anulado_por')
    op.drop_column('consumos', 'motivo_anulacion')
    op.drop_column('pagos', 'anulado_en')
    op.drop_column('pagos', 'anulado_por')
