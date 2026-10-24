/**
 * ===============================================================
 * Booking.js - Reservas de salas
 * ---------------------------------------------------------------
 * Una reserva une: usuario + sala + bloque horario + consumo.
 *
 * Reglas de alimentos (Fase 0):
 *   - tipoAlimentos = 'interno' : el cliente consume items o packs
 *     de la cafeteria, que se cargan en el arreglo consumo[].
 *   - tipoAlimentos = 'externo' : el cliente trae su propia comida y
 *     paga la tarifa fija de descorche / limpieza ($15.00).
 *   - tipoAlimentos = 'ninguno' : solo alquiler de sala.
 *
 * Estados de la reserva:
 *   pendiente -> confirmada -> en_curso -> finalizada
 *   (ademas: cancelada, no_show)
 *
 * El total se recalcula en el servidor antes de cada guardado, para
 * que el precio nunca dependa de lo que envie el cliente.
 * ===============================================================
 */

const mongoose = require('mongoose');

const ESTADOS = ['pendiente', 'confirmada', 'en_curso', 'finalizada', 'cancelada', 'no_show'];
const ESTADOS_PAGO = ['pendiente', 'abonada', 'pagada'];
const TIPOS_ALIMENTOS = ['ninguno', 'interno', 'externo'];

// Tarifa fija de descorche / servicio de limpieza por alimento externo.
const TARIFA_DESCORCHE = 15.0;

/**
 * Subdocumento de consumo: una linea del pedido de cafeteria.
 * Se guarda una copia del nombre y del precio al momento de reservar,
 * para que un cambio posterior de precio no altere reservas pasadas.
 */
const esquemaConsumo = new mongoose.Schema(
  {
    producto: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Product',
      required: [true, 'El producto del consumo es obligatorio'],
    },
    nombre: { type: String, required: true, trim: true },
    precioUnitario: { type: Number, required: true, min: 0 },
    cantidad: {
      type: Number,
      required: true,
      min: [1, 'La cantidad minima es 1'],
      default: 1,
    },
  },
  { _id: false }
);

const esquemaReserva = new mongoose.Schema(
  {
    usuario: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: [true, 'La reserva debe pertenecer a un usuario'],
      index: true,
    },

    sala: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Room',
      required: [true, 'La reserva debe indicar una sala'],
      index: true,
    },

    // Fecha del dia reservado (sin hora). Las horas van aparte para
    // simplificar las consultas de solapamiento por dia + sala.
    fecha: {
      type: Date,
      required: [true, 'La fecha de la reserva es obligatoria'],
      index: true,
    },

    horaInicio: {
      type: String,
      required: [true, 'La hora de inicio es obligatoria'],
      match: [/^([01]\d|2[0-3]):[0-5]\d$/, 'La hora de inicio debe tener formato HH:MM'],
    },

    horaFin: {
      type: String,
      required: [true, 'La hora de fin es obligatoria'],
      match: [/^([01]\d|2[0-3]):[0-5]\d$/, 'La hora de fin debe tener formato HH:MM'],
    },

    asistentes: {
      type: Number,
      required: [true, 'El numero de asistentes es obligatorio'],
      min: [1, 'Debe haber al menos 1 asistente'],
    },

    tipoAlimentos: {
      type: String,
      enum: { values: TIPOS_ALIMENTOS, message: 'Tipo de alimentos no valido: {VALUE}' },
      default: 'ninguno',
    },

    consumo: {
      type: [esquemaConsumo],
      default: [],
    },

    // ---------- Desglose economico ----------
    subtotalSala: { type: Number, default: 0, min: 0 },
    subtotalConsumo: { type: Number, default: 0, min: 0 },
    tarifaDescorche: { type: Number, default: 0, min: 0 },
    total: { type: Number, default: 0, min: 0 },

    estado: {
      type: String,
      enum: { values: ESTADOS, message: 'Estado no valido: {VALUE}' },
      default: 'pendiente',
      index: true,
    },

    estadoPago: {
      type: String,
      enum: { values: ESTADOS_PAGO, message: 'Estado de pago no valido: {VALUE}' },
      default: 'pendiente',
    },

    notas: {
      type: String,
      trim: true,
      maxlength: [500, 'Las notas no pueden superar 500 caracteres'],
      default: '',
    },
  },
  {
    timestamps: true,
    collection: 'reservas',
  }
);

// Acelera la consulta de solapamiento: reservas de una sala en un dia.
esquemaReserva.index({ sala: 1, fecha: 1 });

/**
 * Convierte "HH:MM" a minutos desde medianoche, para comparar horas
 * como numeros en lugar de como texto.
 * @param {string} hora
 * @returns {number}
 */
function aMinutos(hora) {
  const [h, m] = hora.split(':').map(Number);
  return h * 60 + m;
}

esquemaReserva.statics.aMinutos = aMinutos;
esquemaReserva.statics.TARIFA_DESCORCHE = TARIFA_DESCORCHE;

/**
 * Horas de duracion de la reserva, como virtual de solo lectura.
 */
esquemaReserva.virtual('horas').get(function horas() {
  if (!this.horaInicio || !this.horaFin) return 0;
  return (aMinutos(this.horaFin) - aMinutos(this.horaInicio)) / 60;
});

/**
 * Validaciones de coherencia del bloque horario y de los alimentos.
 * La validacion de aforo contra la sala y la deteccion de solapamiento
 * requieren consultar otras colecciones y viven en el controlador.
 */
esquemaReserva.pre('validate', function validarBloque(next) {
  if (this.horaInicio && this.horaFin) {
    if (aMinutos(this.horaFin) <= aMinutos(this.horaInicio)) {
      return next(new Error('La hora de fin debe ser posterior a la hora de inicio'));
    }
  }

  if (this.tipoAlimentos === 'externo' && this.consumo.length > 0) {
    return next(new Error('Una reserva con alimentos externos no puede incluir consumo de cafeteria'));
  }

  return next();
});

/**
 * Recalcula el desglose economico en el servidor antes de guardar.
 * El precio de la sala se resuelve en el controlador (que ya tiene el
 * documento de la sala) y se deja en subtotalSala; aqui se consolidan
 * consumo, descorche y total.
 */
esquemaReserva.pre('save', function calcularTotales(next) {
  this.subtotalConsumo = this.consumo.reduce(
    (acumulado, linea) => acumulado + linea.precioUnitario * linea.cantidad,
    0
  );

  this.tarifaDescorche = this.tipoAlimentos === 'externo' ? TARIFA_DESCORCHE : 0;

  const total = this.subtotalSala + this.subtotalConsumo + this.tarifaDescorche;
  this.total = Math.round(total * 100) / 100; // 2 decimales exactos

  return next();
});

esquemaReserva.set('toJSON', { virtuals: true });
esquemaReserva.set('toObject', { virtuals: true });

module.exports = mongoose.model('Booking', esquemaReserva);
module.exports.ESTADOS = ESTADOS;
module.exports.ESTADOS_PAGO = ESTADOS_PAGO;
module.exports.TIPOS_ALIMENTOS = TIPOS_ALIMENTOS;
module.exports.TARIFA_DESCORCHE = TARIFA_DESCORCHE;
