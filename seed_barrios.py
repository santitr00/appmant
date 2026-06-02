"""
Seed de producción: crea los 3 barrios con sus 9 usuarios.

Barrios:
  1. Vida Barrio Cerrado
  2. Vida Club de Campo
  3. Vida Lagoon

Cada barrio tiene:
  - 1 usuario admin (intendente)
  - 2 usuarios (encargados)

Uso:
    py -3.12 seed_barrios.py

El script es idempotente: si un barrio o usuario ya existe, lo omite.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import Barrio, Usuario

app = create_app(os.environ.get("FLASK_ENV", "development"))

BARRIOS_DATA = [
    {
        "nombre": "Vida Barrio Cerrado",
        "color_primario": "#1e3a5f",
        "usuarios": [
            {
                "nombre": "Intendente VBC",
                "dni": "VBC-ADMIN",
                "password": "vbc123",
                "rol": "admin",
            },
            {
                "nombre": "Encargado VBC 1",
                "dni": "VBC-ENC1",
                "password": "vbc123",
                "rol": "usuario",
            },
            {
                "nombre": "Encargado VBC 2",
                "dni": "VBC-ENC2",
                "password": "vbc123",
                "rol": "usuario",
            },
        ],
    },
    {
        "nombre": "Vida Club de Campo",
        "color_primario": "#14532d",
        "usuarios": [
            {
                "nombre": "Intendente VCC",
                "dni": "VCC-ADMIN",
                "password": "vcc123",
                "rol": "admin",
            },
            {
                "nombre": "Encargado VCC 1",
                "dni": "VCC-ENC1",
                "password": "vcc123",
                "rol": "usuario",
            },
            {
                "nombre": "Encargado VCC 2",
                "dni": "VCC-ENC2",
                "password": "vcc123",
                "rol": "usuario",
            },
        ],
    },
    {
        "nombre": "Vida Lagoon",
        "color_primario": "#0c4a6e",
        "usuarios": [
            {
                "nombre": "Intendente VL",
                "dni": "VL-ADMIN",
                "password": "vl123",
                "rol": "admin",
            },
            {
                "nombre": "Encargado VL 1",
                "dni": "VL-ENC1",
                "password": "vl123",
                "rol": "usuario",
            },
            {
                "nombre": "Encargado VL 2",
                "dni": "VL-ENC2",
                "password": "vl123",
                "rol": "usuario",
            },
        ],
    },
]


def seed():
    with app.app_context():
        print("=" * 60)
        print("Seed de barrios — sistema multi-tenant")
        print("=" * 60)

        for bdata in BARRIOS_DATA:
            # Buscar o crear barrio
            barrio = Barrio.query.filter_by(nombre=bdata["nombre"]).first()
            if not barrio:
                barrio = Barrio(
                    nombre=bdata["nombre"],
                    color_primario=bdata["color_primario"],
                    activo=True,
                )
                db.session.add(barrio)
                db.session.flush()
                print(f"\n[+] Barrio creado: {barrio.nombre} (id={barrio.id})")
            else:
                print(f"\n[=] Barrio ya existe: {barrio.nombre} (id={barrio.id})")

            # Usuarios del barrio
            for udata in bdata["usuarios"]:
                u = Usuario.query.filter_by(dni=udata["dni"]).first()
                if not u:
                    u = Usuario(
                        barrio_id=barrio.id,
                        nombre=udata["nombre"],
                        dni=udata["dni"],
                        email=None,
                        rol=udata["rol"],
                        activo=True,
                    )
                    u.set_password(udata["password"])
                    db.session.add(u)
                    print(f"    [+] {udata['rol']:8s}  DNI: {udata['dni']:12s}  pass: {udata['password']}")
                else:
                    print(f"    [=] Ya existe: DNI={udata['dni']}")

        db.session.commit()

        print("\n" + "=" * 60)
        print("[OK] Seed completado.")
        print("=" * 60)
        print("\nCredenciales de acceso:")
        print(f"{'Barrio':<25} {'DNI':<14} {'Password':<10} {'Rol'}")
        print("-" * 65)
        for bdata in BARRIOS_DATA:
            for udata in bdata["usuarios"]:
                print(
                    f"{bdata['nombre']:<25} {udata['dni']:<14} "
                    f"{udata['password']:<10} {udata['rol']}"
                )


if __name__ == "__main__":
    seed()
