-- Script para crear las tablas del Sistema de Tickets
-- Base de datos: SQLite

-- Tabla: empresa
-- Almacena la información de la empresa (nombre y logo)
CREATE TABLE IF NOT EXISTS empresa (
    nombre TEXT NOT NULL,
    nombre_caja TEXT,
    logo TEXT
);

-- Tabla: productos
-- Almacena los productos disponibles
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL,
    imagen TEXT,
    cantidad_vendida INTEGER DEFAULT 0,
    cantidad_disponible INTEGER DEFAULT 0
);

-- ==================== LICENCIAS ====================

CREATE TABLE IF NOT EXISTS licencia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    max_maquinas INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS licencia_maquinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    licencia_id INTEGER NOT NULL,
    mac TEXT NOT NULL,
    fecha_activacion TEXT NOT NULL,
    FOREIGN KEY (licencia_id) REFERENCES licencia(id)
);

-- ==================== MEDIOS DE PAGO ====================

CREATE TABLE IF NOT EXISTS medios_pago (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    activo INTEGER DEFAULT 1
);

-- ==================== VENTAS ====================

CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora TEXT NOT NULL,
    total REAL NOT NULL,
    medio_pago_id INTEGER NOT NULL,
    corte_id INTEGER,
    FOREIGN KEY (medio_pago_id) REFERENCES medios_pago(id),
    FOREIGN KEY (corte_id) REFERENCES cortes_caja(id)
);

-- ==================== DETALLE DE VENTAS ====================

CREATE TABLE IF NOT EXISTS ventas_detalle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario REAL NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- ==================== CORTES DE CAJA ====================

CREATE TABLE IF NOT EXISTS cortes_caja (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora TEXT NOT NULL,
    total_acumulado REAL NOT NULL,
    ultima_venta_id INTEGER NOT NULL
);
