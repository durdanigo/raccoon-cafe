/**
 * ===============================================================
 * Product.js - Catalogo unificado: cafeteria + libreria
 * ---------------------------------------------------------------
 * Un solo modelo cubre las dos lineas de producto porque ambas
 * comparten el mismo nucleo (nombre, precio, stock, disponibilidad)
 * y se diferencian por el campo "categoria":
 *
 *   categoria = 'cafeteria'  -> subcategoria: bebida_caliente |
 *                               bebida_fria | pasteleria | pack_evento
 *   categoria = 'libro'      -> subcategoria: libro_nuevo |
 *                               libro_usado | lectura_interna
 *
 * Reglas de negocio aplicadas en el esquema:
 *   - Un libro usado DEBE declarar su condicion (excelente, bueno,
 *     aceptable); un libro nuevo o de cafeteria no lleva condicion.
 *   - Los libros de lectura interna no se venden: precio 0 y se
 *     exige ubicacion de estante.
 *   - stock = null significa "sin control de stock" (bebidas que se
 *     preparan al momento).
 * ===============================================================
 */

const mongoose = require('mongoose');

const CATEGORIAS = ['cafeteria', 'libro'];

const SUBCATEGORIAS = [
  // Cafeteria
  'bebida_caliente',
  'bebida_fria',
  'pasteleria',
  'pack_evento',
  // Libreria
  'libro_nuevo',
  'libro_usado',
  'lectura_interna',
];

const CONDICIONES = ['excelente', 'bueno', 'aceptable'];

const esquemaProducto = new mongoose.Schema(
  {
    nombre: {
      type: String,
      required: [true, 'El nombre del producto es obligatorio'],
      trim: true,
      maxlength: [120, 'El nombre no puede superar 120 caracteres'],
      index: true,
    },

    categoria: {
      type: String,
      required: [true, 'La categoria es obligatoria'],
      enum: { values: CATEGORIAS, message: 'Categoria no valida: {VALUE}' },
      index: true,
    },

    subcategoria: {
      type: String,
      required: [true, 'La subcategoria es obligatoria'],
      enum: { values: SUBCATEGORIAS, message: 'Subcategoria no valida: {VALUE}' },
      index: true,
    },

    precio: {
      type: Number,
      required: [true, 'El precio es obligatorio'],
      min: [0, 'El precio no puede ser negativo'],
    },

    descripcion: {
      type: String,
      trim: true,
      maxlength: [400, 'La descripcion no puede superar 400 caracteres'],
      default: '',
    },

    /**
     * null  -> producto sin control de stock (se prepara al momento)
     * >= 0  -> unidades disponibles
     */
    stock: {
      type: Number,
      default: null,
      min: [0, 'El stock no puede ser negativo'],
    },

    // Umbral para la alerta de bajo stock en el panel administrativo.
    stockMinimo: {
      type: Number,
      default: 2,
      min: [0, 'El stock minimo no puede ser negativo'],
    },

    // ---------- Campos exclusivos de libros ----------
    autor: {
      type: String,
      trim: true,
      maxlength: [120, 'El autor no puede superar 120 caracteres'],
      default: '',
    },

    condicion: {
      type: String,
      enum: { values: [...CONDICIONES, null], message: 'Condicion no valida: {VALUE}' },
      default: null,
    },

    // Estante donde se ubica un libro de lectura interna (ej. "A1").
    ubicacion: {
      type: String,
      trim: true,
      uppercase: true,
      default: '',
    },

    imagen: {
      type: String,
      trim: true,
      default: '',
    },

    disponible: {
      type: Boolean,
      default: true,
      index: true,
    },
  },
  {
    timestamps: true,
    collection: 'productos',
  }
);

/**
 * Validacion cruzada entre categoria y subcategoria, y entre
 * subcategoria y los campos propios de libros.
 */
esquemaProducto.pre('validate', function validarCoherencia(next) {
  const subcategoriasCafeteria = ['bebida_caliente', 'bebida_fria', 'pasteleria', 'pack_evento'];
  const subcategoriasLibro = ['libro_nuevo', 'libro_usado', 'lectura_interna'];

  if (this.categoria === 'cafeteria' && !subcategoriasCafeteria.includes(this.subcategoria)) {
    return next(new Error(`La subcategoria "${this.subcategoria}" no corresponde a cafeteria`));
  }

  if (this.categoria === 'libro' && !subcategoriasLibro.includes(this.subcategoria)) {
    return next(new Error(`La subcategoria "${this.subcategoria}" no corresponde a libreria`));
  }

  // Un libro de segunda mano siempre declara su condicion.
  if (this.subcategoria === 'libro_usado' && !this.condicion) {
    return next(new Error('Un libro de segunda mano debe declarar su condicion'));
  }

  // Solo los libros usados llevan condicion.
  if (this.subcategoria !== 'libro_usado' && this.condicion) {
    this.condicion = null;
  }

  // Los libros de lectura interna no se venden y deben tener estante.
  if (this.subcategoria === 'lectura_interna') {
    this.precio = 0;
    if (!this.ubicacion) {
      return next(new Error('Un libro de lectura interna debe indicar su estante'));
    }
  }

  return next();
});

/**
 * Virtual usado por la tabla de inventario del dashboard para pintar
 * la alerta de bajo stock sin recalcular la regla en el frontend.
 */
esquemaProducto.virtual('bajoStock').get(function bajoStock() {
  if (this.stock === null || this.stock === undefined) return false;
  return this.stock <= this.stockMinimo;
});

esquemaProducto.set('toJSON', { virtuals: true });
esquemaProducto.set('toObject', { virtuals: true });

module.exports = mongoose.model('Product', esquemaProducto);
module.exports.CATEGORIAS = CATEGORIAS;
module.exports.SUBCATEGORIAS = SUBCATEGORIAS;
module.exports.CONDICIONES = CONDICIONES;
