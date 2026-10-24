/**
 * ===============================================================
 * seed.js - Poblado inicial de la base de datos
 * ---------------------------------------------------------------
 * Ejecutar con:  npm run seed
 *
 * ADVERTENCIA: el script BORRA el contenido de las colecciones
 * salas, productos, usuarios y contactos antes de insertar los datos
 * de prueba. No ejecutarlo contra una base con informacion real.
 *
 * Las reservas no se siembran: dependen de usuarios y salas ya
 * creados y se generan desde la aplicacion.
 * ===============================================================
 */

require('dotenv').config();

const mongoose = require('mongoose');

const { conectarDB } = require('../config/db');
const User = require('../models/User');
const Room = require('../models/Room');
const Product = require('../models/Product');
const Contact = require('../models/Contact');

// ---------------------------------------------------------------
// 1. Las 6 salas fisicas
// ---------------------------------------------------------------
const salas = [
  {
    codigo: 'COW-01',
    nombre: 'Co-work Bosque',
    tipo: 'cowork',
    capacidadMinima: 6,
    capacidadMaxima: 10,
    precioHora: 12.0,
    descripcion:
      'Sala de trabajo silencioso con escritorios individuales. Ideal para jornadas de estudio o trabajo remoto concentrado.',
    equipamiento: ['Escritorios individuales', 'Sillas ergonomicas', 'Regletas de alta densidad', 'Wi-Fi dedicado'],
    disponible: true,
  },
  {
    codigo: 'COW-02',
    nombre: 'Co-work Roble',
    tipo: 'cowork',
    capacidadMinima: 6,
    capacidadMaxima: 10,
    precioHora: 12.0,
    descripcion:
      'Segunda sala de coworking silencioso, con la misma configuracion de escritorios individuales y luz natural lateral.',
    equipamiento: ['Escritorios individuales', 'Sillas ergonomicas', 'Regletas de alta densidad', 'Luz natural'],
    disponible: true,
  },
  {
    codigo: 'ENC-01',
    nombre: 'Encuentro Nogal',
    tipo: 'encuentro',
    capacidadMinima: 8,
    capacidadMaxima: 12,
    precioHora: 18.0,
    descripcion:
      'Sala de reuniones con mesa central redonda. Pensada para comites de trabajo, reuniones corporativas y clubes de lectura.',
    equipamiento: ['Mesa central redonda', 'Pizarra', 'Pantalla', 'Wi-Fi dedicado'],
    disponible: true,
  },
  {
    codigo: 'ENC-02',
    nombre: 'Encuentro Cedro',
    tipo: 'encuentro',
    capacidadMinima: 8,
    capacidadMaxima: 12,
    precioHora: 18.0,
    descripcion:
      'Sala de reuniones con mesa imperial alargada, apropiada para presentaciones y sesiones de trabajo prolongadas.',
    equipamiento: ['Mesa imperial', 'Pizarra', 'Pantalla', 'Wi-Fi dedicado'],
    disponible: true,
  },
  {
    codigo: 'TAL-01',
    nombre: 'Taller Raccoon',
    tipo: 'taller',
    capacidadMinima: 12,
    capacidadMaxima: 20,
    precioHora: 25.0,
    descripcion:
      'Sala de trabajo manual con mesas modulares largas, tomas de agua y piso despejado. Para ceramica en frio, bordado, acuarela y manualidades.',
    equipamiento: ['Mesas modulares largas', 'Sillas moviles', 'Tomas de agua', 'Piso lavable', 'Almacenamiento de materiales'],
    disponible: true,
  },
  {
    codigo: 'SOC-01',
    nombre: 'Sala Social Luna',
    tipo: 'social',
    capacidadMinima: 15,
    capacidadMaxima: 25,
    precioHora: 32.0,
    descripcion:
      'Espacio para eventos tematicos, cumpleanos y proyecciones, con mesas tipo cafe configurables y equipo audiovisual opcional.',
    equipamiento: ['Mesas tipo cafe', 'Sillas configurables', 'Proyector', 'Sistema de audio', 'Iluminacion ambiental'],
    disponible: true,
  },
];

// ---------------------------------------------------------------
// 2. Menu de cafeteria
// ---------------------------------------------------------------
const cafeteria = [
  // --- Bebidas calientes ---
  { nombre: 'Espresso Raccoon', categoria: 'cafeteria', subcategoria: 'bebida_caliente', precio: 2.0, descripcion: 'Shot doble de nuestra mezcla de la casa.', stock: null },
  { nombre: 'Americano Doble', categoria: 'cafeteria', subcategoria: 'bebida_caliente', precio: 2.5, descripcion: 'Espresso doble alargado con agua caliente.', stock: null },
  { nombre: 'Cappuccino Tradicional', categoria: 'cafeteria', subcategoria: 'bebida_caliente', precio: 3.25, descripcion: 'Partes iguales de espresso, leche y espuma.', stock: null },
  { nombre: 'Flat White Vainilla', categoria: 'cafeteria', subcategoria: 'bebida_caliente', precio: 3.75, descripcion: 'Leche texturizada con un toque de vainilla natural.', stock: null },
  { nombre: 'Latte Caramelo / Moca', categoria: 'cafeteria', subcategoria: 'bebida_caliente', precio: 4.0, descripcion: 'Latte con salsa de caramelo o chocolate a eleccion.', stock: null },

  // --- Bebidas frias e infusiones ---
  { nombre: 'Iced Matcha Latte', categoria: 'cafeteria', subcategoria: 'bebida_fria', precio: 4.25, descripcion: 'Matcha ceremonial batido con leche fria.', stock: null },
  { nombre: 'Cold Brew Raccoon', categoria: 'cafeteria', subcategoria: 'bebida_fria', precio: 3.5, descripcion: 'Extraccion en frio de 18 horas, servida con hielo.', stock: null },
  { nombre: 'Infusion Frutos Rojos', categoria: 'cafeteria', subcategoria: 'bebida_fria', precio: 2.75, descripcion: 'Infusion de frutos rojos, fria o caliente.', stock: null },

  // --- Pasteleria y snacks ---
  { nombre: 'Croissant de Mantequilla', categoria: 'cafeteria', subcategoria: 'pasteleria', precio: 2.5, descripcion: 'Hojaldre horneado la misma manana.', stock: 18, stockMinimo: 5 },
  { nombre: 'Croissant de Almendras', categoria: 'cafeteria', subcategoria: 'pasteleria', precio: 3.25, descripcion: 'Relleno de crema de almendras y almendra laminada.', stock: 12, stockMinimo: 5 },
  { nombre: 'Tarta de Zanahoria', categoria: 'cafeteria', subcategoria: 'pasteleria', precio: 3.75, descripcion: 'Porcion con frosting de queso crema.', stock: 10, stockMinimo: 3 },
  { nombre: 'Brownie con Sal Marina', categoria: 'cafeteria', subcategoria: 'pasteleria', precio: 2.8, descripcion: 'Chocolate 70% con escamas de sal marina.', stock: 14, stockMinimo: 4 },
  { nombre: 'Toast de Aguacate', categoria: 'cafeteria', subcategoria: 'pasteleria', precio: 4.5, descripcion: 'Pan de masa madre, aguacate, semillas y limon.', stock: 8, stockMinimo: 3 },

  // --- Packs para eventos ---
  { nombre: 'Pack Taller Basico', categoria: 'cafeteria', subcategoria: 'pack_evento', precio: 22.0, descripcion: 'Cafe de filtro, infusiones y bocaditos dulces para grupos de taller.', stock: null },
  { nombre: 'Pack Fiesta Social', categoria: 'cafeteria', subcategoria: 'pack_evento', precio: 35.0, descripcion: 'Bebidas frias, snacks salados y pasteleria para eventos tematicos.', stock: null },
  { nombre: 'Tarifa de Descorche / Alimento Externo', categoria: 'cafeteria', subcategoria: 'pack_evento', precio: 15.0, descripcion: 'Tarifa fija de servicio y limpieza cuando el cliente trae alimentos externos.', stock: null },
];

// ---------------------------------------------------------------
// 3. Catalogo de libreria
// ---------------------------------------------------------------
const libreria = [
  // --- Venta: libros nuevos ---
  { nombre: 'Cien Anos de Soledad', autor: 'Gabriel Garcia Marquez', categoria: 'libro', subcategoria: 'libro_nuevo', precio: 18.5, stock: 4, stockMinimo: 2, descripcion: 'Edicion conmemorativa, tapa blanda.' },
  { nombre: 'Habitos Atomicos', autor: 'James Clear', categoria: 'libro', subcategoria: 'libro_nuevo', precio: 21.0, stock: 6, stockMinimo: 2, descripcion: 'Guia practica sobre cambio de habitos.' },
  { nombre: 'Klara y el Sol', autor: 'Kazuo Ishiguro', categoria: 'libro', subcategoria: 'libro_nuevo', precio: 19.0, stock: 3, stockMinimo: 2, descripcion: 'Novela sobre inteligencia artificial y vinculo humano.' },

  // --- Venta: segunda mano ---
  { nombre: 'Harry Potter y el Prisionero de Azkaban', autor: 'J. K. Rowling', categoria: 'libro', subcategoria: 'libro_usado', condicion: 'bueno', precio: 8.5, stock: 1, stockMinimo: 0, descripcion: 'Ejemplar unico, lomo con uso leve.' },
  { nombre: 'El Nombre del Viento', autor: 'Patrick Rothfuss', categoria: 'libro', subcategoria: 'libro_usado', condicion: 'excelente', precio: 12.0, stock: 1, stockMinimo: 0, descripcion: 'Ejemplar unico, practicamente nuevo.' },
  { nombre: 'Rayuela', autor: 'Julio Cortazar', categoria: 'libro', subcategoria: 'libro_usado', condicion: 'aceptable', precio: 6.0, stock: 1, stockMinimo: 0, descripcion: 'Ejemplar unico con subrayados del lector anterior.' },

  // --- Lectura interna (no vendible) ---
  { nombre: 'Antologia Poetica', autor: 'Mario Benedetti', categoria: 'libro', subcategoria: 'lectura_interna', precio: 0, stock: 1, ubicacion: 'A1', descripcion: 'Solo para lectura en mesa o en sala.' },
  { nombre: 'El Principito', autor: 'Antoine de Saint-Exupery', categoria: 'libro', subcategoria: 'lectura_interna', precio: 0, stock: 1, ubicacion: 'B2', descripcion: 'Solo para lectura en mesa o en sala.' },
];

// ---------------------------------------------------------------
// 4. Usuarios de prueba
// ---------------------------------------------------------------
// Las contrasenas se escriben aqui en texto plano a proposito: el
// hook pre-save de User las convierte en hash antes de guardarlas.
// Son credenciales de demostracion, NO usar en produccion.
const usuarios = [
  { nombre: 'Administradora Raccoon', email: 'admin@raccooncafe.com', password: 'Admin2026!', rol: 'admin', telefono: '0999000001' },
  { nombre: 'Empleado Barra', email: 'empleado@raccooncafe.com', password: 'Empleado2026!', rol: 'empleado', telefono: '0999000002' },
  { nombre: 'Cliente de Prueba', email: 'cliente@raccooncafe.com', password: 'Cliente2026!', rol: 'cliente', telefono: '0999000003' },
];

/**
 * Limpia las colecciones y vuelve a insertar los datos de prueba.
 */
async function sembrar() {
  await conectarDB();

  console.log('\n[SEED] Limpiando colecciones...');
  await Promise.all([
    Room.deleteMany({}),
    Product.deleteMany({}),
    User.deleteMany({}),
    Contact.deleteMany({}),
  ]);
  console.log('[SEED] Colecciones vaciadas.');

  console.log('[SEED] Insertando salas...');
  const salasCreadas = await Room.insertMany(salas);
  console.log(`[SEED] ${salasCreadas.length} salas insertadas.`);

  console.log('[SEED] Insertando productos de cafeteria y libreria...');
  // insertMany con runValidators para que se apliquen las reglas del
  // esquema (condicion obligatoria en usados, estante en lectura interna).
  const productosCreados = await Product.insertMany([...cafeteria, ...libreria], {
    runValidators: true,
  });
  console.log(`[SEED] ${productosCreados.length} productos insertados.`);

  console.log('[SEED] Insertando usuarios...');
  // Se usa create (no insertMany) para que corra el hook pre-save que
  // hashea la contrasena de cada usuario.
  const usuariosCreados = await User.create(usuarios);
  console.log(`[SEED] ${usuariosCreados.length} usuarios insertados.`);

  console.log('\n===============================================');
  console.log('  Poblado completado');
  console.log('===============================================');
  console.log(`  Salas      : ${salasCreadas.length}`);
  console.log(`  Cafeteria  : ${cafeteria.length}`);
  console.log(`  Libreria   : ${libreria.length}`);
  console.log(`  Usuarios   : ${usuariosCreados.length}`);
  console.log('-----------------------------------------------');
  console.log('  Credenciales de demostracion:');
  usuarios.forEach((u) => console.log(`   ${u.rol.padEnd(9)} -> ${u.email} / ${u.password}`));
  console.log('===============================================\n');

  await mongoose.connection.close();
  process.exit(0);
}

sembrar().catch(async (error) => {
  console.error(`[SEED] Fallo el poblado: ${error.message}`);
  await mongoose.connection.close();
  process.exit(1);
});
