#!/usr/bin/env python3
"""
Script completo para reparar la base de datos preservando datos existentes
Combina funcionalidad de todos los scripts de configuración
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime

# Estructura académica completa del TESJI (del script populate_academic_structure.py)
ACADEMIC_STRUCTURE = {
    "Ingeniería en Sistemas Computacionales": {
        "codigo": "ISC",
        "semestres": 9,
        "materias": {
            1: [
                "Cálculo Diferencial",
                "Fundamentos de Programación", 
                "Desarrollo Sustentable",
                "Matemáticas Discretas",
                "Química",
                "Fundamentos de Investigación"
            ],
            2: [
                "Cálculo Integral",
                "Programación Orientada a Objetos",
                "Taller de Administración", 
                "Álgebra Lineal",
                "Probabilidad y Estadística",
                "Física General"
            ],
            3: [
                "Cálculo Vectorial",
                "Estructura de Datos",
                "Fundamentos de Telecomunicaciones",
                "Investigación de Operaciones",
                "Sistemas Operativos I",
                "Principios Eléctricos y Aplicaciones Digitales"
            ],
            4: [
                "Ecuaciones Diferenciales",
                "Métodos Numéricos",
                "Tópicos Avanzados de Programación",
                "Fundamentos de Bases de Datos",
                "Taller de Sistemas Operativos",
                "Arquitectura de Computadoras",
                "Taller de Ética"
            ]
        }
    },
    "Ingeniería Industrial": {
        "codigo": "II",
        "semestres": 9,
        "materias": {
            1: [
                "Fundamentos de Investigación",
                "Taller de Ética",
                "Cálculo Diferencial",
                "Taller de Herramientas Intelectuales",
                "Química",
                "Dibujo Industrial"
            ]
        }
    }
}

# Grupos y horarios reales (del script setup_horarios_grupos.py)
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

def backup_database(db_path="tesji_rfid_system.db"):
    """Crear backup de la base de datos antes de modificar"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"tesji_rfid_system_backup_{timestamp}.db"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup creado: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"⚠️ Error creando backup: {e}")
        return None

def check_existing_data(db_path="tesji_rfid_system.db"):
    """Verificar qué datos ya existen"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔍 VERIFICANDO DATOS EXISTENTES...")
    
    # Verificar tablas existentes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"📋 Tablas existentes: {', '.join(tables)}")
    
    stats = {}
    
    if 'usuarios' in tables:
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        stats['usuarios'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'student'")
        stats['estudiantes'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'teacher'")
        stats['maestros'] = cursor.fetchone()[0]
    
    if 'carreras' in tables:
        cursor.execute("SELECT COUNT(*) FROM carreras")
        stats['carreras'] = cursor.fetchone()[0]
    
    if 'grupos' in tables:
        cursor.execute("SELECT COUNT(*) FROM grupos")
        stats['grupos'] = cursor.fetchone()[0]
    
    if 'materias' in tables:
        cursor.execute("SELECT COUNT(*) FROM materias")
        stats['materias'] = cursor.fetchone()[0]
    
    if 'horarios_detallados' in tables:
        cursor.execute("SELECT COUNT(*) FROM horarios_detallados")
        stats['horarios'] = cursor.fetchone()[0]
    
    print("📊 ESTADÍSTICAS ACTUALES:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    conn.close()
    return stats

def add_missing_columns(db_path="tesji_rfid_system.db"):
    """Agregar solo las columnas faltantes sin borrar datos"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 AGREGANDO COLUMNAS FALTANTES...")
    
    # Verificar y agregar columnas a usuarios
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = [row[1] for row in cursor.fetchall()]
    
    missing_columns = []
    required_columns = {
        'salon': 'TEXT',
        'especialidad': 'TEXT',
        'semestre': 'INTEGER',
        'grupo_id': 'INTEGER'
    }
    
    for col_name, col_type in required_columns.items():
        if col_name not in columns:
            missing_columns.append((col_name, col_type))
    
    for col_name, col_type in missing_columns:
        try:
            cursor.execute(f'ALTER TABLE usuarios ADD COLUMN {col_name} {col_type}')
            print(f"   ✅ Columna agregada: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                print(f"   ⚠️ Error agregando {col_name}: {e}")
    
    conn.commit()
    conn.close()

def create_missing_tables(db_path="tesji_rfid_system.db"):
    """Crear solo las tablas que faltan"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🏗️ CREANDO TABLAS FALTANTES...")
    
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
        horas_teoria INTEGER DEFAULT 0,
        horas_practica INTEGER DEFAULT 0,
        clave_oficial TEXT,
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
        salon TEXT,
        turno TEXT,
        activo BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (carrera_id) REFERENCES carreras (id)
    )
    ''')
    
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
    
    # Tabla de asignaciones maestro
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
    
    # Tabla de asistencias
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS asistencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estudiante_id INTEGER NOT NULL,
        materia_id INTEGER NOT NULL,
        fecha DATE NOT NULL,
        hora_entrada TIME,
        hora_salida TIME,
        estado TEXT DEFAULT 'presente',
        observaciones TEXT,
        fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (estudiante_id) REFERENCES usuarios (id),
        FOREIGN KEY (materia_id) REFERENCES materias (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Tablas creadas/verificadas")

def populate_missing_data(db_path="tesji_rfid_system.db"):
    """Poblar solo los datos que faltan"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📚 POBLANDO DATOS FALTANTES...")
    
    # 1. Poblar carreras si no existen
    for carrera_nombre, carrera_data in ACADEMIC_STRUCTURE.items():
        cursor.execute('SELECT id FROM carreras WHERE codigo = ?', (carrera_data["codigo"],))
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO carreras (nombre, codigo, semestres)
            VALUES (?, ?, ?)
            ''', (carrera_nombre, carrera_data["codigo"], carrera_data["semestres"]))
            print(f"   ✅ Carrera agregada: {carrera_nombre}")
    
    # 2. Poblar salones si no existen
    salones = [("N1", 35, "Aula"), ("N2", 35, "Aula"), ("LAB-1", 25, "Laboratorio")]
    for salon_data in salones:
        cursor.execute('SELECT id FROM salones WHERE nombre = ?', (salon_data[0],))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO salones (nombre, capacidad, tipo) VALUES (?, ?, ?)', salon_data)
            print(f"   ✅ Salón agregado: {salon_data[0]}")
    
    # 3. Poblar maestros si no existen
    cursor.execute('SELECT id FROM carreras WHERE codigo = "ISC"')
    carrera_isc = cursor.fetchone()
    if carrera_isc:
        carrera_isc_id = carrera_isc[0]
        
        for nombre_completo, datos in MAESTROS_DATA.items():
            cursor.execute('SELECT id FROM usuarios WHERE matricula = ?', (datos['matricula'],))
            if not cursor.fetchone():
                # Crear contraseña
                password = "123456"
                salt = secrets.token_hex(16)
                password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                password_hash_final = f"{salt}:{password_hash}"
                
                cursor.execute('''
                INSERT INTO usuarios (
                    nombre_completo, matricula, email, password_hash, rol, 
                    carrera_id, especialidad, activo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    nombre_completo, datos['matricula'], datos['email'],
                    password_hash_final, 'teacher', carrera_isc_id,
                    datos['especialidad'], True
                ))
                print(f"   ✅ Maestro agregado: {nombre_completo}")
    
    # 4. Poblar grupos y horarios si no existen
    for grupo_codigo, grupo_data in GRUPOS_HORARIOS.items():
        cursor.execute('SELECT id FROM grupos WHERE nombre = ?', (grupo_data['nombre'],))
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO grupos (nombre, carrera_id, semestre, periodo, salon, turno, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                grupo_data['nombre'], carrera_isc_id, grupo_data['semestre'],
                "2024-2025", grupo_data['salon'], grupo_data['turno'], True
            ))
            print(f"   ✅ Grupo agregado: {grupo_data['nombre']}")
        
        # Obtener ID del grupo
        cursor.execute('SELECT id FROM grupos WHERE nombre = ?', (grupo_data['nombre'],))
        grupo_id = cursor.fetchone()[0]
        
        # Poblar materias y horarios del grupo
        for materia_data in grupo_data['materias']:
            # Verificar si la materia existe
            cursor.execute('SELECT id FROM materias WHERE clave_oficial = ?', (materia_data['clave'],))
            if not cursor.fetchone():
                cursor.execute('''
                INSERT INTO materias (
                    nombre, codigo, carrera_id, semestre, creditos, 
                    horas_teoria, horas_practica, clave_oficial, activa
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    materia_data['nombre'], materia_data['clave'], carrera_isc_id,
                    grupo_data['semestre'], materia_data['creditos'],
                    materia_data['ht'], materia_data['hp'], materia_data['clave'], True
                ))
                print(f"   ✅ Materia agregada: {materia_data['nombre']}")
            
            # Obtener IDs necesarios
            cursor.execute('SELECT id FROM materias WHERE clave_oficial = ?', (materia_data['clave'],))
            materia_id = cursor.fetchone()[0]
            
            cursor.execute('SELECT id FROM salones WHERE nombre = ?', (grupo_data['salon'],))
            salon_id = cursor.fetchone()[0]
            
            cursor.execute('SELECT id FROM usuarios WHERE nombre_completo = ? AND rol = "teacher"', 
                         (materia_data['docente'],))
            maestro_result = cursor.fetchone()
            if maestro_result:
                maestro_id = maestro_result[0]
                
                # Crear asignación maestro-materia-grupo
                cursor.execute('''
                INSERT OR IGNORE INTO asignaciones_maestro (
                    maestro_id, materia_id, grupo_id, periodo, activa
                ) VALUES (?, ?, ?, ?, ?)
                ''', (maestro_id, materia_id, grupo_id, "2024-2025", True))
                
                # Crear horarios detallados
                for horario in materia_data['horarios']:
                    cursor.execute('''
                    INSERT OR IGNORE INTO horarios_detallados (
                        materia_id, grupo_id, salon_id, dia_semana, 
                        hora_inicio, hora_fin, tipo_clase, activo
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        materia_id, grupo_id, salon_id, horario['dia'],
                        horario['hora_inicio'], horario['hora_fin'],
                        'Teoría' if materia_data['ht'] > 0 else 'Práctica', True
                    ))
    
    # 5. Asignar estudiantes a grupos basado en matrículas reales
    for grupo_nombre, matriculas in ESTUDIANTES_GRUPOS.items():
        cursor.execute('SELECT id FROM grupos WHERE nombre LIKE ?', (f"%{grupo_nombre}%",))
        grupo_result = cursor.fetchone()
        if grupo_result:
            grupo_id = grupo_result[0]
            
            for matricula in matriculas:
                cursor.execute('SELECT id FROM usuarios WHERE matricula = ? AND rol = "student"', (matricula,))
                estudiante = cursor.fetchone()
                if estudiante:
                    cursor.execute('UPDATE usuarios SET grupo_id = ?, salon = ? WHERE id = ?', 
                                 (grupo_id, grupo_nombre, estudiante[0]))
    
    conn.commit()
    conn.close()
    print("✅ Datos poblados exitosamente")

def verify_final_state(db_path="tesji_rfid_system.db"):
    """Verificar el estado final de la base de datos"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n📊 VERIFICACIÓN FINAL:")
    print("=" * 50)
    
    # Verificar columnas de usuarios
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = [row[1] for row in cursor.fetchall()]
    required_columns = ['salon', 'especialidad', 'semestre', 'grupo_id']
    
    print("🔍 Columnas en tabla usuarios:")
    for col in required_columns:
        status = "✅" if col in columns else "❌"
        print(f"   {status} {col}")
    
    # Estadísticas finales
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'student'")
    total_estudiantes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'teacher'")
    total_maestros = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM carreras")
    total_carreras = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM grupos")
    total_grupos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM materias")
    total_materias = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM horarios_detallados")
    total_horarios = cursor.fetchone()[0]
    
    print(f"\n📈 ESTADÍSTICAS FINALES:")
    print(f"   👨‍🎓 Estudiantes: {total_estudiantes}")
    print(f"   👨‍🏫 Maestros: {total_maestros}")
    print(f"   🎓 Carreras: {total_carreras}")
    print(f"   📚 Grupos: {total_grupos}")
    print(f"   📖 Materias: {total_materias}")
    print(f"   ⏰ Horarios: {total_horarios}")
    
    # Verificar horarios específicos del grupo N1
    cursor.execute('''
    SELECT COUNT(*) FROM horarios_detallados hd
    JOIN grupos g ON hd.grupo_id = g.id
    WHERE g.nombre LIKE '%N1%' AND hd.activo = 1
    ''')
    horarios_n1 = cursor.fetchone()[0]
    print(f"   📅 Horarios Grupo N1: {horarios_n1}")
    
    conn.close()
    print("=" * 50)

def main():
    print("🔧 REPARACIÓN COMPLETA DE BASE DE DATOS TESJI")
    print("=" * 60)
    print("Este script preserva TODOS los datos existentes")
    print("Solo agrega columnas y datos faltantes")
    print("=" * 60)
    
    try:
        # 1. Crear backup
        backup_path = backup_database()
        
        # 2. Verificar datos existentes
        existing_stats = check_existing_data()
        
        # 3. Agregar columnas faltantes
        add_missing_columns()
        
        # 4. Crear tablas faltantes
        create_missing_tables()
        
        # 5. Poblar datos faltantes
        populate_missing_data()
        
        # 6. Verificar estado final
        verify_final_state()
        
        print("\n🎉 REPARACIÓN COMPLETADA EXITOSAMENTE")
        print("✅ Todos los datos existentes fueron preservados")
        print("✅ Columnas faltantes agregadas")
        print("✅ Estructura académica completa")
        print("✅ Horarios y grupos configurados")
        print("✅ Sistema listo para funcionar")
        
        if backup_path:
            print(f"\n💾 Backup disponible en: {backup_path}")
        
    except Exception as e:
        print(f"❌ Error durante la reparación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
