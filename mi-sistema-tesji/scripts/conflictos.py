#!/usr/bin/env python3
"""
Script para resolver conflictos en la base de datos y crear estructura limpia
Maneja correctamente las migraciones sin errores
"""

import sqlite3
import hashlib
import secrets
import os
from datetime import datetime

def hash_password(password: str) -> str:
    """Genera hash de contraseña con salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def backup_database(db_path="tesji_rfid_system.db"):
    """Crea respaldo de la base de datos"""
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Respaldo creado: {backup_path}")
        return backup_path
    return None

def get_table_info(cursor, table_name):
    """Obtiene información de una tabla"""
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cursor.fetchall()]  # Solo nombres de columnas
    except:
        return []

def safe_migrate_usuarios(cursor):
    """Migra la tabla usuarios de forma segura"""
    print("🔄 Migrando tabla usuarios...")
    
    # Verificar si existe tabla usuarios
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
    if not cursor.fetchone():
        print("   ℹ️ No existe tabla usuarios anterior")
        return
    
    # Obtener columnas existentes
    existing_columns = get_table_info(cursor, 'usuarios')
    print(f"   📋 Columnas existentes: {existing_columns}")
    
    # Crear nueva tabla usuarios con estructura completa
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios_temp (
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
    
    # Migrar datos existentes
    common_columns = []
    required_columns = ['id', 'uid', 'nombre_completo', 'matricula', 'email', 'password_hash', 
                       'rol', 'activo', 'fecha_registro', 'ultimo_acceso', 'carrera_id', 
                       'grupo_id', 'semestre', 'especialidad', 'salon']
    
    for col in required_columns:
        if col in existing_columns:
            common_columns.append(col)
    
    if common_columns:
        columns_str = ', '.join(common_columns)
        cursor.execute(f'''
        INSERT INTO usuarios_temp ({columns_str})
        SELECT {columns_str} FROM usuarios
        ''')
        print(f"   ✅ Migrados datos de: {', '.join(common_columns)}")
    
    # Reemplazar tabla
    cursor.execute('DROP TABLE usuarios')
    cursor.execute('ALTER TABLE usuarios_temp RENAME TO usuarios')
    print("   ✅ Tabla usuarios actualizada")

def safe_migrate_asistencias(cursor):
    """Migra la tabla asistencias de forma segura"""
    print("🔄 Migrando tabla asistencias...")
    
    # Verificar si existe tabla asistencias
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='asistencias'")
    if not cursor.fetchone():
        print("   ℹ️ No existe tabla asistencias anterior")
        # Crear tabla nueva
        cursor.execute('''
        CREATE TABLE asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            presente BOOLEAN DEFAULT TRUE,
            usuario_id INTEGER,
            materia_id INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
        ''')
        print("   ✅ Tabla asistencias creada")
        return
    
    # Obtener columnas existentes
    existing_columns = get_table_info(cursor, 'asistencias')
    print(f"   📋 Columnas existentes: {existing_columns}")
    
    # Crear nueva tabla temporal
    cursor.execute('''
    CREATE TABLE asistencias_temp (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
        presente BOOLEAN DEFAULT TRUE,
        usuario_id INTEGER,
        materia_id INTEGER,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    ''')
    
    # Migrar datos existentes
    try:
        if 'presente' in existing_columns:
            cursor.execute('''
            INSERT INTO asistencias_temp (id, fecha, presente, usuario_id, materia_id)
            SELECT id, fecha, presente, usuario_id, materia_id FROM asistencias
            ''')
        else:
            cursor.execute('''
            INSERT INTO asistencias_temp (id, fecha, presente, usuario_id, materia_id)
            SELECT id, fecha, TRUE, usuario_id, materia_id FROM asistencias
            ''')
        print("   ✅ Datos migrados")
    except Exception as e:
        print(f"   ⚠️ Error migrando datos: {e}")
    
    # Reemplazar tabla
    cursor.execute('DROP TABLE asistencias')
    cursor.execute('ALTER TABLE asistencias_temp RENAME TO asistencias')
    print("   ✅ Tabla asistencias actualizada")

def create_missing_tables(cursor):
    """Crea tablas faltantes"""
    print("🔧 Creando tablas faltantes...")
    
    # Tabla de carreras
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carreras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
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
    
    print("✅ Tablas creadas/actualizadas")

def populate_basic_data(cursor):
    """Pobla datos básicos del sistema"""
    print("📚 Poblando datos básicos...")
    
    # Verificar si ya hay datos
    cursor.execute('SELECT COUNT(*) FROM carreras')
    if cursor.fetchone()[0] > 0:
        print("   ℹ️ Ya existen datos básicos")
        return
    
    # Carreras básicas
    carreras = [
        ("Ingeniería en Sistemas Computacionales", "ISC", 9),
        ("Ingeniería Industrial", "II", 9),
        ("Ingeniería Mecánica", "IM", 9),
        ("Ingeniería Civil", "IC", 9),
        ("Licenciatura en Administración", "LA", 8)
    ]
    
    for nombre, codigo, semestres in carreras:
        cursor.execute('''
        INSERT OR IGNORE INTO carreras (nombre, codigo, semestres)
        VALUES (?, ?, ?)
        ''', (nombre, codigo, semestres))
    
    # Usuario administrador
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "admin"')
    if cursor.fetchone()[0] == 0:
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
        print("   ✅ Usuario administrador creado")
    
    print("✅ Datos básicos poblados")

def verify_structure(cursor):
    """Verifica la estructura final"""
    print("🔍 Verificando estructura...")
    
    # Verificar tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = ['usuarios', 'carreras', 'grupos', 'materias', 'asistencias', 
                      'asignaciones_maestro', 'horarios_detallados']
    
    for table in required_tables:
        if table in tables:
            print(f"   ✅ {table}")
        else:
            print(f"   ❌ {table} (FALTANTE)")
    
    # Verificar columnas de usuarios
    user_columns = get_table_info(cursor, 'usuarios')
    required_user_columns = ['salon', 'carrera_id', 'grupo_id', 'semestre']
    
    print("\n📋 Columnas críticas en usuarios:")
    for col in required_user_columns:
        if col in user_columns:
            print(f"   ✅ {col}")
        else:
            print(f"   ❌ {col} (FALTANTE)")
    
    # Contar datos
    cursor.execute('SELECT COUNT(*) FROM carreras')
    carreras_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "admin"')
    admin_count = cursor.fetchone()[0]
    
    print(f"\n📊 Datos:")
    print(f"   🎓 Carreras: {carreras_count}")
    print(f"   👨‍💼 Administradores: {admin_count}")

def main():
    print("🔧 REPARADOR DE CONFLICTOS DE BASE DE DATOS")
    print("=" * 60)
    
    db_path = "tesji_rfid_system.db"
    
    try:
        # 1. Crear respaldo
        backup_path = backup_database(db_path)
        
        # 2. Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 3. Migrar tablas problemáticas
        safe_migrate_usuarios(cursor)
        safe_migrate_asistencias(cursor)
        
        # 4. Crear tablas faltantes
        create_missing_tables(cursor)
        
        # 5. Poblar datos básicos
        populate_basic_data(cursor)
        
        # 6. Confirmar cambios
        conn.commit()
        
        # 7. Verificar estructura
        verify_structure(cursor)
        
        conn.close()
        
        print("\n🎉 REPARACIÓN COMPLETADA EXITOSAMENTE")
        print("✅ Base de datos lista para usar")
        print(f"✅ Respaldo disponible en: {backup_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
