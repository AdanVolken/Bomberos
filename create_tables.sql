-- Script para crear las tablas del Sistema de Tickets
-- Base de datos: SQLite

-- Tabla: empresa
-- Almacena la información de la empresa (nombre y logo)
CREATE TABLE IF NOT EXISTS empresa (
    nombre TEXT NOT NULL,
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

