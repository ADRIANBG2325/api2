#!/usr/bin/env python3
"""
Script para configurar horarios, grupos y asignaciones de maestros del TESJI
Basado en los horarios reales proporcionados
"""

import sqlite3
import json
from datetime import datetime, time

# Datos de los grupos y horarios
GRUPOS_HORARIOS = {
    "N2": {
        "nombre": "Grupo N2",
        "carrera": "ISC",
        "semestre": 4,
        "salon": "N2",
        "turno": "Vespertino",
        "materias": [
            {
                "numero": 13,
                "nombre": "Ecuaciones Diferenciales",
                "clave": "ACF-0905",
                "ht": 3, "hp": 2, "creditos": 5,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "13:00", "hora_fin": "15:00"},
                    {"dia": "Miércoles", "hora_inicio": "12:00", "hora_fin": "15:00"}
                ],
                "docente": "Ing. Rodolfo Guadalupe Alcántara Rosales"
            },
            {
                "numero": 14,
                "nombre": "Métodos Numéricos",
                "clave": "SCC-1017",
                "ht": 2, "hp": 2, "creditos": 4,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "11:00", "hora_fin": "13:00"},
                    {"dia": "Miércoles", "hora_inicio": "11:00", "hora_fin": "13:00"}
                ],
                "docente": "Lic. Juan Alberto Martínez Zamora"
            },
            {
                "numero": 15,
                "nombre": "Tópicos Avanzados de Programación",
                "clave": "SCD-1027",
                "ht": 2, "hp": 3, "creditos": 5,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "12:00", "hora_fin": "15:00"},
                    {"dia": "Miércoles", "hora_inicio": "09:00", "hora_fin": "11:00"}
                ],
                "docente": "Víctor David Maya Arce"
            },
            {
                "numero": 16,
                "nombre": "Fundamentos de Base de Datos",
                "clave": "AEF-1031",
                "ht": 3, "hp": 2, "creditos": 5,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "11:00", "hora_fin": "13:00"},
                    {"dia": "Miércoles", "hora_inicio": "08:00", "hora_fin": "11:00"}
                ],
                "docente": "Mtra. Yadira Esther Jiménez Pérez"
            },
            {
                "numero": 17,
                "nombre": "Taller de Sistemas Operativos",
                "clave": "SCA-1026",
                "ht": 0, "hp": 4, "creditos": 4,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "07:00", "hora_fin": "09:00"},
                    {"dia": "Miércoles", "hora_inicio": "07:00", "hora_fin": "09:00"}
                ],
                "docente": "Mtro. Anselmo Martínez Montalvo"
            },
            {
                "numero": 18,
                "nombre": "Arquitectura de Computadoras",
                "clave": "SCD-1003",
                "ht": 2, "hp": 3, "creditos": 5,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "13:00", "hora_fin": "15:00"},
                    {"dia": "Miércoles", "hora_inicio": "09:00", "hora_fin": "12:00"}
                ],
                "docente": "Ing. Alfredo Aguilar López"
            },
            {
                "numero": 19,
                "nombre": "Taller de Ética",
                "clave": "ACA-0907",
                "ht": 0, "hp": 4, "creditos": 4,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "10:00", "hora_fin": "12:00"},
                    {"dia": "Miércoles", "hora_inicio": "13:00", "hora_fin": "15:00"}
                ],
                "docente": "C.P. Sonia Vázquez Alcántara"
            }
        ]
    },
    "N1": {
        "nombre": "Grupo N1",
        "carrera": "ISC",
        "semestre": 4,
        "salon": "N1",
        "turno": "Matutino",
        "materias": [
            {
                "numero": 20,
                "nombre": "Ecuaciones Diferenciales",
                "clave": "ACF-0905",
                "ht": 3, "hp": 2, "creditos": 5,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "09:00", "hora_fin": "12:00"},
                    {"dia": "Miércoles", "hora_inicio": "11:00", "hora_fin": "13:00"}
                ],
                "docente": "Ing. Rodolfo Guadalupe Alcántara Rosales"
            },
            {
                "numero": 21,
                "nombre": "Métodos Numéricos",
                "clave": "SCC-1017",
                "ht": 2, "hp": 2, "creditos": 4,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "07:00", "hora_fin": "09:00"},
                    {"dia": "Miércoles", "hora_inicio": "07:00", "hora_fin": "09:00"}
                ],
                "docente": "Lic. Juan Alberto Martínez Zamora"
            },
            {
                "numero": 22,
                "nombre": "Tópicos Avanzados de Programación",
                "clave": "SCD-1027",
                "ht": 2, "hp": 3, "creditos": 5,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "13:00", "hora_fin": "15:00"},
                    {"dia": "Miércoles", "hora_inicio": "14:00", "hora_fin": "17:00"}
                ],
                "docente": "Ing. José Lucio Hernández Noguez"
            },
            {
                "numero": 23,
                "nombre": "Fundamentos de Base de Datos",
                "clave": "AEF-1031",
                "ht": 3, "hp": 2, "creditos": 5,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "15:00", "hora_fin": "18:00"},
                    {"dia": "Miércoles", "hora_inicio": "11:00", "hora_fin": "13:00"}
                ],
                "docente": "Víctor David Maya Arce"
            },
            {
                "numero": 24,
                "nombre": "Taller de Sistemas Operativos",
                "clave": "SCA-1026",
                "ht": 0, "hp": 4, "creditos": 4,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "13:00", "hora_fin": "15:00"},
                    {"dia": "Miércoles", "hora_inicio": "07:00", "hora_fin": "09:00"}
                ],
                "docente": "Mtro. Anselmo Martínez Montalvo"
            },
            {
                "numero": 25,
                "nombre": "Arquitectura de Computadoras",
                "clave": "SCD-1003",
                "ht": 2, "hp": 3, "creditos": 5,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "11:00", "hora_fin": "13:00"},
                    {"dia": "Miércoles", "hora_inicio": "12:00", "hora_fin": "15:00"}
                ],
                "docente": "Ing. Alfredo Aguilar López"
            },
            {
                "numero": 26,
                "nombre": "Taller de Ética",
                "clave": "ACA-0907",
                "ht": 0, "hp": 4, "creditos": 4,
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "09:00", "hora_fin": "11:00"},
                    {"dia": "Miércoles", "hora_inicio": "09:00", "hora_fin": "11:00"}
                ],
                "docente": "C.P. Sonia Vázquez Alcántara"
            }
        ]
    }
}

# Maestros con sus datos completos
MAESTROS_DATA = {
    "Ing. Rodolfo Guadalupe Alcántara Rosales": {
        "matricula": "PROF001",
        "email": "rodolfo.alcantara@tesji.edu.mx",
        "especialidad": "Matemáticas",
        "carreras": ["ISC"]
    },
    "Lic. Juan Alberto Martínez Zamora": {
        "matricula": "PROF002", 
        "email": "juan.martinez@tesji.edu.mx",
        "especialidad": "Métodos Numéricos",
        "carreras": ["ISC"]
    },
    "Víctor David Maya Arce": {
        "matricula": "PROF003",
        "email": "victor.maya@tesji.edu.mx", 
        "especialidad": "Programación",
        "carreras": ["ISC"]
    },
    "Mtra. Yadira Esther Jiménez Pérez": {
        "matricula": "PROF004",
        "email": "yadira.jimenez@tesji.edu.mx",
        "especialidad": "Base de Datos",
        "carreras": ["ISC"]
    },
    "Mtro. Anselmo Martínez Montalvo": {
        "matricula": "PROF005",
        "email": "anselmo.martinez@tesji.edu.mx",
        "especialidad": "Sistemas Operativos", 
        "carreras": ["ISC"]
    },
    "Ing. Alfredo Aguilar López": {
        "matricula": "PROF006",
        "email": "alfredo.aguilar@tesji.edu.mx",
        "especialidad": "Hardware",
        "carreras": ["ISC"]
    },
    "C.P. Sonia Vázquez Alcántara": {
        "matricula": "PROF007",
        "email": "sonia.vazquez@tesji.edu.mx",
        "especialidad": "Ética",
        "carreras": ["ISC", "II", "IM"]
    },
    "Ing. José Lucio Hernández Noguez": {
        "matricula": "PROF008",
        "email": "jose.hernandez@tesji.edu.mx",
        "especialidad": "Programación Avanzada",
        "carreras": ["ISC"]
    }
}

# Estudiantes reales por grupo
ESTUDIANTES_GRUPOS = {
    "N1": [  # Grupo 3101
        "202323069", "202323274", "202323221", "202323699", "202323108",
        "202323090", "202323080", "202323006", "202323116", "202323288",
        "202323306", "202323370", "202323261", "202323695", "202323251",
        "202323346", "202323100", "202323027", "202323193", "202323083",
        "202323053", "202323009", "202323376", "202323334", "202323070",
        "202323130", "202323118", "202323117", "202323106", "202323746",
        "202323399", "202323098", "202323045", "202323671", "202323880",
        "202323103"
    ],
    "N2": [  # Grupo 3102
        "202323734", "202323768", "202323367", "202323728", "202323883",
        "202323830", "202323377", "202323352", "202323652", "202323737",
        "202323458", "202323762", "202323355", "202323750", "202323315",
        "202323732", "202323445", "202323403", "202323394", "202323424",
        "202323752", "202323881", "202323877", "202323850", "202323885",
        "202323725", "202323386", "202323446", "202323891", "202323887",
        "202323774", "202323464", "202323092", "202323112", "202323723",
        "202323413", "202323892", "202323730", "202323843", "202323896",
        "202323758", "202323398", "202323420", "202323382", "202323449"
    ]
}

def create_extended_tables(db_path="tesji_rfid_system.db"):
    """Crea las tablas extendidas para horarios y asignaciones"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabla de salones
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS salones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        capacidad INTEGER DEFAULT 30,
        tipo TEXT DEFAULT 'Aula',
        activo BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabla de horarios detallados
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS horarios_detallados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        materia_id INTEGER NOT NULL,
        grupo_id INTEGER NOT NULL,
        salon_id INTEGER NOT NULL,
        dia_semana TEXT NOT NULL,
        hora_inicio TEXT NOT NULL,
        hora_fin TEXT NOT NULL,
        tipo_clase TEXT DEFAULT 'Teoría',
        activo BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (materia_id) REFERENCES materias (id),
        FOREIGN KEY (grupo_id) REFERENCES grupos (id),
        FOREIGN KEY (salon_id) REFERENCES salones (id)
    )
    ''')
    
    # Tabla de asignaciones maestro-materia-grupo
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS asignaciones_maestro (
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
    
    # Actualizar tabla de grupos para incluir más información
    try:
        cursor.execute('ALTER TABLE grupos ADD COLUMN salon TEXT')
        cursor.execute('ALTER TABLE grupos ADD COLUMN turno TEXT')
        print("✅ Columnas salon y turno agregadas a grupos")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️ Columnas salon y turno ya existen en grupos")
        else:
            print(f"⚠️ Error agregando columnas: {e}")
    
    # Actualizar tabla de materias para incluir más información
    try:
        cursor.execute('ALTER TABLE materias ADD COLUMN horas_teoria INTEGER DEFAULT 0')
        cursor.execute('ALTER TABLE materias ADD COLUMN horas_practica INTEGER DEFAULT 0')
        cursor.execute('ALTER TABLE materias ADD COLUMN clave_oficial TEXT')
        print("✅ Columnas de horas y clave agregadas a materias")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️ Columnas de horas ya existen en materias")
        else:
            print(f"⚠️ Error agregando columnas: {e}")
    
    # Actualizar tabla de usuarios para incluir especialidad
    try:
        cursor.execute('ALTER TABLE usuarios ADD COLUMN especialidad TEXT')
        print("✅ Columna especialidad agregada a usuarios")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️ Columna especialidad ya existe en usuarios")
        else:
            print(f"⚠️ Error agregando especialidad: {e}")
    
    conn.commit()
    conn.close()
    print("✅ Tablas extendidas creadas/actualizadas exitosamente")

def populate_salones(db_path="tesji_rfid_system.db"):
    """Pobla la tabla de salones"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    salones = [
        ("N1", 35, "Aula"),
        ("N2", 35, "Aula"), 
        ("LAB-1", 25, "Laboratorio"),
        ("LAB-2", 25, "Laboratorio"),
        ("A-101", 40, "Aula"),
        ("A-102", 40, "Aula"),
        ("A-103", 40, "Aula")
    ]
    
    for salon_data in salones:
        cursor.execute('''
        INSERT OR IGNORE INTO salones (nombre, capacidad, tipo)
        VALUES (?, ?, ?)
        ''', salon_data)
    
    conn.commit()
    conn.close()
    print("✅ Salones poblados exitosamente")

def populate_maestros(db_path="tesji_rfid_system.db"):
    """Pobla la tabla de maestros"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Obtener carrera ISC
    cursor.execute('SELECT id FROM carreras WHERE codigo = "ISC"')
    carrera_isc = cursor.fetchone()
    if not carrera_isc:
        print("❌ Error: Carrera ISC no encontrada")
        return
    carrera_isc_id = carrera_isc[0]
    
    for nombre_completo, datos in MAESTROS_DATA.items():
        # Verificar si ya existe
        cursor.execute('SELECT id FROM usuarios WHERE matricula = ?', (datos['matricula'],))
        if cursor.fetchone():
            print(f"ℹ️ Maestro {datos['matricula']} ya existe")
            continue
        
        # Crear hash de contraseña simple
        import hashlib
        import secrets
        password = "123456"  # Contraseña por defecto
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        password_hash_final = f"{salt}:{password_hash}"
        
        cursor.execute('''
        INSERT INTO usuarios (
            nombre_completo, matricula, email, password_hash, rol, 
            carrera_id, especialidad, activo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            nombre_completo,
            datos['matricula'],
            datos['email'],
            password_hash_final,
            'teacher',
            carrera_isc_id,
            datos['especialidad'],
            True
        ))
        
        print(f"✅ Maestro creado: {nombre_completo} ({datos['matricula']})")
    
    conn.commit()
    conn.close()
    print("✅ Maestros poblados exitosamente")

def populate_grupos_horarios(db_path="tesji_rfid_system.db"):
    """Pobla grupos, materias y horarios"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Obtener carrera ISC
    cursor.execute('SELECT id FROM carreras WHERE codigo = "ISC"')
    carrera_isc = cursor.fetchone()
    if not carrera_isc:
        print("❌ Error: Carrera ISC no encontrada")
        return
    carrera_isc_id = carrera_isc[0]
    
    for grupo_codigo, grupo_data in GRUPOS_HORARIOS.items():
        print(f"📚 Procesando {grupo_data['nombre']}...")
        
        # Crear/actualizar grupo
        cursor.execute('''
        INSERT OR REPLACE INTO grupos (
            nombre, carrera_id, semestre, periodo, salon, turno, activo
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            grupo_data['nombre'],
            carrera_isc_id,
            grupo_data['semestre'],
            "2024-2025",
            grupo_data['salon'],
            grupo_data['turno'],
            True
        ))
        
        # Obtener ID del grupo
        cursor.execute('SELECT id FROM grupos WHERE nombre = ?', (grupo_data['nombre'],))
        grupo_id = cursor.fetchone()[0]
        
        # Obtener ID del salón
        cursor.execute('SELECT id FROM salones WHERE nombre = ?', (grupo_data['salon'],))
        salon_result = cursor.fetchone()
        if not salon_result:
            print(f"⚠️ Salón {grupo_data['salon']} no encontrado")
            continue
        salon_id = salon_result[0]
        
        # Procesar materias del grupo
        for materia_data in grupo_data['materias']:
            # Crear/actualizar materia
            cursor.execute('''
            INSERT OR REPLACE INTO materias (
                nombre, codigo, carrera_id, semestre, creditos, 
                horas_teoria, horas_practica, clave_oficial, activa
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                materia_data['nombre'],
                materia_data['clave'],
                carrera_isc_id,
                grupo_data['semestre'],
                materia_data['creditos'],
                materia_data['ht'],
                materia_data['hp'],
                materia_data['clave'],
                True
            ))
            
            # Obtener ID de la materia
            cursor.execute('SELECT id FROM materias WHERE clave_oficial = ?', (materia_data['clave'],))
            materia_id = cursor.fetchone()[0]
            
            # Buscar maestro
            cursor.execute('SELECT id FROM usuarios WHERE nombre_completo = ? AND rol = "teacher"', 
                         (materia_data['docente'],))
            maestro_result = cursor.fetchone()
            if not maestro_result:
                print(f"⚠️ Maestro {materia_data['docente']} no encontrado")
                continue
            maestro_id = maestro_result[0]
            
            # Crear asignación maestro-materia-grupo
            cursor.execute('''
            INSERT OR REPLACE INTO asignaciones_maestro (
                maestro_id, materia_id, grupo_id, periodo, activa
            ) VALUES (?, ?, ?, ?, ?)
            ''', (maestro_id, materia_id, grupo_id, "2024-2025", True))
            
            # Crear horarios detallados
            for horario in materia_data['horarios']:
                cursor.execute('''
                INSERT OR REPLACE INTO horarios_detallados (
                    materia_id, grupo_id, salon_id, dia_semana, 
                    hora_inicio, hora_fin, tipo_clase, activo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    materia_id, grupo_id, salon_id,
                    horario['dia'],
                    horario['hora_inicio'],
                    horario['hora_fin'],
                    'Teoría' if materia_data['ht'] > 0 else 'Práctica',
                    True
                ))
            
            print(f"   ✅ {materia_data['nombre']} - {materia_data['docente']}")
    
    conn.commit()
    conn.close()
    print("✅ Grupos y horarios poblados exitosamente")

def assign_students_to_groups(db_path="tesji_rfid_system.db"):
    """Asigna estudiantes existentes a sus grupos correspondientes"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("👥 Asignando estudiantes reales a grupos...")
    
    for grupo_nombre, matriculas in ESTUDIANTES_GRUPOS.items():
        if not matriculas:
            print(f"⚠️ No hay matrículas para el grupo {grupo_nombre}")
            continue
            
        # Obtener ID del grupo
        cursor.execute('SELECT id FROM grupos WHERE nombre LIKE ?', (f"%{grupo_nombre}%",))
        grupo_result = cursor.fetchone()
        if not grupo_result:
            print(f"❌ Grupo {grupo_nombre} no encontrado")
            continue
        grupo_id = grupo_result[0]
        
        print(f"📚 Procesando grupo {grupo_nombre} (ID: {grupo_id})")
        
        asignados = 0
        for matricula in matriculas:
            # Buscar estudiante por matrícula
            cursor.execute('SELECT id FROM usuarios WHERE matricula = ? AND rol = "student"', (matricula,))
            estudiante = cursor.fetchone()
            
            if estudiante:
                # Asignar al grupo
                cursor.execute('UPDATE usuarios SET grupo_id = ? WHERE id = ?', (grupo_id, estudiante[0]))
                asignados += 1
                print(f"   ✅ {matricula} asignado al grupo {grupo_nombre}")
            else:
                print(f"   ⚠️ Estudiante {matricula} no encontrado en la base de datos")
        
        print(f"   📊 Total asignados al grupo {grupo_nombre}: {asignados}")
    
    conn.commit()
    conn.close()
    print("✅ Asignación de estudiantes completada")

def generate_report(db_path="tesji_rfid_system.db"):
    """Genera un reporte del sistema configurado"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📊 REPORTE DEL SISTEMA DE HORARIOS TESJI")
    print("="*80)
    
    # Estadísticas generales
    cursor.execute('SELECT COUNT(*) FROM grupos WHERE activo = TRUE')
    total_grupos = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM materias WHERE activa = TRUE')
    total_materias = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "teacher"')
    total_maestros = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM horarios_detallados WHERE activo = TRUE')
    total_horarios = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM asignaciones_maestro WHERE activa = TRUE')
    total_asignaciones = cursor.fetchone()[0]
    
    print(f"\n📈 ESTADÍSTICAS GENERALES:")
    print(f"   👥 Grupos activos: {total_grupos}")
    print(f"   📚 Materias activas: {total_materias}")
    print(f"   👨‍🏫 Maestros registrados: {total_maestros}")
    print(f"   ⏰ Horarios configurados: {total_horarios}")
    print(f"   📝 Asignaciones activas: {total_asignaciones}")
    
    # Detalle por grupo
    print(f"\n📋 DETALLE POR GRUPO:")
    cursor.execute('''
    SELECT g.nombre, g.salon, g.turno, COUNT(hd.id) as total_horarios
    FROM grupos g
    LEFT JOIN horarios_detallados hd ON g.id = hd.grupo_id
    WHERE g.activo = TRUE
    GROUP BY g.id
    ORDER BY g.nombre
    ''')
    
    grupos = cursor.fetchall()
    for nombre, salon, turno, horarios_count in grupos:
        print(f"   📚 {nombre}")
        print(f"      🏢 Salón: {salon}")
        print(f"      🌅 Turno: {turno}")
        print(f"      ⏰ Horarios: {horarios_count}")
    
    # Maestros y sus asignaciones
    print(f"\n👨‍🏫 MAESTROS Y SUS ASIGNACIONES:")
    cursor.execute('''
    SELECT u.nombre_completo, u.matricula, u.especialidad, COUNT(am.id) as total_asignaciones
    FROM usuarios u
    LEFT JOIN asignaciones_maestro am ON u.id = am.maestro_id AND am.activa = TRUE
    WHERE u.rol = "teacher"
    GROUP BY u.id
    ORDER BY u.nombre_completo
    ''')
    
    maestros = cursor.fetchall()
    for nombre, matricula, especialidad, asignaciones_count in maestros:
        print(f"   👨‍🏫 {nombre}")
        print(f"      🆔 {matricula}")
        print(f"      🎯 {especialidad}")
        print(f"      📝 Asignaciones: {asignaciones_count}")
    
    conn.close()
    print("="*80)

def main():
    print("🏫 CONFIGURADOR DE HORARIOS Y GRUPOS TESJI")
    print("="*60)
    
    try:
        # 1. Crear tablas extendidas
        create_extended_tables()
        
        # 2. Poblar salones
        populate_salones()
        
        # 3. Poblar maestros
        populate_maestros()
        
        # 4. Poblar grupos y horarios
        populate_grupos_horarios()

        # 5. Asignar estudiantes a grupos
        assign_students_to_groups()
        
        # 6. Generar reporte
        generate_report()
        
        print("\n🎉 CONFIGURACIÓN DE HORARIOS COMPLETADA")
        print("✅ El sistema TESJI está listo con horarios reales")
        print("\n📋 CREDENCIALES DE MAESTROS:")
        print("   Usuario: PROF001, PROF002, etc.")
        print("   Contraseña: 123456 (para todos)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
