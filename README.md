# Raccoon Café — API REST (Backend)

API REST de **Raccoon Café**, un café-librería que combina tres líneas de negocio en un mismo espacio:

1. **Alquiler de 6 salas modulares** — 2 de co-work, 2 de encuentro, 1 taller y 1 social.
2. **Cafetería de especialidad** — bebidas calientes y frías, pastelería y packs para eventos.
3. **Librería mixta** — libros nuevos, de segunda mano (clasificados por condición) y de lectura interna.

Este repositorio contiene **únicamente el backend**. El frontend cliente vive en su propio repositorio y consume esta API por HTTPS.

---

## Arquitectura

```
┌──────────────────────┐      HTTPS      ┌──────────────────────┐    mongodb+srv    ┌──────────────────┐
│  Frontend cliente    │ ──────────────► │  API REST            │ ────────────────► │  MongoDB Atlas   │
│  (repositorio aparte)│  fetch / JSON   │  Node.js + Express   │     Mongoose      │  (M0 Free Tier)  │
│  GitHub Pages        │ ◄────────────── │  JWT + RBAC          │ ◄──────────────── │                  │
└──────────────────────┘                 │  Render              │                   └──────────────────┘
                                         └──────────────────────┘
```

| Capa | Tecnología | Despliegue |
|---|---|---|
| Base de datos | MongoDB Atlas + Mongoose | MongoDB Atlas (M0) |
| API | Node.js + Express, JWT, RBAC, bcryptjs | Render (Web Service) |

**Roles del sistema (RBAC):** `cliente`, `empleado`, `admin`.

---

## Estructura del repositorio

```
raccoon-cafe-backend/
└── backend/
    ├── src/
    │   ├── config/
    │   │   └── db.js            # Conexión a MongoDB Atlas
    │   ├── models/
    │   │   ├── User.js          # Usuarios + hash bcrypt + roles
    │   │   ├── Room.js          # Las 6 salas físicas
    │   │   ├── Product.js       # Cafetería y librería unificadas
    │   │   ├── Booking.js       # Reservas, consumo y desglose
    │   │   └── Contact.js       # Mensajes del formulario público
    │   ├── routes/              # Routers por módulo (v2.0)
    │   ├── seeds/
    │   │   └── seed.js          # Poblado inicial de la base
    │   └── server.js            # Express + CORS + /api/health
    ├── .env.example             # Plantilla de variables (sin secretos)
    └── package.json
```

> Si mueves el contenido de `backend/` a la raíz del repositorio, omite el `cd backend` de los comandos siguientes y pon `Root Directory` vacío en Render.

---

## Requisitos previos

- **Node.js 18 o superior** y npm.
- Una cuenta de **MongoDB Atlas** con un clúster M0 creado.
- Git.

---

## Instalación y ejecución local

### 1. Clonar e instalar

```bash
git clone https://github.com/<tu-usuario>/raccoon-cafe-backend.git
cd raccoon-cafe-backend/backend
npm install
```

### 2. Crear el archivo de variables

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

### 3. Completar las variables

| Variable | Descripción | Ejemplo |
|---|---|---|
| `PORT` | Puerto del servidor Express. En Render la plataforma inyecta el suyo, así que allí no hace falta. | `5000` |
| `MONGO_URI` | Cadena de conexión de MongoDB Atlas (ver abajo). | `mongodb+srv://usuario:clave@cluster0.ab1cd.mongodb.net/raccoon_cafe?retryWrites=true&w=majority` |
| `JWT_SECRET` | Clave secreta para firmar los tokens JWT. | Cadena aleatoria larga |
| `CLIENT_URL` | Origen del frontend autorizado por CORS. | `http://localhost:5500` o `https://<tu-usuario>.github.io` |

#### Cómo obtener `MONGO_URI`

1. En [cloud.mongodb.com](https://cloud.mongodb.com), abre tu clúster y pulsa **Connect**.
2. Elige **Drivers** → Driver **Node.js**, Version **5.5 or later**.
3. Copia la cadena que aparece:

```
mongodb+srv://miusuario:<db_password>@cluster0.ab1cd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

4. Haz dos cambios antes de pegarla en `.env`:
   - Sustituye `<db_password>` por la contraseña del **usuario de base de datos** (la creada en *Database Access*, no la de tu cuenta de Atlas).
   - Inserta el nombre de la base entre el `/` y el `?`: `raccoon_cafe`.

```bash
MONGO_URI=mongodb+srv://miusuario:MiClave123@cluster0.ab1cd.mongodb.net/raccoon_cafe?retryWrites=true&w=majority
```

**Errores frecuentes**

| Síntoma | Causa | Solución |
|---|---|---|
| El seed corre pero la base `raccoon_cafe` sigue vacía | Falta `/raccoon_cafe` en la URI; Mongoose escribe en `test` | Agrega el nombre de la base antes del `?` |
| `Authentication failed` | La contraseña contiene `@ : / ? # [ ] %` sin codificar | Cámbiala por letras y números, o codifícala: `node -e "console.log(encodeURIComponent('TuC@ve'))"` |
| Timeout al conectar | La IP no está autorizada | Atlas → **Network Access** → *Allow access from anywhere* (`0.0.0.0/0`) |
| `MONGO_URI` indefinida | El `.env` está fuera de `backend/` | Debe estar junto a `package.json` |

Para generar un `JWT_SECRET` seguro:

```bash
node -e "console.log(require('crypto').randomBytes(48).toString('hex'))"
```

Para comprobar la cadena antes de arrancar el servidor:

```bash
node -e "require('dotenv').config();require('mongoose').connect(process.env.MONGO_URI).then(c=>{console.log('OK ->',c.connection.name);process.exit(0)}).catch(e=>{console.error('FALLO:',e.message);process.exit(1)})"
```

Debe imprimir `OK -> raccoon_cafe`.

> `.env` está listado en `.gitignore` y **nunca** debe subirse. `.env.example` solo contiene los nombres de las variables.

### 4. Poblar la base de datos

```bash
npm run seed
```

**Borra** las colecciones `salas`, `productos`, `usuarios` y `contactos` y vuelve a insertar:

- Las 6 salas físicas con su aforo, equipamiento y precio por hora.
- 16 ítems de cafetería (bebidas calientes, frías, pastelería y packs).
- 8 libros (3 nuevos, 3 de segunda mano, 2 de lectura interna).
- 3 usuarios de demostración, uno por rol.

| Rol | Correo | Contraseña |
|---|---|---|
| `admin` | `admin@raccooncafe.com` | `Admin2026!` |
| `empleado` | `empleado@raccooncafe.com` | `Empleado2026!` |
| `cliente` | `cliente@raccooncafe.com` | `Cliente2026!` |

> Credenciales de demostración. Cámbialas antes de cualquier uso real.

### 5. Levantar la API

```bash
npm start        # modo normal
npm run dev      # con recarga automática (node --watch)
```

Comprueba que responde:

```bash
curl http://localhost:5000/api/health
```

```json
{
  "ok": true,
  "servicio": "Raccoon Cafe API",
  "version": "1.0.0",
  "baseDatos": "conectado",
  "entorno": "development",
  "marcaTiempo": "2026-10-23T14:20:00.000Z"
}
```

---

## Scripts disponibles

| Script | Acción |
|---|---|
| `npm start` | Levanta la API en modo normal. |
| `npm run dev` | Levanta la API con recarga automática al guardar. |
| `npm run seed` | Limpia y vuelve a poblar la base de datos. |

---

## Endpoints

### Versión 1.0 (disponibles)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api` | Índice de la API. |
| `GET` | `/api/health` | Estado del servicio y de la conexión con MongoDB. |

### Versión 2.0 (punto de montaje ya reservado en `src/server.js`)

| Prefijo | Módulo |
|---|---|
| `/api/auth` | Registro, login y perfil |
| `/api/rooms` | Salas |
| `/api/products` | Cafetería y librería |
| `/api/bookings` | Reservas |
| `/api/contact` | Mensajes de contacto |

---

## Modelo de datos

| Modelo | Colección | Notas |
|---|---|---|
| `User` | `usuarios` | Contraseña hasheada con bcrypt en un hook `pre('save')`; `select: false` para que no salga en las consultas. Roles: `cliente`, `empleado`, `admin`. |
| `Room` | `salas` | Tipos: `cowork`, `encuentro`, `taller`, `social`. Aforo como rango mínimo/máximo y precio por hora. |
| `Product` | `productos` | Unifica cafetería y librería mediante `categoria` + `subcategoria`. Valida que un libro usado declare condición y que uno de lectura interna tenga estante y precio 0. |
| `Booking` | `reservas` | Fecha + bloque horario + asistentes + consumo. Recalcula el total en el servidor: sala + consumo + descorche ($15.00 fijo). Estados: `pendiente` → `confirmada` → `en_curso` → `finalizada`, más `cancelada` y `no_show`. |
| `Contact` | `contactos` | Mensajes del formulario público. Estados: `nuevo` → `leido` → `respondido` → `archivado`. |

### Reglas de negocio aplicadas en los esquemas

- **Alimentos internos** (`tipoAlimentos: 'interno'`): el consumo de cafetería se carga en `consumo[]`, guardando una copia del nombre y del precio al momento de reservar, para que un cambio posterior de precio no altere reservas pasadas.
- **Alimentos externos** (`tipoAlimentos: 'externo'`): se aplica la tarifa fija de descorche de **$15.00** y se rechaza cualquier línea de consumo de cafetería.
- **Libros de segunda mano**: deben declarar su condición (`excelente`, `bueno`, `aceptable`).
- **Libros de lectura interna**: el precio se fuerza a 0 y el estante es obligatorio.
- **Bloque horario**: `horaFin` debe ser posterior a `horaInicio`.
- **Totales**: siempre se recalculan en el servidor; nunca se acepta el total que envía el cliente.

---

## Despliegue en Render

1. **New → Web Service** y conecta este repositorio.
2. **Root Directory:** `backend` *(vacío si moviste el contenido a la raíz)*
3. **Build Command:** `npm install`
4. **Start Command:** `npm start`
5. En **Environment** añade `MONGO_URI`, `JWT_SECRET` y `CLIENT_URL`.
   `PORT` no hace falta: Render lo inyecta.
6. En MongoDB Atlas, **Network Access** debe permitir `0.0.0.0/0` para que Render pueda conectarse.

Tras el despliegue, verifica:

```bash
curl https://<tu-servicio>.onrender.com/api/health
```

> En el plan gratuito de Render el servicio se duerme tras unos minutos sin tráfico. La primera petición después del reposo puede tardar ~30 segundos; por eso `db.js` usa un `serverSelectionTimeoutMS` de 15 s.

---

## CORS

El frontend se sirve desde otro dominio, así que el navegador exige cabeceras CORS explícitas. `src/server.js` autoriza:

- El origen declarado en `CLIENT_URL`.
- `http://localhost:5500`, `http://127.0.0.1:5500` y `http://localhost:3000` para desarrollo.
- Cualquier subdominio `https://*.github.io`, para no tener que reconfigurar la variable al cambiar de cuenta o de repositorio.

Cualquier otro origen recibe la petición rechazada sin cabecera `Access-Control-Allow-Origin`.

---

## Seguridad

- Las contraseñas se almacenan **solo como hash** (bcryptjs, 10 rondas de sal) y `toJSON()` las elimina de cualquier respuesta.
- `.env` está en `.gitignore`; `.env.example` no contiene ningún valor real.
- CORS restringido a una lista de orígenes conocidos.
- El total de una reserva se calcula en el servidor.
- Cierre ordenado de la conexión ante `SIGINT` / `SIGTERM`, que es la señal que envía Render al reiniciar el servicio.

---

## Hoja de ruta

| Versión | Alcance |
|---|---|
| **1.0** ✅ | Scaffolding, modelos, conexión a Atlas, seed y `GET /api/health`. |
| 2.0 | Routers y controladores CRUD, autenticación JWT y middleware de roles. |
| 3.0 | Flujo completo de reservas: disponibilidad, solapamiento, consumo y check-in. |
| 4.0 | Dashboard administrativo en React. |

### Decisiones pendientes antes de la v2.0

- **Buffer de limpieza entre reservas** — necesario para el algoritmo de detección de solapamiento.
- **Expiración de reservas impagas** — cuánto tiempo permanece una reserva en `pendiente` antes de liberarse.
- **Duración del token de sesión.**
- **Si el consumo puede modificarse con la reserva ya en curso.**

---

## Autoría

Proyecto académico desarrollado por **Silvia Milena Pazmiño Montes** — Ingeniería en Computación, ESPOL (FIEC), Guayaquil, Ecuador.

Licencia MIT.
