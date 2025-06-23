#!/usr/bin/env python3
"""
Script para crear una base de datos completamente nueva y limpia para TESJI
Elimina la base anterior y crea todo desde cero
"""

import sqlite3
import os
import hashlib
import secrets
from datetime import datetime

def delete_old_database(db_path="tesji_rfid_system.db"):
    """Elimina la base de datos anterior si existe"""
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️ Base de datos anterior eliminada: {db_path}")
    else:
        print("ℹ️ No existe base de datos anterior")

def create_fresh_database(db_path="tesji_rfid_system.db"):
    """Crea una base de datos completamente nueva"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🆕 Creando base de datos nueva...")
    
    # 1. Tabla de carreras
    cursor.execute('''
    CREATE TABLE carreras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        codigo TEXT NOT NULL UNIQUE,
        semestres INTEGER NOT NULL,
        activa BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. Tabla de salones
    cursor.execute('''
    CREATE TABLE salones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        capacidad INTEGER DEFAULT 30,
        tipo TEXT DEFAULT 'Aula',
        activo BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 3. Tabla de grupos
    cursor.execute('''
    CREATE TABLE grupos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        carrera_id INTEGER NOT NULL,
        semestre INTEGER NOT NULL,
        salon_id INTEGER,
        periodo TEXT NOT NULL DEFAULT '2024-2025',
        turno TEXT DEFAULT 'Matutino',
        activo BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (carrera_id) REFERENCES carreras (id),
        FOREIGN KEY (salon_id) REFERENCES salones (id)
    )
    ''')
    
    # 4. Tabla de materias
    cursor.execute('''
    CREATE TABLE materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo TEXT UNIQUE,
        carrera_id INTEGER NOT NULL,
        semestre INTEGER NOT NULL,
        creditos INTEGER DEFAULT 5,
        horas_teoria INTEGER DEFAULT 3,
        horas_practica INTEGER DEFAULT 2,
        activa BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (carrera_id) REFERENCES carreras (id)
    )
    ''')
    
    # 5. Tabla de usuarios
    cursor.execute('''
    CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT UNIQUE,
        nombre_completo TEXT NOT NULL,
        matricula TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT,
        rol TEXT DEFAULT 'student' CHECK (rol IN ('admin', 'teacher', 'student')),
        carrera_id INTEGER,
        grupo_id INTEGER,
        semestre INTEGER DEFAULT 1,
        especialidad TEXT,
        activo BOOLEAN DEFAULT TRUE,
        fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        ultimo_acceso DATETIME,
        FOREIGN KEY (carrera_id) REFERENCES carreras (id),
        FOREIGN KEY (grupo_id) REFERENCES grupos (id)
    )
    ''')
    
    # 6. Tabla de asignaciones maestro-materia
    cursor.execute('''
    CREATE TABLE asignaciones_maestro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maestro_id INTEGER NOT NULL,
        materia_id INTEGER NOT NULL,
        grupo_id INTEGER NOT NULL,
        periodo TEXT NOT NULL DEFAULT '2024-2025',
        activa BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (maestro_id) REFERENCES usuarios (id),
        FOREIGN KEY (materia_id) REFERENCES materias (id),
        FOREIGN KEY (grupo_id) REFERENCES grupos (id),
        UNIQUE(maestro_id, materia_id, grupo_id, periodo)
    )
    ''')
    
    # 7. Tabla de horarios
    cursor.execute('''
    CREATE TABLE horarios_detallados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asignacion_id INTEGER NOT NULL,
        dia_semana TEXT NOT NULL CHECK (dia_semana IN ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes')),
        hora_inicio TEXT NOT NULL,
        hora_fin TEXT NOT NULL,
        tipo_clase TEXT DEFAULT 'Teoría' CHECK (tipo_clase IN ('Teoría', 'Práctica', 'Laboratorio')),
        activo BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (asignacion_id) REFERENCES asignaciones_maestro (id)
    )
    ''')
    
    # 8. Tabla de asistencias
    cursor.execute('''
    CREATE TABLE asistencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        asignacion_id INTEGER NOT NULL,
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
        presente BOOLEAN DEFAULT TRUE,
        observaciones TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
        FOREIGN KEY (asignacion_id) REFERENCES asignaciones_maestro (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Estructura de base de datos creada")

def insert_basic_data(db_path="tesji_rfid_system.db"):
    """Inserta datos básicos necesarios"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📚 Insertando datos básicos...")
    
    # 1. Carreras principales
    carreras = [
        ("Ingeniería en Sistemas Computacionales", "ISC", 9),
        ("Ingeniería Industrial", "II", 9),
        ("Ingeniería Mecatrónica", "IM", 9)
    ]
    
    for nombre, codigo, semestres in carreras:
        cursor.execute('''
        INSERT INTO carreras (nombre, codigo, semestres) VALUES (?, ?, ?)
        ''', (nombre, codigo, semestres))
    
    # 2. Salones
    salones = [
        ("N1", 35, "Aula"),
        ("N2", 35, "Aula"),
        ("LAB-1", 25, "Laboratorio"),
        ("LAB-2", 25, "Laboratorio"),
        ("A-101", 40, "Aula")
    ]
    
    for nombre, capacidad, tipo in salones:
        cursor.execute('''
        INSERT INTO salones (nombre, capacidad, tipo) VALUES (?, ?, ?)
        ''', (nombre, capacidad, tipo))
    
    # 3. Grupos principales (4to semestre ISC)
    cursor.execute('SELECT id FROM carreras WHERE codigo = "ISC"')
    carrera_isc_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM salones WHERE nombre = "N1"')
    salon_n1_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM salones WHERE nombre = "N2"')
    salon_n2_id = cursor.fetchone()[0]
    
    grupos = [
        ("ISC-4A", carrera_isc_id, 4, salon_n1_id, "Matutino"),
        ("ISC-4B", carrera_isc_id, 4, salon_n2_id, "Matutino")
    ]
    
    for nombre, carrera_id, semestre, salon_id, turno in grupos:
        cursor.execute('''
        INSERT INTO grupos (nombre, carrera_id, semestre, salon_id, turno) 
        VALUES (?, ?, ?, ?, ?)
        ''', (nombre, carrera_id, semestre, salon_id, turno))
    
    # 4. Materias de 4to semestre ISC
    materias_4to = [
        ("Métodos Numéricos", "SCC-1017", 5, 3, 2),
        ("Ecuaciones Diferenciales", "ACF-0905", 5, 4, 1),
        ("Fundamentos de Base de Datos", "AEF-1031", 5, 2, 3),
        ("Tópicos Avanzados de Programación", "SCD-1027", 5, 2, 3),
        ("Arquitectura de Computadoras", "SCD-1003", 5, 3, 2),
        ("Taller de Sistemas Operativos", "SCA-1026", 4, 1, 3),
        ("Taller de Ética", "ACA-0907", 4, 4, 0)
    ]
    
    for nombre, codigo, creditos, teoria, practica in materias_4to:
        cursor.execute('''
        INSERT INTO materias (nombre, codigo, carrera_id, semestre, creditos, horas_teoria, horas_practica)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, codigo, carrera_isc_id, 4, creditos, teoria, practica))
    
    # 5. Usuario administrador
    admin_password = "admin123"
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((admin_password + salt).encode()).hexdigest()
    password_hash_final = f"{salt}:{password_hash}"
    
    cursor.execute('''
    INSERT INTO usuarios (uid, nombre_completo, matricula, email, password_hash, rol)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', ("ADMIN001", "Administrador TESJI", "ADMIN001", "admin@tesji.edu.mx", password_hash_final, "admin"))
    
    # 6. Maestros
    maestros = [
        ("PROF001", "Dr. Juan Carlos Pérez López", "PROF001", "juan.perez@tesji.edu.mx", "Programación y Bases de Datos"),
        ("PROF002", "Lic. Juan Alberto Martínez Zamora", "PROF002", "juan.martinez@tesji.edu.mx", "Métodos Numéricos"),
        ("PROF003", "Ing. Rodolfo Guadalupe Alcántara Rosales", "PROF003", "rodolfo.alcantara@tesji.edu.mx", "Ecuaciones Diferenciales"),
        ("PROF004", "Mtra. Yadira Esther Jiménez Pérez", "PROF004", "yadira.jimenez@tesji.edu.mx", "Fundamentos de Base de Datos")
    ]
    
    teacher_password = "profesor123"
    for uid, nombre, matricula, email, especialidad in maestros:
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((teacher_password + salt).encode()).hexdigest()
        password_hash_final = f"{salt}:{password_hash}"
        
        cursor.execute('''
        INSERT INTO usuarios (uid, nombre_completo, matricula, email, password_hash, rol, carrera_id, especialidad)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (uid, nombre, matricula, email, password_hash_final, "teacher", carrera_isc_id, especialidad))
    
    conn.commit()
    conn.close()
    print("✅ Datos básicos insertados")

def create_sample_students(db_path="tesji_rfid_system.db"):
    """Crea estudiantes de ejemplo bien organizados"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("👨‍🎓 Creando estudiantes de ejemplo...")
    
    # Obtener IDs necesarios
    cursor.execute('SELECT id FROM carreras WHERE codigo = "ISC"')
    carrera_isc_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM grupos WHERE nombre = "ISC-4A"')
    grupo_4a_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM grupos WHERE nombre = "ISC-4B"')
    grupo_4b_id = cursor.fetchone()[0]
    
    # Estudiantes para grupo ISC-4A
    estudiantes_4a = [
        ("1234567890", "Adrian Estudiante Ejemplo", "202323652", "adrian@tesji.edu.mx"),
        ("2345678901", "María González López", "202323653", "maria.gonzalez@tesji.edu.mx"),
        ("3456789012", "Carlos Hernández Ruiz", "202323654", "carlos.hernandez@tesji.edu.mx")
    ]
    
    # Estudiantes para grupo ISC-4B
    estudiantes_4b = [
        ("4567890123", "Ana Martínez Silva", "202323655", "ana.martinez@tesji.edu.mx"),
        ("5678901234", "Luis García Pérez", "202323656", "luis.garcia@tesji.edu.mx"),
        ("6789012345", "Sofia Rodríguez Torres", "202323657", "sofia.rodriguez@tesji.edu.mx")
    ]
    
    student_password = "123456"
    
    # Insertar estudiantes grupo 4A
    for uid, nombre, matricula, email in estudiantes_4a:
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((student_password + salt).encode()).hexdigest()
        password_hash_final = f"{salt}:{password_hash}"
        
        cursor.execute('''
        INSERT INTO usuarios (uid, nombre_completo, matricula, email, password_hash, rol, carrera_id, grupo_id, semestre)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (uid, nombre, matricula, email, password_hash_final, "student", carrera_isc_id, grupo_4a_id, 4))
    
    # Insertar estudiantes grupo 4B
    for uid, nombre, matricula, email in estudiantes_4b:
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((student_password + salt).encode()).hexdigest()
        password_hash_final = f"{salt}:{password_hash}"
        
        cursor.execute('''
        INSERT INTO usuarios (uid, nombre_completo, matricula, email, password_hash, rol, carrera_id, grupo_id, semestre)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (uid, nombre, matricula, email, password_hash_final, "student", carrera_isc_id, grupo_4b_id, 4))
    
    conn.commit()
    conn.close()
    print("✅ Estudiantes creados y asignados a grupos")

def create_assignments_and_schedules(db_path="tesji_rfid_system.db"):
    """Crea asignaciones de maestros y horarios"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📅 Creando asignaciones y horarios...")
    
    # Obtener IDs
    cursor.execute('SELECT id FROM usuarios WHERE matricula = "PROF002"')  # Juan Alberto - Métodos
    maestro_metodos_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM usuarios WHERE matricula = "PROF003"')  # Rodolfo - Ecuaciones
    maestro_ecuaciones_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM usuarios WHERE matricula = "PROF004"')  # Yadira - BD
    maestro_bd_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM usuarios WHERE matricula = "PROF001"')  # Juan Carlos - Programación
    maestro_prog_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM materias WHERE codigo = "SCC-1017"')  # Métodos Numéricos
    materia_metodos_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM materias WHERE codigo = "ACF-0905"')  # Ecuaciones
    materia_ecuaciones_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM materias WHERE codigo = "AEF-1031"')  # BD
    materia_bd_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM materias WHERE codigo = "SCD-1027"')  # Tópicos Programación
    materia_prog_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM grupos WHERE nombre = "ISC-4A"')
    grupo_4a_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM grupos WHERE nombre = "ISC-4B"')
    grupo_4b_id = cursor.fetchone()[0]
    
    # Crear asignaciones para ambos grupos
    asignaciones = [
        # Grupo ISC-4A
        (maestro_metodos_id, materia_metodos_id, grupo_4a_id),
        (maestro_ecuaciones_id, materia_ecuaciones_id, grupo_4a_id),
        (maestro_bd_id, materia_bd_id, grupo_4a_id),
        (maestro_prog_id, materia_prog_id, grupo_4a_id),
        # Grupo ISC-4B
        (maestro_metodos_id, materia_metodos_id, grupo_4b_id),
        (maestro_ecuaciones_id, materia_ecuaciones_id, grupo_4b_id),
        (maestro_bd_id, materia_bd_id, grupo_4b_id),
        (maestro_prog_id, materia_prog_id, grupo_4b_id)
    ]
    
    asignacion_ids = []
    for maestro_id, materia_id, grupo_id in asignaciones:
        cursor.execute('''
        INSERT INTO asignaciones_maestro (maestro_id, materia_id, grupo_id)
        VALUES (?, ?, ?)
        ''', (maestro_id, materia_id, grupo_id))
        asignacion_ids.append(cursor.lastrowid)
    
    # Crear horarios de ejemplo
    horarios = [
        # Métodos Numéricos - ISC-4A
        (asignacion_ids[0], "Lunes", "08:00", "10:00", "Teoría"),
        (asignacion_ids[0], "Miércoles", "08:00", "10:00", "Práctica"),
        # Ecuaciones Diferenciales - ISC-4A
        (asignacion_ids[1], "Martes", "10:00", "12:00", "Teoría"),
        (asignacion_ids[1], "Jueves", "10:00", "12:00", "Teoría"),
        # Base de Datos - ISC-4A
        (asignacion_ids[2], "Lunes", "14:00", "16:00", "Teoría"),
        (asignacion_ids[2], "Viernes", "14:00", "17:00", "Laboratorio"),
        # Tópicos Programación - ISC-4A
        (asignacion_ids[3], "Martes", "16:00", "18:00", "Teoría"),
        (asignacion_ids[3], "Jueves", "16:00", "19:00", "Laboratorio"),
        
        # Métodos Numéricos - ISC-4B
        (asignacion_ids[4], "Lunes", "10:00", "12:00", "Teoría"),
        (asignacion_ids[4], "Miércoles", "10:00", "12:00", "Práctica"),
        # Ecuaciones Diferenciales - ISC-4B
        (asignacion_ids[5], "Martes", "08:00", "10:00", "Teoría"),
        (asignacion_ids[5], "Jueves", "08:00", "10:00", "Teoría"),
        # Base de Datos - ISC-4B
        (asignacion_ids[6], "Lunes", "16:00", "18:00", "Teoría"),
        (asignacion_ids[6], "Viernes", "16:00", "19:00", "Laboratorio"),
        # Tópicos Programación - ISC-4B
        (asignacion_ids[7], "Martes", "14:00", "16:00", "Teoría"),
        (asignacion_ids[7], "Jueves", "14:00", "17:00", "Laboratorio")
    ]
    
    for asignacion_id, dia, inicio, fin, tipo in horarios:
        cursor.execute('''
        INSERT INTO horarios_detallados (asignacion_id, dia_semana, hora_inicio, hora_fin, tipo_clase)
        VALUES (?, ?, ?, ?, ?)
        ''', (asignacion_id, dia, inicio, fin, tipo))
    
    conn.commit()
    conn.close()
    print("✅ Asignaciones y horarios creados")

def verify_new_database(db_path="tesji_rfid_system.db"):
    """Verifica que la nueva base de datos esté correcta"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n📊 VERIFICANDO NUEVA BASE DE DATOS")
    print("=" * 50)
    
    # Contar registros
    tables = ['carreras', 'salones', 'grupos', 'materias', 'usuarios', 'asignaciones_maestro', 'horarios_detallados']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"📋 {table}: {count} registros")
    
    # Verificar estudiantes por grupo
    cursor.execute('''
    SELECT g.nombre, COUNT(u.id) as estudiantes
    FROM grupos g
    LEFT JOIN usuarios u ON u.grupo_id = g.id AND u.rol = 'student'
    GROUP BY g.id
    ORDER BY g.nombre
    ''')
    
    print("\n👥 ESTUDIANTES POR GRUPO:")
    for grupo, estudiantes in cursor.fetchall():
        print(f"   {grupo}: {estudiantes} estudiantes")
    
    # Verificar asignaciones
    cursor.execute('''
    SELECT 
        u.nombre_completo as maestro,
        m.nombre as materia,
        g.nombre as grupo
    FROM asignaciones_maestro am
    JOIN usuarios u ON am.maestro_id = u.id
    JOIN materias m ON am.materia_id = m.id
    JOIN grupos g ON am.grupo_id = g.id
    ORDER BY g.nombre, m.nombre
    ''')
    
    print("\n📚 ASIGNACIONES MAESTRO-MATERIA:")
    for maestro, materia, grupo in cursor.fetchall():
        print(f"   {grupo}: {materia} - {maestro}")
    
    conn.close()
    print("\n✅ Verificación completada")

def main():
    print("🆕 CREADOR DE BASE DE DATOS LIMPIA TESJI")
    print("=" * 50)
    
    try:
        # 1. Eliminar base anterior
        delete_old_database()
        
        # 2. Crear estructura nueva
        create_fresh_database()
        
        # 3. Insertar datos básicos
        insert_basic_data()
        
        # 4. Crear estudiantes
        create_sample_students()
        
        # 5. Crear asignaciones y horarios
        create_assignments_and_schedules()
        
        # 6. Verificar resultado
        verify_new_database()
        
        print("\n🎉 BASE DE DATOS NUEVA CREADA EXITOSAMENTE")
        print("✅ Todo está limpio y bien organizado")
        print("\n🔑 CREDENCIALES:")
        print("   Admin: admin@tesji.edu.mx / admin123")
        print("   Maestros: profesor123")
        print("   Estudiantes: 123456")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
