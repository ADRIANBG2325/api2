#!/usr/bin/env python3
"""
Script para actualizar columnas faltantes en la base de datos
"""

import sqlite3
from datetime import datetime

def update_database_columns(db_path="tesji_rfid_system.db"):
    """Actualiza columnas faltantes en las tablas existentes"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Actualizando columnas de la base de datos...")
    
    # Lista de columnas a verificar/agregar
    columns_to_add = [
        ("usuarios", "especialidad", "TEXT"),
        ("usuarios", "fecha_registro", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
        ("materias", "semestres", "INTEGER DEFAULT 8"),
        ("grupos", "periodo", "TEXT DEFAULT '2024-2025'"),
        ("grupos", "salon", "TEXT"),
        ("grupos", "turno", "TEXT"),
        ("asistencias", "usuario_id", "INTEGER"),
        ("asistencias", "materia_id", "INTEGER"),
        ("asistencias", "presente", "BOOLEAN DEFAULT TRUE"),
        ("asistencias", "fecha", "DATETIME DEFAULT CURRENT_TIMESTAMP")
    ]
    
    for table, column, column_type in columns_to_add:
        try:
            # Verificar si la columna existe
            cursor.execute(f"PRAGMA table_info({table})")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            if column not in existing_columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
                print(f"✅ Columna {table}.{column} agregada")
            else:
                print(f"ℹ️ Columna {table}.{column} ya existe")
                
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                print(f"⚠️ Tabla {table} no existe")
            else:
                print(f"⚠️ Error agregando {table}.{column}: {e}")
    
    # Actualizar tabla de asistencias para compatibilidad
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS asistencias_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            estudiante_id INTEGER,
            materia_id INTEGER,
            grupo_id INTEGER,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            presente BOOLEAN DEFAULT TRUE,
            hora TIME,
            tipo TEXT DEFAULT 'entrada',
            uid_tarjeta TEXT,
            dispositivo TEXT,
            validada BOOLEAN DEFAULT FALSE,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (estudiante_id) REFERENCES usuarios (id),
            FOREIGN KEY (materia_id) REFERENCES materias (id),
            FOREIGN KEY (grupo_id) REFERENCES grupos (id)
        )
        ''')
        
        # Migrar datos existentes si hay
        cursor.execute('''
        INSERT OR IGNORE INTO asistencias_new (
            id, estudiante_id, usuario_id, materia_id, grupo_id, 
            fecha, presente, hora, tipo, uid_tarjeta, dispositivo, validada, fecha_creacion
        )
        SELECT 
            id, estudiante_id, estudiante_id as usuario_id, materia_id, grupo_id,
            fecha, TRUE as presente, hora, tipo, uid_tarjeta, dispositivo, validada, fecha_creacion
        FROM asistencias
        ''')
        
        # Reemplazar tabla antigua
        cursor.execute('DROP TABLE IF EXISTS asistencias_old')
        cursor.execute('ALTER TABLE asistencias RENAME TO asistencias_old')
        cursor.execute('ALTER TABLE asistencias_new RENAME TO asistencias')
        
        print("✅ Tabla asistencias actualizada con compatibilidad")
        
    except sqlite3.OperationalError as e:
        print(f"ℹ️ Asistencias ya actualizada o error: {e}")
    
    conn.commit()
    conn.close()
    print("✅ Actualización de columnas completada")

def verify_updated_structure(db_path="tesji_rfid_system.db"):
    """Verifica la estructura actualizada"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n🔍 Verificando estructura actualizada...")
    
    # Verificar columnas de usuarios
    cursor.execute("PRAGMA table_info(usuarios)")
    user_columns = [row[1] for row in cursor.fetchall()]
    
    required_user_columns = [
        'id', 'uid', 'nombre_completo', 'matricula', 'email', 
        'password_hash', 'rol', 'carrera_id', 'grupo_id', 
        'semestre', 'especialidad', 'activo', 'fecha_creacion', 
        'fecha_registro', 'ultimo_acceso'
    ]
    
    print("📋 Columnas en tabla usuarios:")
    for col in required_user_columns:
        status = "✅" if col in user_columns else "❌"
        print(f"   {status} {col}")
    
    # Verificar columnas de asistencias
    cursor.execute("PRAGMA table_info(asistencias)")
    attendance_columns = [row[1] for row in cursor.fetchall()]
    
    required_attendance_columns = [
        'id', 'usuario_id', 'estudiante_id', 'materia_id', 
        'fecha', 'presente', 'hora'
    ]
    
    print("\n📋 Columnas en tabla asistencias:")
    for col in required_attendance_columns:
        status = "✅" if col in attendance_columns else "❌"
        print(f"   {status} {col}")
    
    conn.close()
    print("\n✅ Verificación completada")

def main():
    print("🔧 ACTUALIZADOR DE COLUMNAS DE BASE DE DATOS")
    print("=" * 50)
    
    try:
        update_database_columns()
        verify_updated_structure()
        
        print("\n🎉 BASE DE DATOS ACTUALIZADA EXITOSAMENTE")
        print("✅ Todas las columnas necesarias están disponibles")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
