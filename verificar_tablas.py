"""
Script para verificar y crear las tablas en la base de datos SQLite
"""

import sqlite3
import os

DB_NAME = "Sistema_Tickets_DB.db"

def verificar_tablas():
    """Verifica qué tablas existen en la base de datos"""
    if not os.path.exists(DB_NAME):
        print(f"La base de datos {DB_NAME} no existe.")
        return False
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Obtener lista de tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    
    print(f"\nBase de datos: {DB_NAME}")
    print(f"Ubicación: {os.path.abspath(DB_NAME)}")
    print("\n" + "="*50)
    print("TABLAS EXISTENTES:")
    print("="*50)
    
    if tablas:
        for tabla in tablas:
            print(f"  - {tabla[0]}")
            
            # Mostrar estructura de cada tabla
            cursor.execute(f"PRAGMA table_info({tabla[0]});")
            columnas = cursor.fetchall()
            print(f"    Columnas:")
            for col in columnas:
                print(f"      • {col[1]} ({col[2]})")
            print()
    else:
        print("  No hay tablas en la base de datos.")
    
    conn.close()
    return True

def crear_tablas_directamente():
    """Crea las tablas directamente usando SQL"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("CREANDO TABLAS...")
    print("="*50 + "\n")
    
    try:
        # Tabla: empresa
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empresa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                imagen TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Tabla 'empresa' creada")
        
        # Tabla: productos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL,
                imagen TEXT,
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Tabla 'productos' creada")
        
        # Tabla: ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL DEFAULT 1,
                precio_unitario REAL NOT NULL,
                total REAL NOT NULL,
                fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
            )
        """)
        print("[OK] Tabla 'ventas' creada")
        
        # Crear índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ventas_producto_id ON ventas(producto_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha_venta)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_productos_activo ON productos(activo)
        """)
        print("[OK] Índices creados")
        
        conn.commit()
        print("\n[OK] Todas las tablas creadas exitosamente!\n")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error al crear tablas: {e}\n")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("VERIFICACIÓN DE BASE DE DATOS")
    print("="*50)
    
    # Verificar tablas existentes
    if verificar_tablas():
        # Preguntar si crear las tablas
        print("\n" + "="*50)
        respuesta = input("¿Deseas crear/verificar las tablas? (s/n): ").lower()
        
        if respuesta in ['s', 'si', 'y', 'yes']:
            crear_tablas_directamente()
            print("\nVerificando nuevamente...")
            verificar_tablas()
    else:
        print(f"\nCreando base de datos {DB_NAME}...")
        crear_tablas_directamente()

