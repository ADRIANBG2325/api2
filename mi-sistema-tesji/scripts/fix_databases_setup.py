#!/usr/bin/env python3
"""
Script para reparar y crear la estructura completa de la base de datos TESJI
Incluye todas las columnas necesarias para el funcionamiento del sistema
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime

def hash_password(password: str) -> str:
    """Genera hash de contraseña con salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def create_complete_tables(db_path="tesji_rfid_system.db"):
    """Crea todas las tablas con la estructura completa"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Creando estructura completa de la base de datos...")
    
    # Tabla de carreras
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carreras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo TEXT NOT NULL UNIQUE,
        semestres INTEGER DEFAULT 9,
        activa BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabla de grupos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS grupos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        carrera_id INTEGER NOT NULL,
        semestre INTEGER NOT NULL,
        periodo TEXT DEFAULT '2024-1',
        salon TEXT,
        turno TEXT,
        activo BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (carrera_id) REFERENCES carreras (id)
    )
    ''')
    
    # Crear nueva tabla de usuarios con todas las columnas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios_new (
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
        semestre INTEGER DEFAULT 4,
        especialidad TEXT,
        salon TEXT,
        FOREIGN KEY (carrera_id) REFERENCES carreras (id),
        FOREIGN KEY (grupo_id) REFERENCES grupos (id)
    )
    ''')
    
    # Migrar datos existentes si hay tabla usuarios antigua
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if cursor.fetchone():
            print("📦 Migrando datos existentes...")
            
            # Obtener columnas de la tabla actual
            cursor.execute("PRAGMA table_info(usuarios)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            # Construir query de migración dinámicamente
            common_columns = []
            for col in ['id', 'uid', 'nombre_completo', 'matricula', 'email', 'password_hash', 
                       'rol', 'activo', 'fecha_registro', 'ultimo_acceso', 'carrera_id', 
                       'grupo_id', 'semestre', 'especialidad']:
                if col in existing_columns:
                    common_columns.append(col)
            
            if common_columns:
                columns_str = ', '.join(common_columns)
                cursor.execute(f'''
                INSERT INTO usuarios_new ({columns_str})
                SELECT {columns_str} FROM usuarios
                ''')
                print(f"✅ Migrados datos de columnas: {', '.join(common_columns)}")
            
            # Renombrar tablas
            cursor.execute('DROP TABLE usuarios')
            cursor.execute('ALTER TABLE usuarios_new RENAME TO usuarios')
            print("✅ Tabla usuarios actualizada")
        else:
            cursor.execute('ALTER TABLE usuarios_new RENAME TO usuarios')
            print("✅ Tabla usuarios creada")
    except Exception as e:
        print(f"⚠️ Error en migración: {e}")
        cursor.execute('ALTER TABLE usuarios_new RENAME TO usuarios')
    
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
        horas_teoria INTEGER DEFAULT 0,
        horas_practica INTEGER DEFAULT 0,
        clave_oficial TEXT,
        FOREIGN KEY (carrera_id) REFERENCES carreras (id)
    )
    ''')
    
    # Tabla de asignaciones maestro
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS asignaciones_maestro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maestro_id INTEGER NOT NULL,
        materia_id INTEGER NOT NULL,
        grupo_id INTEGER NOT NULL,
        periodo TEXT NOT NULL DEFAULT '2024-1',
        activa BOOLEAN DEFAULT TRUE,
        fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (maestro_id) REFERENCES usuarios (id),
        FOREIGN KEY (materia_id) REFERENCES materias (id),
        FOREIGN KEY (grupo_id) REFERENCES grupos (id)
    )
    ''')
    
    # Tabla de horarios detallados
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS horarios_detallados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        materia_id INTEGER NOT NULL,
        grupo_id INTEGER NOT NULL,
        dia_semana TEXT NOT NULL,
        hora_inicio TEXT NOT NULL,
        hora_fin TEXT NOT NULL,
        tipo_clase TEXT DEFAULT 'Teoría',
        activo BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (materia_id) REFERENCES materias (id),
        FOREIGN KEY (grupo_id) REFERENCES grupos (id)
    )
    ''')
    
    # Tabla de asistencias actualizada
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS asistencias_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
        presente BOOLEAN DEFAULT TRUE,
        usuario_id INTEGER,
        materia_id INTEGER,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    ''')
    
    # Migrar asistencias si existen
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='asistencias'")
        if cursor.fetchone():
            cursor.execute('''
            INSERT INTO asistencias_new (id, fecha, presente, usuario_id, materia_id)
            SELECT id, fecha, 
                   CASE WHEN presente IS NULL THEN TRUE ELSE presente END,
                   usuario_id, materia_id
            FROM asistencias
            ''')
            cursor.execute('DROP TABLE asistencias')
            print("✅ Asistencias migradas")
        
        cursor.execute('ALTER TABLE asistencias_new RENAME TO asistencias')
    except Exception as e:
        print(f"⚠️ Error migrando asistencias: {e}")
        cursor.execute('ALTER TABLE asistencias_new RENAME TO asistencias')
    
    conn.commit()
    conn.close()
    print("✅ Estructura completa de tablas creada")

def populate_essential_data(db_path="tesji_rfid_system.db"):
    """Pobla datos esenciales del sistema"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📚 Poblando datos esenciales...")
    
    # Carreras del TESJI
    carreras = [
        ("Ingeniería en Sistemas Computacionales", "ISC", 9),
        ("Ingeniería Industrial", "II", 9),
        ("Ingeniería Mecánica", "IM", 9),
        ("Ingeniería Civil", "IC", 9),
        ("Licenciatura en Administración", "LA", 8),
        ("Ingeniería Química", "IQ", 9),
        ("Ingeniería en Logística", "IL", 9),
        ("Ingeniería en Tecnologías de la Información y Comunicaciones", "ITIC", 9)
    ]
    
    for nombre, codigo, semestres in carreras:
        cursor.execute('''
        INSERT OR IGNORE INTO carreras (nombre, codigo, semestres)
        VALUES (?, ?, ?)
        ''', (nombre, codigo, semestres))
    
    # Obtener ID de ISC
    cursor.execute('SELECT id FROM carreras WHERE codigo = "ISC"')
    isc_id = cursor.fetchone()[0]
    
    # Crear grupos básicos
    grupos = [
        ("Grupo 3402", isc_id, 4, "2024-1", "N1", "Matutino"),
        ("Grupo 3401", isc_id, 4, "2024-1", "N2", "Matutino")
    ]
    
    for nombre, carrera_id, semestre, periodo, salon, turno in grupos:
        cursor.execute('''
        INSERT OR IGNORE INTO grupos (nombre, carrera_id, semestre, periodo, salon, turno)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, carrera_id, semestre, periodo, salon, turno))
    
    # Crear usuario administrador
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "admin"')
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        admin_password_hash = hash_password("admin123")
        
        cursor.execute('''
        INSERT INTO usuarios (
            nombre_completo, matricula, email, password_hash, rol, activo
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            "Administrador TESJI",
            "ADMIN001",
            "admin@tesji.edu.mx",
            admin_password_hash,
            "admin",
            True
        ))
        print("✅ Usuario administrador creado")
    
    # Crear maestro de ejemplo
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "teacher"')
    teacher_count = cursor.fetchone()[0]
    
    if teacher_count == 0:
        teacher_password_hash = hash_password("teacher123")
        
        cursor.execute('''
        INSERT INTO usuarios (
            nombre_completo, matricula, email, password_hash, rol, 
            carrera_id, especialidad, activo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            "Lic. Juan Alberto Martínez Zamora",
            "PROF001",
            "juan.martinez@tesji.edu.mx",
            teacher_password_hash,
            "teacher",
            isc_id,
            "Métodos Numéricos",
            True
        ))
        print("✅ Maestro de ejemplo creado")
    
    # Crear estudiantes de ejemplo con salón asignado
    estudiantes_ejemplo = [
        ("Adrian Estudiante Ejemplo", "202323652", "adrian@tesji.edu.mx", "TEST001", isc_id, 4, "N1"),
        ("María González López", "202323653", "maria.gonzalez@tesji.edu.mx", "TEST002", isc_id, 4, "N2"),
        ("Carlos Hernández Ruiz", "202323654", "carlos.hernandez@tesji.edu.mx", "TEST003", isc_id, 4, "N1")
    ]
    
    # Obtener IDs de grupos
    cursor.execute('SELECT id FROM grupos WHERE nombre = "Grupo 3402"')
    grupo_3402_id = cursor.fetchone()
    grupo_3402_id = grupo_3402_id[0] if grupo_3402_id else None
    
    cursor.execute('SELECT id FROM grupos WHERE nombre = "Grupo 3401"')
    grupo_3401_id = cursor.fetchone()
    grupo_3401_id = grupo_3401_id[0] if grupo_3401_id else None
    
    for nombre, matricula, email, uid, carrera_id, semestre, salon in estudiantes_ejemplo:
        # Asignar grupo según salón
        grupo_id = grupo_3402_id if salon == "N1" else grupo_3401_id
        
        cursor.execute('''
        INSERT OR IGNORE INTO usuarios (
            nombre_completo, matricula, email, uid, rol, 
            carrera_id, grupo_id, semestre, salon, activo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            nombre, matricula, email, uid, "student",
            carrera_id, grupo_id, semestre, salon, True
        ))
    
    print("✅ Estudiantes de ejemplo creados")
    
    conn.commit()
    conn.close()
    print("✅ Datos esenciales poblados")

def verify_complete_structure(db_path="tesji_rfid_system.db"):
    """Verifica que la estructura esté completa"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔍 Verificando estructura completa...")
    
    # Verificar tabla usuarios
    cursor.execute("PRAGMA table_info(usuarios)")
    user_columns = [row[1] for row in cursor.fetchall()]
    
    required_columns = [
        'id', 'uid', 'nombre_completo', 'matricula', 'email', 'password_hash',
        'rol', 'activo', 'fecha_registro', 'ultimo_acceso', 'carrera_id',
        'grupo_id', 'semestre', 'especialidad', 'salon'
    ]
    
    print("📋 Columnas en tabla usuarios:")
    missing_columns = []
    for col in required_columns:
        if col in user_columns:
            print(f"   ✅ {col}")
        else:
            print(f"   ❌ {col} (FALTANTE)")
            missing_columns.append(col)
    
    if missing_columns:
        print(f"\n⚠️ Columnas faltantes: {', '.join(missing_columns)}")
        return False
    
    # Verificar datos
    cursor.execute('SELECT COUNT(*) FROM carreras')
    carreras_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM grupos')
    grupos_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "admin"')
    admin_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "student"')
    student_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "teacher"')
    teacher_count = cursor.fetchone()[0]
    
    print(f"\n📊 Datos en la base:")
    print(f"   🎓 Carreras: {carreras_count}")
    print(f"   👥 Grupos: {grupos_count}")
    print(f"   👨‍💼 Administradores: {admin_count}")
    print(f"   👨‍🎓 Estudiantes: {student_count}")
    print(f"   👨‍🏫 Maestros: {teacher_count}")
    
    conn.close()
    print("✅ Verificación completada")
    return True

def main():
    print("🔧 REPARADOR COMPLETO DE BASE DE DATOS TESJI")
    print("=" * 60)
    print("Este script reparará completamente la base de datos")
    print("agregando todas las columnas faltantes.")
    print("=" * 60)
    
    try:
        # 1. Crear estructura completa
        create_complete_tables()
        
        # 2. Poblar datos esenciales
        populate_essential_data()
        
        # 3. Verificar estructura
        if verify_complete_structure():
            print("\n🎉 BASE DE DATOS REPARADA EXITOSAMENTE")
            print("✅ Todas las columnas necesarias están disponibles")
            print("\n📝 CREDENCIALES DE PRUEBA:")
            print("   Admin - Usuario: ADMIN001, Contraseña: admin123")
            print("   Maestro - Usuario: PROF001, Contraseña: teacher123")
            print("   Estudiante - UID: TEST001 (Adrian)")
            print("\n🚀 El servidor debería funcionar correctamente ahora")
        else:
            print("\n❌ La estructura aún tiene problemas")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
