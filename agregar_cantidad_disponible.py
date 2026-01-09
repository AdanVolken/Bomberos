"""
Script para agregar el campo cantidad_disponible a la tabla productos
"""

import sqlite3
import os

DB_NAME = "Sistema_Tickets_DB.db"

def agregar_cantidad_disponible():
    """Agrega la columna cantidad_disponible a la tabla productos"""
    if not os.path.exists(DB_NAME):
        print(f"La base de datos {DB_NAME} no existe.")
        return False
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("AGREGANDO CAMPO cantidad_disponible")
    print("="*50 + "\n")
    
    try:
        # Verificar si la tabla productos tiene cantidad_disponible
        cursor.execute("PRAGMA table_info(productos)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if 'cantidad_disponible' not in columnas:
            # Agregar columna cantidad_disponible
            cursor.execute("""
                ALTER TABLE productos 
                ADD COLUMN cantidad_disponible INTEGER DEFAULT 0
            """)
            print("[OK] Columna 'cantidad_disponible' agregada a tabla 'productos'")
            
            # Establecer cantidad_disponible = cantidad_vendida para productos existentes
            # Esto permite que los productos ya vendidos no se puedan vender más
            # Si quieres permitir más ventas, puedes establecer un valor mayor
            cursor.execute("""
                UPDATE productos 
                SET cantidad_disponible = COALESCE(cantidad_vendida, 0) + 100
                WHERE cantidad_disponible IS NULL OR cantidad_disponible = 0
            """)
            print("[OK] Valores iniciales establecidos para productos existentes")
        else:
            print("[OK] Columna 'cantidad_disponible' ya existe")
        
        # Asegurar que todos los productos tengan cantidad_disponible >= 0
        cursor.execute("""
            UPDATE productos 
            SET cantidad_disponible = 0 
            WHERE cantidad_disponible IS NULL
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
    agregar_cantidad_disponible()
