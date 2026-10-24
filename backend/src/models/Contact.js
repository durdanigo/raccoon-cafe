/**
 * ===============================================================
 * Contact.js - Mensajes del formulario de contacto publico
 * ---------------------------------------------------------------
 * Alimenta el formulario de contacto exigido por la rubrica. No
 * requiere autenticacion para escribir (POST publico), pero solo
 * empleados y admin pueden leer y cambiar su estado.
 *
 * Flujo del estado: nuevo -> leido -> respondido  (o archivado)
 * ===============================================================
 */

const mongoose = require('mongoose');

const ESTADOS_MENSAJE = ['nuevo', 'leido', 'respondido', 'archivado'];

const ASUNTOS = ['reserva', 'eventos', 'libreria', 'cafeteria', 'otro'];

const esquemaContacto = new mongoose.Schema(
  {
    nombre: {
      type: String,
      required: [true, 'El nombre es obligatorio'],
      trim: true,
      minlength: [3, 'El nombre debe tener al menos 3 caracteres'],
      maxlength: [80, 'El nombre no puede superar 80 caracteres'],
    },

    email: {
      type: String,
      required: [true, 'El correo es obligatorio'],
      lowercase: true,
      trim: true,
      match: [/^[^\s@]+@[^\s@]+\.[^\s@]+$/, 'El formato del correo no es valido'],
    },

    telefono: {
      type: String,
      trim: true,
      default: '',
      match: [/^$|^[0-9+\-\s()]{7,20}$/, 'El telefono no tiene un formato valido'],
    },

    asunto: {
      type: String,
      required: [true, 'El asunto es obligatorio'],
      enum: { values: ASUNTOS, message: 'Asunto no valido: {VALUE}' },
      default: 'otro',
    },

    mensaje: {
      type: String,
      required: [true, 'El mensaje es obligatorio'],
      trim: true,
      minlength: [10, 'El mensaje debe tener al menos 10 caracteres'],
      maxlength: [1000, 'El mensaje no puede superar 1000 caracteres'],
    },

    estado: {
      type: String,
      enum: { values: ESTADOS_MENSAJE, message: 'Estado no valido: {VALUE}' },
      default: 'nuevo',
      index: true,
    },

    // Empleado o admin que atendio el mensaje.
    atendidoPor: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      default: null,
    },
  },
  {
    timestamps: true,
    collection: 'contactos',
  }
);

module.exports = mongoose.model('Contact', esquemaContacto);
module.exports.ESTADOS_MENSAJE = ESTADOS_MENSAJE;
module.exports.ASUNTOS = ASUNTOS;
