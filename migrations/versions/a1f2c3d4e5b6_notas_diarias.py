"""notas diarias

Revision ID: a1f2c3d4e5b6
Revises: 19eda2ed9af2
Create Date: 2026-07-01 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1f2c3d4e5b6'
down_revision = '19eda2ed9af2'
branch_labels = None
depends_on = None


def _tabla_existe(conn, tabla):
    row = conn.execute(sa.text(
        "SELECT COUNT(*) FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t"
    ), {"t": tabla}).fetchone()
    return bool(row and row[0])


def upgrade():
    conn = op.get_bind()
    if _tabla_existe(conn, "notas_diarias"):
        return

    op.create_table(
        "notas_diarias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("barrio_id", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("contenido", sa.Text(), nullable=False),
        sa.Column("creada_por", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["barrio_id"], ["barrios.id"]),
        sa.ForeignKeyConstraint(["creada_por"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("barrio_id", "fecha", name="uq_nota_barrio_fecha"),
    )


def downgrade():
    conn = op.get_bind()
    if _tabla_existe(conn, "notas_diarias"):
        op.drop_table("notas_diarias")
