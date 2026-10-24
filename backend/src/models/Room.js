/**
 * ===============================================================
 * Room.js - Las 6 salas fisicas de Raccoon Cafe
 * ---------------------------------------------------------------
 * Tipos de sala:
 *   cowork    (2) : trabajo individual / estudio silencioso
 *   encuentro (2) : reuniones, comites, clubes de lectura
 *   taller    (1) : manualidades, ceramica, bordado, acuarela
 *   social    (1) : eventos tematicos, cumpleanos, proyecciones
 *
 * El aforo se guarda como rango (minimo / maximo) porque cada sala
 * tiene una configuracion de mobiliario con holgura, y la validacion
 * de asistentes en Booking se apoya en capacidadMaxima.
 * ===============================================================
 */

const mongoose = require('mongoose');

const TIPOS_SALA = ['cowork', 'encuentro', 'taller', 'social'];

const esquemaSala = new mongoose.Schema(
  {
    codigo: {
      type: String,
      required: [true, 'El codigo de la sala es obligatorio'],
      unique: true,
      uppercase: true,
      trim: true,
      // Ejemplos validos: COW-01, ENC-02, TAL-01, SOC-01
      match: [/^[A-Z]{3}-\d{2}$/, 'El codigo debe tener el formato ABC-01'],
    },

    nombre: {
      type: String,
      required: [true, 'El nombre de la sala es obligatorio'],
      trim: true,
      maxlength: [80, 'El nombre no puede superar 80 caracteres'],
    },

    tipo: {
      type: String,
      required: [true, 'El tipo de sala es obligatorio'],
      enum: { values: TIPOS_SALA, message: 'Tipo de sala no valido: {VALUE}' },
      index: true,
    },

    capacidadMinima: {
      type: Number,
      required: [true, 'La capacidad minima es obligatoria'],
      min: [1, 'La capacidad minima debe ser al menos 1'],
    },

    capacidadMaxima: {
      type: Number,
      required: [true, 'La capacidad maxima es obligatoria'],
      min: [1, 'La capacidad maxima debe ser al menos 1'],
      validate: {
        validator(valor) {
          return valor >= this.capacidadMinima;
        },
        message: 'La capacidad maxima no puede ser menor que la minima',
      },
    },

    precioHora: {
      type: Number,
      required: [true, 'El precio por hora es obligatorio'],
      min: [0, 'El precio por hora no puede ser negativo'],
    },

    descripcion: {
      type: String,
      trim: true,
      maxlength: [400, 'La descripcion no puede superar 400 caracteres'],
      default: '',
    },

    // Lista de equipamiento mostrada como chips en la tarjeta de sala.
    equipamiento: {
      type: [String],
      default: [],
    },

    imagen: {
      type: String,
      trim: true,
      default: '',
    },

    // Permite retirar una sala del catalogo publico sin borrar su
    // historial de reservas.
    disponible: {
      type: Boolean,
      default: true,
      index: true,
    },
  },
  {
    timestamps: true,
    collection: 'salas',
  }
);

/**
 * Campo virtual de solo lectura usado por el frontend para mostrar
 * el aforo en una sola linea: "6 - 10 personas".
 */
esquemaSala.virtual('aforoTexto').get(function aforoTexto() {
  return `${this.capacidadMinima} - ${this.capacidadMaxima} personas`;
});

esquemaSala.set('toJSON', { virtuals: true });
esquemaSala.set('toObject', { virtuals: true });

module.exports = mongoose.model('Room', esquemaSala);
module.exports.TIPOS_SALA = TIPOS_SALA;
