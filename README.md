# Raccoon Café

Aplicación web full stack de **Raccoon Café**, un café-librería que combina tres líneas de negocio:

1. **Alquiler de 6 salas** — 2 Co-work, 2 Encuentro, 1 Taller y 1 Social.
2. **Cafetería de especialidad** — bebidas calientes y frías, pastelería y packs para eventos.
3. **Librería mixta** — libros para vender y libros para leer en la cafetería.

API en producción: <https://dannurda.alwaysdata.net/api/>

---

## Arquitectura

```
┌──────────────────────┐      HTTPS      ┌──────────────────────┐   PyMySQL   ┌──────────────┐
│  Frontend            │ ──────────────► │  API REST            │ ──────────► │  MySQL       │
│  (carpeta frontend/) │  fetch / JSON   │  Django + DRF        │             │  alwaysdata  │
│  GitHub Pages        │ ◄────────────── │  alwaysdata (uWSGI)  │ ◄────────── │              │
└──────────────────────┘                 └──────────────────────┘             └──────────────┘
```

| Capa | Tecnología | Despliegue |
|---|---|---|
| Base de datos | MySQL (SQLite en local) | alwaysdata |
| Backend | Django 6 + Django REST Framework, WhiteNoise | alwaysdata |
| Interfaz del panel | Plantillas Django + Tailwind CSS (binario standalone, sin Node) | alwaysdata |
| Frontend público | React + Vite (repositorio [RaccoonCafe](https://github.com/durdanigo/RaccoonCafe)) | GitHub Pages |

**Roles:** `Administrador` (gestiona todo) y `Cliente` (consulta y gestiona sus reservas).

---

## Estructura del repositorio

```
raccoon-cafe/
└── backend/
    ├── manage.py
    ├── requirements.txt
    ├── .env.example              # Plantilla de variables (sin secretos)
    ├── bookspace_manager/        # Configuración del proyecto (settings, urls, wsgi)
    ├── cuentas/                  # Login, registro, perfil y roles
    ├── espacios/                 # Salas, tipos de espacio y servicios
    ├── clientes/                 # Personas y empresas
    ├── reservas/                 # Reservas + validación de horario y cruces
    ├── pagos/                    # Pagos sobre reservas
    ├── cafeteria/                # Menú: categorías y productos con stock opcional
    ├── libreria/                 # Libros: para vender / para leer en la cafetería
    ├── contacto/                 # Mensajes del formulario de contacto
    ├── panel/                    # Tablero de indicadores y calendario
    ├── api/                      # API REST (solo lectura, JSON)
    ├── templates/                # Plantillas base y parciales
    ├── static/                   # JavaScript propio
    └── theme/                    # Tailwind (paleta de la marca)
```

> **Nota:** el paquete Python se llama `bookspace_manager` por razones históricas. Renombrarlo rompe `wsgi.py`, las migraciones y la configuración del hosting; la marca visible es *Raccoon Café*.

---

## Instalación local

Requisitos: **Python 3.13** y Git.

```bash
git clone https://github.com/durdanigo/raccoon-cafe.git
cd raccoon-cafe/backend

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # Windows: copy .env.example .env
python manage.py migrate
python manage.py crear_roles
python manage.py seed_raccoon     # menú y libros iniciales
python manage.py createsuperuser

python manage.py tailwind install
python manage.py tailwind build
python manage.py runserver
```

Sin `DB_HOST` en el `.env` se usa SQLite; no hace falta MySQL para desarrollar.

### Variables de entorno

| Variable | Descripción |
|---|---|
| `DJANGO_SECRET_KEY` | Clave de firma. **Obligatoria en producción.** |
| `DJANGO_DEBUG` | `True` solo en desarrollo. Por defecto `False`. |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por coma. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Orígenes HTTPS de confianza. |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | MySQL. Si no hay `DB_HOST`, se usa SQLite. |

---

## API REST

La lectura es **pública**. Las escrituras tienen dos niveles: `POST` de reservas, `login` y `contacto` son abiertos; crear, editar o borrar menú, libros y mensajes exige el **token de un administrador**. Todo responde JSON.

| Ruta | Descripción | Filtros |
|---|---|---|
| `/api/` | Índice de recursos | — |
| `/api/espacios/` | Salas | `?estado=`, `?tipo=`, `?q=` |
| `/api/reservas/` | Reservas | `?estado=`, `?fecha=`, `?cliente=`, `?proximas=true` |
| `/api/clientes/` | Clientes | `?q=` |
| `/api/pagos/` | Pagos | `?metodo=`, `?reserva=` |
| `/api/menu/` | Productos de cafetería | `?categoria=`, `?disponible=true\|false` |
| `/api/categorias-menu/` | Categorías del menú | `?activa=true` |
| `/api/libros/` | Libros | `?tipo=venta\|lectura`, `?disponible=true\|false` |
| `/api/dashboard/` | Indicadores del tablero | — |
| `/api/contacto/` | `POST` público (máx. 5/hora por IP). `GET`/`PATCH`/`DELETE`: solo administradores | `?leido=true|false` |
| `/api/login/` | Valida credenciales (`POST`) y devuelve `token` | — |

`/api/` no usa `BrowsableAPIRenderer` a propósito: con `DEBUG=False` y el manifest de WhiteNoise provoca un error 500.

### Autenticación del panel de administración

`POST /api/login/` con `{"usuario", "clave"}` devuelve, además de los datos de la persona, un `token`. Las rutas protegidas lo exigen en la cabecera:

```
Authorization: Token <token>
```

Solo los usuarios con rol Administrador pueden escribir en `/api/menu/`, `/api/libros/` y `/api/contacto/` (salvo el `POST` público de contacto). Los permisos están en `api/permissions.py`. Las mismas reglas de negocio del sistema web se validan también por API.

### Reglas de negocio

- **Reservas:** hora de fin posterior a la de inicio, dentro del horario de atención, aforo respetado y sin cruces en la misma sala.
- **Productos del menú:** el stock solo se controla si `controla_stock` está activo; `bajo_stock` avisa cuando se llega al mínimo.
- **Libros `lectura`:** precio fijo en 0, sin condición y con estante obligatorio. **Libros `venta`:** precio mayor a 0.

---

## Comandos de gestión

| Comando | Qué hace |
|---|---|
| `crear_roles` | Crea los grupos Administrador y Cliente. |
| `seed_raccoon` | Carga el menú y los libros iniciales (idempotente). |
| `renombrar_salas` | Actualiza las 6 salas a las de Raccoon Café. Simula por defecto; usa `--aplicar` para guardar. |
| `cargar_demo` | Genera clientes y reservas de ejemplo para el tablero. |

---

## Despliegue en alwaysdata

```bash
cd ~/www/bookspace_manager
source venv/bin/activate
python manage.py migrate        # incluye contacto y authtoken
python manage.py tailwind build
python manage.py collectstatic --noinput
```

Después, reinicia el sitio desde el panel de alwaysdata (*Web → Sites → Restart*). Define las variables de entorno en el mismo panel; nunca las escribas en el código.

---

## Estado del proyecto

- [x] Backend Django con API REST desplegado.
- [x] Módulos de salas, cafetería y librería con CRUD web.
- [ ] Frontend público (Home, catálogo, contacto, panel de admin, IA) en `frontend/`.
- [ ] Publicación del frontend en GitHub Pages.
