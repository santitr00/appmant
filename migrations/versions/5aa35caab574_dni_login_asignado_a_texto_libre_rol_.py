"""dni login, asignado_a texto libre, rol admin usuario

Revision ID: 5aa35caab574
Revises: 423107f54206
Create Date: 2026-03-12 14:34:48.511090

"""
from alembic import op
import sqlalchemy as sa

revision = '5aa35caab574'
down_revision = '423107f54206'
branch_labels = None
depends_on = None


def _col_type(conn, table, col):
    """Devuelve el tipo actual de una columna o None si no existe."""
    row = conn.execute(sa.text(
        "SELECT COLUMN_TYPE FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c"
    ), {"t": table, "c": col}).fetchone()
    return row[0].lower() if row else None


def upgrade():
    conn = op.get_bind()

    # 1. asignado_a → VARCHAR(150) si todavía es INT
    for table in ("tareas_excepcionales", "tareas_programadas"):
        if _col_type(conn, table, "asignado_a") and "int" in _col_type(conn, table, "asignado_a"):
            # Eliminar FK que apunta a usuarios.id antes de cambiar el tipo
            fk = conn.execute(sa.text(
                "SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t "
                "AND COLUMN_NAME = 'asignado_a' AND REFERENCED_TABLE_NAME IS NOT NULL"
            ), {"t": table}).fetchone()
            if fk:
                conn.execute(sa.text(f"ALTER TABLE {table} DROP FOREIGN KEY {fk[0]}"))
            conn.execute(sa.text(f"ALTER TABLE {table} MODIFY COLUMN asignado_a VARCHAR(150) NULL"))

    # 2. dni: agregar si no existe
    if _col_type(conn, "usuarios", "dni") is None:
        conn.execute(sa.text("ALTER TABLE usuarios ADD COLUMN dni VARCHAR(20) NULL"))

    # 3. email → nullable si no lo es
    conn.execute(sa.text("ALTER TABLE usuarios MODIFY COLUMN email VARCHAR(180) NULL"))

    # 4. rol: ampliar ENUM, mapear datos, luego reducir a valores finales
    rol_type = _col_type(conn, "usuarios", "rol") or ""
    if "intendente" in rol_type:
        # Paso 4a: ampliar ENUM para aceptar los 4 valores durante la transición
        conn.execute(sa.text(
            "ALTER TABLE usuarios MODIFY COLUMN rol "
            "ENUM('intendente','encargado','admin','usuario') NOT NULL"
        ))
        # Paso 4b: migrar los datos
        conn.execute(sa.text("UPDATE usuarios SET rol = 'admin'   WHERE rol = 'intendente'"))
        conn.execute(sa.text("UPDATE usuarios SET rol = 'usuario' WHERE rol = 'encargado'"))
        # Paso 4c: dejar solo los nuevos valores
        conn.execute(sa.text(
            "ALTER TABLE usuarios MODIFY COLUMN rol ENUM('admin','usuario') NOT NULL DEFAULT 'usuario'"
        ))

    # 5. dni: poblar, hacer NOT NULL y UNIQUE
    conn.execute(sa.text("UPDATE usuarios SET dni = CONCAT('tmp_', id) WHERE dni IS NULL"))
    conn.execute(sa.text("ALTER TABLE usuarios MODIFY COLUMN dni VARCHAR(20) NOT NULL"))

    idx = conn.execute(sa.text(
        "SELECT INDEX_NAME FROM information_schema.STATISTICS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'usuarios' AND INDEX_NAME = 'uq_usuarios_dni'"
    )).fetchone()
    if not idx:
        conn.execute(sa.text("ALTER TABLE usuarios ADD UNIQUE INDEX uq_usuarios_dni (dni)"))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE usuarios DROP INDEX uq_usuarios_dni"))
    conn.execute(sa.text("ALTER TABLE usuarios DROP COLUMN dni"))
    conn.execute(sa.text("ALTER TABLE usuarios MODIFY COLUMN email VARCHAR(180) NOT NULL"))
    conn.execute(sa.text("UPDATE usuarios SET rol = 'intendente' WHERE rol = 'admin'"))
    conn.execute(sa.text("UPDATE usuarios SET rol = 'encargado'  WHERE rol = 'usuario'"))
    conn.execute(sa.text("ALTER TABLE usuarios MODIFY COLUMN rol ENUM('intendente','encargado') NOT NULL"))
    conn.execute(sa.text("ALTER TABLE tareas_excepcionales MODIFY COLUMN asignado_a INT NULL"))
    conn.execute(sa.text("ALTER TABLE tareas_programadas   MODIFY COLUMN asignado_a INT NULL"))
