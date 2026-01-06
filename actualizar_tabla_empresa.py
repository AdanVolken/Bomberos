"""
Script para actualizar la tabla empresa: cambiar 'imagen' por 'logo'
"""

import sqlite3
import os

DB_NAME = "Sistema_Tickets_DB.db"

def actualizar_tabla_empresa():
    """Actualiza la tabla empresa para usar 'logo' en lugar de 'imagen'"""
    if not os.path.exists(DB_NAME):
        print(f"La base de datos {DB_NAME} no existe.")
        return False
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("ACTUALIZANDO TABLA EMPRESA")
    print("="*50 + "\n")
    
    try:
        # Verificar estructura actual
        cursor.execute("PRAGMA table_info(empresa)")
        columnas = cursor.fetchall()
        nombres_columnas = [col[1] for col in columnas]
        
        print("Columnas actuales:", nombres_columnas)
        
        # Si tiene 'imagen' pero no 'logo', renombrar
        if 'imagen' in nombres_columnas and 'logo' not in nombres_columnas:
            # SQLite no soporta ALTER TABLE RENAME COLUMN directamente en versiones antiguas
            # Necesitamos recrear la tabla
            
            # 1. Crear tabla temporal con la estructura correcta
            cursor.execute("""
                CREATE TABLE empresa_temp (
                    nombre TEXT NOT NULL,
                    logo TEXT
                )
            """)
            
            # 2. Copiar datos de la tabla antigua a la nueva
            cursor.execute("""
                INSERT INTO empresa_temp (nombre, logo)
                SELECT nombre, imagen FROM empresa
            """)
            
            # 3. Eliminar tabla antigua
            cursor.execute("DROP TABLE empresa")
            
            # 4. Renombrar tabla temporal
            cursor.execute("ALTER TABLE empresa_temp RENAME TO empresa")
            
            print("[OK] Columna 'imagen' renombrada a 'logo'")
            
        elif 'logo' in nombres_columnas:
            print("[OK] La tabla ya tiene la columna 'logo'")
        else:
            # Si no tiene ninguna, crear la estructura correcta
            cursor.execute("DROP TABLE IF EXISTS empresa")
            cursor.execute("""
                CREATE TABLE empresa (
                    nombre TEXT NOT NULL,
                    logo TEXT
                )
            """)
            print("[OK] Tabla 'empresa' recreada con estructura correcta")
        
        conn.commit()
        print("\n" + "="*50)
        print("[OK] TABLA EMPRESA ACTUALIZADA!")
        print("="*50 + "\n")
        
        # Mostrar estructura final
        print("Estructura final de la tabla 'empresa':")
        cursor.execute("PRAGMA table_info(empresa)")
        columnas = cursor.fetchall()
        for col in columnas:
            print(f"  - {col[1]} ({col[2]})")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error al actualizar tabla: {e}\n")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    actualizar_tabla_empresa()

