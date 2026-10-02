"""auditoria y usuarios activos

Revision ID: c3e8f0a5d1b7
Revises: b7d2e91a4c3f
Create Date: 2026-10-02 19:20:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c3e8f0a5d1b7"
down_revision: str | None = "b7d2e91a4c3f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "auditoria",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("accion", sa.String(length=64), nullable=False),
        sa.Column("entidad", sa.String(length=64), nullable=False),
        sa.Column("entidad_id", sa.Integer(), nullable=True),
        sa.Column("direccion_ip", sa.String(length=45), nullable=True),
        sa.Column("detalle", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.id"],
            name=op.f("fk_auditoria_usuario_id_usuarios"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auditoria")),
    )
    op.create_index("ix_auditoria_accion", "auditoria", ["accion"], unique=False)
    op.create_index(
        "ix_auditoria_created_at", "auditoria", ["created_at"], unique=False
    )
    op.create_index("ix_auditoria_entidad", "auditoria", ["entidad"], unique=False)
    op.create_index(
        "ix_auditoria_entidad_entidad_id",
        "auditoria",
        ["entidad", "entidad_id"],
        unique=False,
    )
    op.create_index(
        "ix_auditoria_usuario_id", "auditoria", ["usuario_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_auditoria_usuario_id", table_name="auditoria")
    op.drop_index("ix_auditoria_entidad_entidad_id", table_name="auditoria")
    op.drop_index("ix_auditoria_entidad", table_name="auditoria")
    op.drop_index("ix_auditoria_created_at", table_name="auditoria")
    op.drop_index("ix_auditoria_accion", table_name="auditoria")
    op.drop_table("auditoria")
    op.drop_column("usuarios", "activo")
