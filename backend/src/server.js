/**
 * ===============================================================
 * server.js - Punto de entrada de la API de Raccoon Cafe
 * ---------------------------------------------------------------
 * Version 1.0 (scaffolding): levanta Express, conecta con MongoDB
 * Atlas, habilita CORS para el frontend publicado en GitHub Pages y
 * expone el endpoint de diagnostico GET /api/health.
 *
 * Los routers de cada modulo (auth, rooms, products, bookings,
 * contact) se montaran sobre esta misma base en las versiones
 * siguientes, en la seccion marcada mas abajo.
 * ===============================================================
 */

require('dotenv').config();

const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');

const { conectarDB, describirEstado } = require('./config/db');

const app = express();
const PUERTO = process.env.PORT || 5000;

// ---------------------------------------------------------------
// 1. CORS
// ---------------------------------------------------------------
// El frontend se sirve desde GitHub Pages (otro dominio), asi que el
// navegador exige cabeceras CORS explicitas. Se permite el origen
// declarado en CLIENT_URL mas los origenes locales de desarrollo.
const origenesPermitidos = [
  process.env.CLIENT_URL,
  'http://localhost:5500',
  'http://127.0.0.1:5500',
  'http://localhost:3000',
].filter(Boolean);

const opcionesCors = {
  origin(origen, callback) {
    // Sin origen = peticiones desde curl, Postman o healthchecks.
    if (!origen) return callback(null, true);

    // Se acepta cualquier subdominio *.github.io para no tener que
    // reconfigurar la variable al cambiar de cuenta o repositorio.
    const esGitHubPages = /^https:\/\/[\w-]+\.github\.io$/.test(origen);

    if (origenesPermitidos.includes(origen) || esGitHubPages) {
      return callback(null, true);
    }
    return callback(new Error(`Origen no permitido por CORS: ${origen}`));
  },
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
};

app.use(cors(opcionesCors));

// ---------------------------------------------------------------
// 2. Parseo del cuerpo de las peticiones
// ---------------------------------------------------------------
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));

// ---------------------------------------------------------------
// 3. Log minimo de peticiones (sin dependencias externas)
// ---------------------------------------------------------------
app.use((req, _res, next) => {
  console.log(`[API] ${new Date().toISOString()} ${req.method} ${req.originalUrl}`);
  next();
});

// ---------------------------------------------------------------
// 4. Endpoint de diagnostico
// ---------------------------------------------------------------
/**
 * GET /api/health
 * Devuelve el estado del servicio y de la conexion con MongoDB.
 * El frontend lo usa para pintar el indicador visual de conexion.
 */
app.get('/api/health', (_req, res) => {
  const estadoDB = describirEstado(mongoose.connection.readyState);

  res.status(200).json({
    ok: estadoDB === 'conectado',
    servicio: 'Raccoon Cafe API',
    version: '1.0.0',
    baseDatos: estadoDB,
    entorno: process.env.NODE_ENV || 'development',
    marcaTiempo: new Date().toISOString(),
  });
});

/**
 * GET /api
 * Indice de la API: lista los recursos disponibles.
 */
app.get('/api', (_req, res) => {
  res.status(200).json({
    servicio: 'Raccoon Cafe API',
    version: '1.0.0',
    recursos: {
      health: '/api/health',
    },
  });
});

// ---------------------------------------------------------------
// 5. Routers de modulos (se incorporan en las proximas versiones)
// ---------------------------------------------------------------
// app.use('/api/auth', require('./routes/auth.routes'));
// app.use('/api/rooms', require('./routes/room.routes'));
// app.use('/api/products', require('./routes/product.routes'));
// app.use('/api/bookings', require('./routes/booking.routes'));
// app.use('/api/contact', require('./routes/contact.routes'));

// ---------------------------------------------------------------
// 6. Manejo de rutas no encontradas
// ---------------------------------------------------------------
app.use((req, res) => {
  res.status(404).json({
    ok: false,
    mensaje: `Ruta no encontrada: ${req.method} ${req.originalUrl}`,
  });
});

// ---------------------------------------------------------------
// 7. Manejador global de errores
// ---------------------------------------------------------------
// eslint-disable-next-line no-unused-vars
app.use((error, _req, res, _next) => {
  console.error(`[API] Error no controlado: ${error.message}`);

  const codigo = error.status || 500;
  res.status(codigo).json({
    ok: false,
    mensaje: codigo === 500 ? 'Error interno del servidor' : error.message,
  });
});

// ---------------------------------------------------------------
// 8. Arranque
// ---------------------------------------------------------------
async function iniciarServidor() {
  await conectarDB();

  app.listen(PUERTO, () => {
    console.log('===============================================');
    console.log(`  Raccoon Cafe API escuchando en el puerto ${PUERTO}`);
    console.log(`  Health check: http://localhost:${PUERTO}/api/health`);
    console.log('===============================================');
  });
}

iniciarServidor();

module.exports = app;
