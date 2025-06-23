#!/usr/bin/env python3
"""
Script para inicializar completamente la base de datos del sistema TESJI
Este script debe ejecutarse ANTES que populate_academic_structure.py
"""

import sqlite3
import os
from datetime import datetime

def create_base_tables(db_path="tesji_rfid_system.db"):
    """Crea las tablas base del sistema"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Creando tablas base del sistema...")
    
    # Tabla de usuarios (base)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT UNIQUE,
        nombre_completo TEXT NOT NULL,
        matricula TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT,
        rol TEXT DEFAULT 'student',
        activo BOOLEAN DEFAULT TRUE,
        fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        ultimo_acceso DATETIME,
        carrera_id INTEGER,
        grupo_id INTEGER,
        semestre INTEGER DEFAULT 1
    )
    ''')
    
    # Tabla de asistencias (base)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS asistencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
        presente BOOLEAN DEFAULT TRUE,
        usuario_id INTEGER,
        materia_id INTEGER,
        grupo_id INTEGER,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    ''')
    
    # Tabla de carreras
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carreras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        codigo TEXT NOT NULL UNIQUE,
        semestres INTEGER NOT NULL,
        activa BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabla de materias
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        carrera_id INTEGER NOT NULL,
        semestre INTEGER NOT NULL,
        codigo TEXT,
        creditos INTEGER DEFAULT 5,
        activa BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (carrera_id) REFERENCES carreras (id),
        UNIQUE(nombre, carrera_id, semestre)
    )
    ''')
    
    # Tabla de grupos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS grupos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        carrera_id INTEGER NOT NULL,
        semestre INTEGER NOT NULL,
        periodo TEXT NOT NULL,
        activo BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (carrera_id) REFERENCES carreras (id)
    )
    ''')
    
    # Tabla de asignaciones maestro-materia
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS asignaciones_maestro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maestro_id INTEGER NOT NULL,
        materia_id INTEGER NOT NULL,
        grupo_id INTEGER NOT NULL,
        periodo TEXT NOT NULL,
        horario TEXT,
        aula TEXT,
        activa BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (maestro_id) REFERENCES usuarios (id),
        FOREIGN KEY (materia_id) REFERENCES materias (id),
        FOREIGN KEY (grupo_id) REFERENCES grupos (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Tablas base creadas exitosamente")

def create_admin_user(db_path="tesji_rfid_system.db"):
    """Crea usuario administrador por defecto"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("👨‍💼 Creando usuario administrador...")
    
    # Verificar si ya existe un admin
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "admin"')
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        import hashlib
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        
        cursor.execute('''
        INSERT INTO usuarios (nombre_completo, matricula, email, password_hash, rol, uid)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            "Administrador del Sistema",
            "ADMIN001",
            "admin@tesji.edu.mx",
            admin_password,
            "admin",
            "ADMIN001"
        ))
        
        conn.commit()
        print("✅ Usuario administrador creado")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
    else:
        print("ℹ️ Ya existe un usuario administrador")
    
    conn.close()

def create_sample_students(db_path="tesji_rfid_system.db"):
    """Crea algunos estudiantes de ejemplo"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("👨‍🎓 Creando estudiantes de ejemplo...")
    
    sample_students = [
        {
            "uid": "1234567890",
            "nombre": "Adrian Estudiante Ejemplo",
            "matricula": "202323652",
            "email": "adrian@tesji.edu.mx",
            "carrera_id": 1,  # ISC
            "semestre": 5
        },
        {
            "uid": "0987654321",
            "nombre": "María González López",
            "matricula": "202323653",
            "email": "maria.gonzalez@tesji.edu.mx",
            "carrera_id": 1,  # ISC
            "semestre": 4
        },
        {
            "uid": "1122334455",
            "nombre": "Carlos Hernández Ruiz",
            "matricula": "202323654",
            "email": "carlos.hernandez@tesji.edu.mx",
            "carrera_id": 2,  # II
            "semestre": 3
        }
    ]
    
    for student in sample_students:
        cursor.execute('''
        INSERT OR IGNORE INTO usuarios 
        (uid, nombre_completo, matricula, email, rol, carrera_id, semestre)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            student["uid"],
            student["nombre"],
            student["matricula"],
            student["email"],
            "student",
            student["carrera_id"],
            student["semestre"]
        ))
    
    conn.commit()
    conn.close()
    print("✅ Estudiantes de ejemplo creados")

def verify_database_structure(db_path="tesji_rfid_system.db"):
    """Verifica la estructura de la base de datos"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n📊 VERIFICANDO ESTRUCTURA DE BASE DE DATOS")
    print("=" * 50)
    
    # Obtener lista de tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"��� Tablas encontradas: {len(tables)}")
    
    for table in tables:
        table_name = table[0]
        print(f"\n🔍 Tabla: {table_name}")
        
        # Obtener estructura de la tabla
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            col_notnull = "NOT NULL" if col[3] else ""
            col_default = f"DEFAULT {col[4]}" if col[4] else ""
            print(f"   - {col_name} {col_type} {col_notnull} {col_default}")
        
        # Contar registros
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   📊 Registros: {count}")
    
    conn.close()
    print("\n✅ Verificación completada")

def main():
    print("🏫 INICIALIZADOR DE BASE DE DATOS TESJI")
    print("=" * 50)
    
    db_path = "tesji_rfid_system.db"
    
    try:
        # 1. Crear tablas base
        create_base_tables(db_path)
        
        # 2. Crear usuario administrador
        create_admin_user(db_path)
        
        # 3. Crear estudiantes de ejemplo
        create_sample_students(db_path)
        
        # 4. Verificar estructura
        verify_database_structure(db_path)
        
        print("\n🎉 INICIALIZACIÓN COMPLETADA")
        print("✅ La base de datos está lista para poblar con la estructura académica")
        print("\n📝 SIGUIENTE PASO:")
        print("   Ejecuta: python scripts/populate_academic_structure.py")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

