"""
Script de seed para testing inicial.
Crea un barrio, un admin y un usuario de ejemplo.

Uso:
    py -3.12 seed.py
"""
import os
from datetime import time
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import Barrio, Usuario, PlantillaTarea

app = create_app(os.environ.get("FLASK_ENV", "development"))


def seed():
    with app.app_context():
        # ── Barrio ────────────────────────────────────────────────────────────
        barrio = Barrio.query.filter_by(nombre="Barrio Las Acacias").first()
        if not barrio:
            barrio = Barrio(
                nombre="Barrio Las Acacias",
                color_primario="#2563eb",
                activo=True,
            )
            db.session.add(barrio)
            db.session.flush()
            print(f"[+] Barrio creado: {barrio.nombre} (id={barrio.id})")
        else:
            print(f"[=] Barrio ya existe: {barrio.nombre}")

        # ── Admin ─────────────────────────────────────────────────────────────
        admin = Usuario.query.filter_by(dni="00000000").first()
        if not admin:
            admin = Usuario(
                barrio_id=barrio.id,
                nombre="Administrador",
                dni="00000000",
                email=None,
                rol="admin",
                activo=True,
            )
            admin.set_password("admin123")
            db.session.add(admin)
            print("[+] Admin creado: DNI=00000000 / admin123")
        else:
            print("[=] Admin ya existe: DNI=00000000")

        # ── Usuario operativo ─────────────────────────────────────────────────
        usuario = Usuario.query.filter_by(dni="12345678").first()
        if not usuario:
            usuario = Usuario(
                barrio_id=barrio.id,
                nombre="Juan Perez",
                dni="12345678",
                email=None,
                rol="usuario",
                activo=True,
            )
            usuario.set_password("usuario123")
            db.session.add(usuario)
            print("[+] Usuario creado: DNI=12345678 / usuario123")
        else:
            print("[=] Usuario ya existe: DNI=12345678")

        db.session.flush()

        # ── Plantillas de ejemplo ─────────────────────────────────────────────
        plantillas_data = [
            {
                "nombre": "Limpieza de calles",
                "descripcion": "Barrido y recoleccion de residuos en calles internas.",
                "frecuencia": "diaria",
                "dia_semana": None,
                "horario": time(7, 0),
            },
            {
                "nombre": "Mantenimiento piscina",
                "descripcion": "Revision de pH, cloro y limpieza del vaso.",
                "frecuencia": "semanal",
                "dia_semana": 1,  # martes
                "horario": time(9, 0),
            },
            {
                "nombre": "Corte de cesped areas comunes",
                "descripcion": "Corte y desbrozado de espacios verdes.",
                "frecuencia": "semanal",
                "dia_semana": 4,  # viernes
                "horario": time(8, 30),
            },
            {
                "nombre": "Control de porteria",
                "descripcion": "Verificacion del libro de ingresos y camaras.",
                "frecuencia": "diaria",
                "dia_semana": None,
                "horario": time(6, 0),
            },
        ]

        for data in plantillas_data:
            existe = PlantillaTarea.query.filter_by(
                barrio_id=barrio.id, nombre=data["nombre"]
            ).first()
            if not existe:
                p = PlantillaTarea(barrio_id=barrio.id, activa=True, **data)
                db.session.add(p)
                print(f"[+] Plantilla creada: {data['nombre']}")
            else:
                print(f"[=] Plantilla ya existe: {data['nombre']}")

        db.session.commit()
        print("\n[OK] Seed completado correctamente.")
        print("\nUsuarios disponibles:")
        print("  Admin   -> DNI: 00000000 / admin123")
        print("  Usuario -> DNI: 12345678 / usuario123")


if __name__ == "__main__":
    seed()
