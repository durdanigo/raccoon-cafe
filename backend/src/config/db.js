/**
 * ===============================================================
 * db.js - Conexion a MongoDB Atlas mediante Mongoose
 * ---------------------------------------------------------------
 * Responsabilidades:
 *   1. Validar que exista MONGO_URI antes de intentar conectar.
 *   2. Abrir la conexion con timeouts explicitos (Atlas M0 puede
 *      tardar en despertar el cluster).
 *   3. Registrar los eventos del ciclo de vida de la conexion.
 *   4. Cerrar la conexion de forma ordenada ante SIGINT / SIGTERM,
 *      que es la senal que envia Render al reiniciar el servicio.
 * ===============================================================
 */

const mongoose = require('mongoose');

/**
 * Traduce el codigo numerico de readyState a texto legible.
 * @param {number} estado valor de mongoose.connection.readyState
 * @returns {string}
 */
function describirEstado(estado) {
  const estados = {
    0: 'desconectado',
    1: 'conectado',
    2: 'conectando',
    3: 'desconectando',
  };
  return estados[estado] || 'desconocido';
}

/**
 * Abre la conexion con MongoDB Atlas.
 * Si la conexion falla, termina el proceso: un backend sin base de
 * datos no puede responder nada util y es preferible que Render lo
 * reinicie a que quede sirviendo errores 500.
 *
 * @returns {Promise<typeof mongoose>}
 */
async function conectarDB() {
  const uri = process.env.MONGO_URI;

  if (!uri) {
    console.error('[DB] Falta la variable MONGO_URI. Revisa tu archivo .env');
    process.exit(1);
  }

  // Evita avisos por consultas con campos no declarados en el esquema.
  mongoose.set('strictQuery', true);

  try {
    const conexion = await mongoose.connect(uri, {
      serverSelectionTimeoutMS: 15000, // 15 s para encontrar un nodo del cluster
      socketTimeoutMS: 45000, // 45 s maximo por operacion
      maxPoolSize: 10, // suficiente para el free tier
    });

    console.log(`[DB] Conectado a MongoDB Atlas -> host: ${conexion.connection.host}`);
    console.log(`[DB] Base de datos activa  -> ${conexion.connection.name}`);
    return conexion;
  } catch (error) {
    console.error('[DB] No se pudo conectar a MongoDB Atlas.');
    console.error(`[DB] Detalle: ${error.message}`);
    console.error('[DB] Verifica: 1) usuario y password, 2) la IP permitida en Network Access, 3) el nombre de la base.');
    process.exit(1);
  }
}

// ---------------------------------------------------------------
// Eventos del ciclo de vida de la conexion
// ---------------------------------------------------------------
mongoose.connection.on('error', (error) => {
  console.error(`[DB] Error en la conexion: ${error.message}`);
});

mongoose.connection.on('disconnected', () => {
  console.warn('[DB] Conexion perdida con MongoDB Atlas.');
});

mongoose.connection.on('reconnected', () => {
  console.log('[DB] Conexion restablecida con MongoDB Atlas.');
});

// ---------------------------------------------------------------
// Cierre ordenado: Render envia SIGTERM, Ctrl+C envia SIGINT.
// ---------------------------------------------------------------
['SIGINT', 'SIGTERM'].forEach((senal) => {
  process.on(senal, async () => {
    await mongoose.connection.close();
    console.log(`[DB] Conexion cerrada por ${senal}.`);
    process.exit(0);
  });
});

module.exports = { conectarDB, describirEstado };
