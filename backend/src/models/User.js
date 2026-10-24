/**
 * ===============================================================
 * User.js - Usuarios del sistema (clientes, empleados y admin)
 * ---------------------------------------------------------------
 * Control de acceso basado en roles (RBAC):
 *   - cliente  : crea y consulta sus propias reservas.
 *   - empleado : gestiona reservas, check-in y stock.
 *   - admin    : ademas administra usuarios y catalogos.
 *
 * La contrasena NUNCA se almacena en texto plano: un hook pre-save
 * la convierte en hash con bcryptjs antes de escribir en Mongo.
 * ===============================================================
 */

const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const ROLES = ['cliente', 'empleado', 'admin'];

const esquemaUsuario = new mongoose.Schema(
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
      unique: true,
      lowercase: true,
      trim: true,
      match: [/^[^\s@]+@[^\s@]+\.[^\s@]+$/, 'El formato del correo no es valido'],
    },

    password: {
      type: String,
      required: [true, 'La contrasena es obligatoria'],
      minlength: [8, 'La contrasena debe tener al menos 8 caracteres'],
      // select:false => las consultas normales no devuelven el hash.
      // Para el login hay que pedirlo de forma explicita con .select('+password')
      select: false,
    },

    telefono: {
      type: String,
      trim: true,
      match: [/^[0-9+\-\s()]{7,20}$/, 'El telefono no tiene un formato valido'],
      default: '',
    },

    rol: {
      type: String,
      enum: { values: ROLES, message: 'Rol no valido: {VALUE}' },
      default: 'cliente',
      index: true,
    },

    activo: {
      type: Boolean,
      default: true,
    },

    ultimoAcceso: {
      type: Date,
      default: null,
    },
  },
  {
    timestamps: true, // createdAt y updatedAt automaticos
    collection: 'usuarios',
  }
);

/**
 * Hook pre-save: genera el hash de la contrasena.
 * Solo actua cuando el campo password fue modificado, para no volver
 * a hashear un hash existente en cada actualizacion del documento.
 */
esquemaUsuario.pre('save', async function hashearPassword(next) {
  if (!this.isModified('password')) return next();

  try {
    const sal = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, sal);
    return next();
  } catch (error) {
    return next(error);
  }
});

/**
 * Compara una contrasena en texto plano contra el hash almacenado.
 * @param {string} passwordPlano
 * @returns {Promise<boolean>}
 */
esquemaUsuario.methods.compararPassword = function compararPassword(passwordPlano) {
  return bcrypt.compare(passwordPlano, this.password);
};

/**
 * Elimina el hash de cualquier representacion JSON del documento,
 * como salvaguarda adicional por si alguna consulta lo trajo.
 */
esquemaUsuario.methods.toJSON = function toJSON() {
  const objeto = this.toObject();
  delete objeto.password;
  delete objeto.__v;
  return objeto;
};

module.exports = mongoose.model('User', esquemaUsuario);
module.exports.ROLES = ROLES;
