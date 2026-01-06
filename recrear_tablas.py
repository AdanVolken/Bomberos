"""
Script para recrear las tablas con la nueva estructura simplificada
ADVERTENCIA: Esto eliminará todas las tablas existentes y sus datos
"""

import sqlite3
import os

DB_NAME = "Sistema_Tickets_DB.db"

def recrear_tablas():
    """Recrea las tablas con la nueva estructura"""
    if not os.path.exists(DB_NAME):
        print(f"La base de datos {DB_NAME} no existe.")
        return False
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("RECREANDO TABLAS CON NUEVA ESTRUCTURA")
    print("="*50 + "\n")
    print("ADVERTENCIA: Esto eliminará las tablas existentes")
    print("="*50 + "\n")
    
    try:
        # Eliminar tablas existentes
        cursor.execute("DROP TABLE IF EXISTS ventas")
        cursor.execute("DROP TABLE IF EXISTS productos")
        cursor.execute("DROP TABLE IF EXISTS empresa")
        print("[OK] Tablas antiguas eliminadas")
        
        # Crear tabla: empresa (solo nombre y logo)
        cursor.execute("""
            CREATE TABLE empresa (
                nombre TEXT NOT NULL,
                logo TEXT
            )
        """)
        print("[OK] Tabla 'empresa' creada (nombre, logo)")
        
        # Crear tabla: productos (id, nombre, precio, imagen, cantidad_vendida)
        cursor.execute("""
            CREATE TABLE productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL,
                imagen TEXT,
                cantidad_vendida INTEGER DEFAULT 0
            )
        """)
        print("[OK] Tabla 'productos' creada (id, nombre, precio, imagen, cantidad_vendida)")
        
        conn.commit()
        print("\n" + "="*50)
        print("[OK] TABLAS RECREADAS EXITOSAMENTE!")
        print("="*50 + "\n")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error al recrear tablas: {e}\n")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    respuesta = input("¿Estás seguro de que quieres recrear las tablas? (s/n): ").lower()
    if respuesta in ['s', 'si', 'y', 'yes']:
        recrear_tablas()
        print("\nAhora puedes cargar datos con:")
        print("  python cargar_productos_ejemplo.py")
    else:
        print("\nOperación cancelada.\n")

