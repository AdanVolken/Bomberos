"""
Script para aplicar los cambios a la base de datos
Elimina la tabla ventas y agrega cantidad_vendida a productos
"""

import sqlite3
import os

DB_NAME = "Sistema_Tickets_DB.db"

def aplicar_cambios():
    """Aplica los cambios a la base de datos"""
    if not os.path.exists(DB_NAME):
        print(f"La base de datos {DB_NAME} no existe.")
        return False
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("APLICANDO CAMBIOS A LA BASE DE DATOS")
    print("="*50 + "\n")
    
    try:
        # 1. Eliminar tabla ventas si existe
        cursor.execute("DROP TABLE IF EXISTS ventas")
        print("[OK] Tabla 'ventas' eliminada")
        
        # 2. Verificar si la tabla productos tiene cantidad_vendida
        cursor.execute("PRAGMA table_info(productos)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if 'cantidad_vendida' not in columnas:
            # Agregar columna cantidad_vendida
            cursor.execute("""
                ALTER TABLE productos 
                ADD COLUMN cantidad_vendida INTEGER DEFAULT 0
            """)
            print("[OK] Columna 'cantidad_vendida' agregada a tabla 'productos'")
        else:
            print("[OK] Columna 'cantidad_vendida' ya existe")
        
        # 3. Asegurar que todos los productos tengan cantidad_vendida = 0 si es NULL
        cursor.execute("""
            UPDATE productos 
            SET cantidad_vendida = 0 
            WHERE cantidad_vendida IS NULL
        """)
        print("[OK] Valores NULL actualizados a 0")
        
        conn.commit()
        print("\n" + "="*50)
        print("[OK] CAMBIOS APLICADOS EXITOSAMENTE!")
        print("="*50 + "\n")
        
        # Mostrar estructura final
        print("Estructura de la tabla 'productos':")
        cursor.execute("PRAGMA table_info(productos)")
        columnas = cursor.fetchall()
        for col in columnas:
            print(f"  - {col[1]} ({col[2]})")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error al aplicar cambios: {e}\n")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    aplicar_cambios()

