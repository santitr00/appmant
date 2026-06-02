# Estado del proyecto — Gestión de Mantenimiento de Barrios Privados

> Última actualización: 2026-03-12 (fase 2)

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Flask 3.0 + Blueprints + SQLAlchemy + Flask-Migrate + openpyxl + xhtml2pdf |
| Autenticación | Flask-Login + Flask-WTF (CSRF) |
| Base de datos | MySQL (PyMySQL) — `app_tareas` en localhost:3306 |
| Servidor (prod) | Waitress (puerto 8080) |
| Servidor (dev) | Flask debug (puerto 5000) |
| Frontend | Jinja2 + Bootstrap 5 + Bootstrap Icons + FullCalendar.js 6 |

---

## Estructura de archivos

```
d:\ProyectoMantenimiento\
│
├── .env                          # Variables de entorno (DB, SECRET_KEY)
├── config.py                     # Configuración por entorno (dev/prod)
├── requirements.txt              # Dependencias Python
├── run.py                        # Punto de entrada (dev: Flask / prod: Waitress)
├── seed.py                       # Carga datos iniciales para testing
│
├── app\
│   ├── __init__.py               # create_app() — factory con todos los blueprints
│   ├── models.py                 # 6 modelos SQLAlchemy
│   │
│   ├── auth\                     # Blueprint /auth
│   │   ├── decorators.py         # solo_admin, rol_requerido
│   │   ├── forms.py              # LoginForm (DNI + contraseña)
│   │   └── routes.py             # GET/POST /auth/login | GET /auth/logout
│   │
│   ├── plantillas\               # Blueprint /plantillas (solo admin)
│   │   ├── forms.py              # PlantillaForm
│   │   └── routes.py             # CRUD: index / nueva / editar / toggle_activa
│   │
│   ├── tareas\                   # Blueprint /tareas
│   │   ├── generador.py          # generar_tareas_para_fecha() / semana()
│   │   ├── forms.py              # TareaExcepcionalForm, JustificacionForm
│   │   └── routes.py             # generar / excepcional nueva / AJAX estados
│   │
│   ├── calendario\               # Blueprint /calendario
│   │   └── routes.py             # GET /calendario/dia?fecha=YYYY-MM-DD
│   │
│   ├── usuarios\                 # Blueprint /usuarios (solo admin)
│   │   ├── forms.py              # UsuarioForm
│   │   └── routes.py             # CRUD: index / nuevo / editar / toggle_activo
│   │
│   └── templates\
│       ├── base.html             # Layout base (navbar, flash messages)
│       ├── auth\
│       │   └── login.html        # Pantalla de login (DNI + contraseña)
│       ├── plantillas\
│       │   ├── index.html        # Listado de plantillas con toggle activa
│       │   └── form.html         # Alta / edición de plantilla
│       ├── tareas\
│       │   └── excepcional_form.html  # Nueva tarea excepcional
│       ├── usuarios\
│       │   ├── index.html        # Listado de usuarios del barrio
│       │   └── form.html         # Alta / edición de usuario
│       └── calendario\
│           └── dia.html          # Vista diaria: cards de tareas + AJAX + modal justificación
│
└── migrations\
    └── versions\
        ├── 423107f54206_initial.py                      # Migración inicial (tablas)
        └── 5aa35caab574_dni_login_asignado_a_...py      # DNI, roles admin/usuario, asignado_a texto
```

---

## Módulos implementados

### 1. Setup y configuración
- `config.py`: entornos dev/prod, URI de MySQL desde variables de entorno
- `run.py`: dev con Flask debug, prod con Waitress en puerto 8080
- `app/__init__.py`: factory `create_app()` con todos los blueprints registrados

### 2. Modelos de datos (`app/models.py`)

| Tabla | Descripción |
|---|---|
| `barrios` | Barrio privado (nombre, logo, color, activo) |
| `usuarios` | Usuario del sistema (DNI, nombre, email opcional, rol, barrio) |
| `plantillas_tarea` | Tareas rutinarias con frecuencia diaria o semanal |
| `tareas_programadas` | Instancias generadas de plantillas para una fecha |
| `tareas_excepcionales` | Tareas ad-hoc creadas manualmente |
| `justificaciones` | Motivo cuando una tarea programada no se realizó |

### 3. Autenticación (`/auth`)
- Login por **DNI + contraseña** (sin email)
- Logout con limpieza de sesión
- Decoradores: `solo_admin` (403 si no es admin), `rol_requerido(*roles)`
- Multi-tenant: todo filtrado por `current_user.barrio_id`

### 4. CRUD Plantillas (`/plantillas`) — solo admin
- Listar plantillas del barrio con estado activa/inactiva
- Crear nueva plantilla (nombre, descripción, frecuencia, día semana, horario)
- Editar plantilla existente
- Toggle activar/desactivar (sin borrar)

### 5. Generación de tareas (`app/tareas/generador.py`)
- `generar_tareas_para_fecha(barrio_id, fecha)`: genera tareas del día sin duplicados
- `generar_tareas_para_semana(barrio_id, fecha_inicio)`: genera para 7 días
- Se ejecuta **automáticamente** al cargar el calendario
- Se puede ejecutar manualmente con el botón "Regenerar tareas del día"

### 6. Calendario diario (`/calendario/dia`)
- Vista por fecha (navegable con Anterior/Siguiente)
- Muestra tareas rutinarias y excepcionales separadas
- Marcar como **completada / no_realizada / pendiente** vía AJAX (sin recarga)
- Agregar **justificación** para tareas no realizadas (modal)
- Botón rápido para crear tarea excepcional en la fecha visualizada
- Fecha en español sin dependencia de locale del sistema

### 7. Gestión de usuarios (`/usuarios`) — solo admin
- Listar usuarios del barrio con rol y estado
- Crear usuario nuevo (DNI, nombre, email opcional, contraseña, rol)
- Editar usuario (contraseña: vacío = no cambia)
- Activar/desactivar cuenta (sin borrar, protegido para no autodesactivarse)

---

## Estado de la base de datos

| Tabla | Registros actuales |
|---|---|
| barrios | 1 (Barrio Las Acacias) |
| usuarios | 4 (2 nuevos con DNI + 2 legacy con dni tmp_1/tmp_2) |
| plantillas_tarea | 4 |
| tareas_programadas | 18 (generadas automáticamente) |
| tareas_excepcionales | 0 |
| justificaciones | 0 |

### Usuarios de acceso

| DNI | Contraseña | Rol | Nombre |
|---|---|---|---|
| `00000000` | `admin123` | admin | Administrador |
| `12345678` | `usuario123` | usuario | Juan Perez |
| `tmp_1` | `admin123` | admin | Admin Intendente (legacy) |
| `tmp_2` | `encargado123` | usuario | Juan Encargado (legacy) |

> Los usuarios legacy (`tmp_1`, `tmp_2`) se pueden actualizar o eliminar desde `/usuarios/`.

---

## Comandos de operación

```bash
# Levantar servidor de desarrollo
py -3.12 run.py

# Crear y aplicar una nueva migración
py -3.12 -m flask db migrate -m "descripcion"
py -3.12 -m flask db upgrade

# Cargar datos iniciales (idempotente)
py -3.12 seed.py

# Servidor de producción (modo automático)
set FLASK_ENV=production && py -3.12 run.py
```

> **Importante:** Usar siempre `py -3.12` (Python 3.12 con paquetes instalados).
> El comando `python` apunta a Python 3.14 (Microsoft Store) que no tiene las dependencias.

---

## Pendiente / Próxima fase

### Funcionalidades nuevas
- [x] **Calendario mensual** (FullCalendar.js, `/calendario/mes`)
- [x] **Tareas excepcionales: editar y eliminar** (`/tareas/excepcional/<id>/editar|eliminar`)
- [x] **Justificación mejorada**: vinculación opcional con tarea excepcional del día
- [x] **Exportación Excel**: reporte diario y mensual (`/reportes/excel/dia|mes`)
- [x] **Exportación PDF**: reporte diario y mensual con xhtml2pdf (`/reportes/pdf/dia|mes`)
- [x] **Multi-tenant con 3 barrios**: `seed_barrios.py` crea Vida Barrio Cerrado, Vida Club de Campo, Vida Lagoon
- [ ] **Asignación inline desde el calendario**: editar "asignado a" sin abrir otro formulario
- [ ] **Vista semanal**: resumen de los 7 días con conteo de estados
- [ ] **Estadísticas**: porcentaje de cumplimiento por período
- [ ] **Gestión de barrios desde UI**: panel para crear/administrar barrios

### Mejoras técnicas
- [ ] **Paginación** en el calendario para días con muchas tareas
- [ ] **Búsqueda / filtro** en el listado de plantillas y usuarios
- [ ] **Confirmación antes de toggle** (desactivar usuario/plantilla)
- [ ] **Tests unitarios** para el generador de tareas y los modelos
- [ ] **Logging** de errores y acciones críticas
- [ ] **Variables de entorno en producción**: separar `.env.production`
