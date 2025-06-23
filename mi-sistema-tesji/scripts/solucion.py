#!/usr/bin/env python3
"""
Script FINAL para configurar TESJI con TODOS los datos reales
Basado en la información exacta proporcionada
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime

# DATOS REALES DE ESTUDIANTES POR GRUPO (de los archivos existentes)
GRUPO_N1_ESTUDIANTES = [
    "202323069", "202323274", "202323221", "202323699", "202323108",
    "202323090", "202323080", "202323006", "202323116", "202323288",
    "202323306", "202323370", "202323261", "202323695", "202323251",
    "202323346", "202323100", "202323027", "202323193", "202323083",
    "202323053", "202323009", "202323376", "202323334", "202323070",
    "202323130", "202323118", "202323117", "202323106", "202323746",
    "202323399", "202323098", "202323045", "202323671", "202323880",
    "202323103"
]

GRUPO_N2_ESTUDIANTES = [
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

# MAESTROS REALES (de los archivos existentes)
MAESTROS_REALES = {
    "Ing. Rodolfo Guadalupe Alcántara Rosales": {
        "matricula": "PROF001",
        "email": "rodolfo.alcantara@tesji.edu.mx",
        "especialidad": "Matemáticas",
        "password": "123456"
    },
    "Lic. Juan Alberto Martínez Zamora": {
        "matricula": "PROF002", 
        "email": "juan.martinez@tesji.edu.mx",
        "especialidad": "Métodos Numéricos",
        "password": "123456"
    },
    "Víctor David Maya Arce": {
        "matricula": "PROF003",
        "email": "victor.maya@tesji.edu.mx", 
        "especialidad": "Programación",
        "password": "123456"
    },
    "Mtra. Yadira Esther Jiménez Pérez": {
        "matricula": "PROF004",
        "email": "yadira.jimenez@tesji.edu.mx",
        "especialidad": "Base de Datos",
        "password": "123456"
    },
    "Mtro. Anselmo Martínez Montalvo": {
        "matricula": "PROF005",
        "email": "anselmo.martinez@tesji.edu.mx",
        "especialidad": "Sistemas Operativos", 
        "password": "123456"
    },
    "Ing. Alfredo Aguilar López": {
        "matricula": "PROF006",
        "email": "alfredo.aguilar@tesji.edu.mx",
        "especialidad": "Hardware",
        "password": "123456"
    },
    "C.P. Sonia Vázquez Alcántara": {
        "matricula": "PROF007",
        "email": "sonia.vazquez@tesji.edu.mx",
        "especialidad": "Ética",
        "password": "123456"
    },
    "Ing. José Lucio Hernández Noguez": {
        "matricula": "PROF008",
        "email": "jose.hernandez@tesji.edu.mx",
        "especialidad": "Programación Avanzada",
        "password": "123456"
    }
}

# HORARIOS REALES DEL SALÓN N1 (de los archivos existentes)
HORARIOS_N1 = {
    "Lunes": [
        {"materia": "Métodos Numéricos", "codigo": "SCC-1017", "hora_inicio": "07:00", "hora_fin": "09:00", "maestro": "Lic. Juan Alberto Martínez Zamora", "creditos": 4},
        {"materia": "Ecuaciones Diferenciales", "codigo": "ACF-0905", "hora_inicio": "09:00", "hora_fin": "12:00", "maestro": "Ing. Rodolfo Guadalupe Alcántara Rosales", "creditos": 5},
        {"materia": "Fundamentos de Base de Datos", "codigo": "AEF-1031", "hora_inicio": "15:00", "hora_fin": "18:00", "maestro": "Víctor David Maya Arce", "creditos": 5}
    ],
    "Martes": [
        {"materia": "Arquitectura de Computadoras", "codigo": "SCD-1003", "hora_inicio": "11:00", "hora_fin": "13:00", "maestro": "Ing. Alfredo Aguilar López", "creditos": 5},
        {"materia": "Tópicos Avanzados de Programación", "codigo": "SCD-1027", "hora_inicio": "13:00", "hora_fin": "15:00", "maestro": "Ing. José Lucio Hernández Noguez", "creditos": 5}
    ],
    "Miércoles": [
        {"materia": "Métodos Numéricos", "codigo": "SCC-1017", "hora_inicio": "07:00", "hora_fin": "09:00", "maestro": "Lic. Juan Alberto Martínez Zamora", "creditos": 4},
        {"materia": "Ecuaciones Diferenciales", "codigo": "ACF-0905", "hora_inicio": "11:00", "hora_fin": "13:00", "maestro": "Ing. Rodolfo Guadalupe Alcántara Rosales", "creditos": 5},
        {"materia": "Taller de Sistemas Operativos", "codigo": "SCA-1026", "hora_inicio": "07:00", "hora_fin": "09:00", "maestro": "Mtro. Anselmo Martínez Montalvo", "creditos": 4},
        {"materia": "Fundamentos de Base de Datos", "codigo": "AEF-1031", "hora_inicio": "11:00", "hora_fin": "13:00", "maestro": "Mtra. Yadira Esther Jiménez Pérez", "creditos": 5}
    ],
    "Jueves": [
        {"materia": "Taller de Ética", "codigo": "ACA-0907", "hora_inicio": "09:00", "hora_fin": "11:00", "maestro": "C.P. Sonia Vázquez Alcántara", "creditos": 4},
        {"materia": "Tópicos Avanzados de Programación", "codigo": "SCD-1027", "hora_inicio": "14:00", "hora_fin": "17:00", "maestro": "Víctor David Maya Arce", "creditos": 5}
    ],
    "Viernes": [
        {"materia": "Taller de Sistemas Operativos", "codigo": "SCA-1026", "hora_inicio": "07:00", "hora_fin": "09:00", "maestro": "Mtro. Anselmo Martínez Montalvo", "creditos": 4},
        {"materia": "Taller de Ética", "codigo": "ACA-0907", "hora_inicio": "09:00", "hora_fin": "11:00", "maestro": "C.P. Sonia Vázquez Alcántara", "creditos": 4},
        {"materia": "Arquitectura de Computadoras", "codigo": "SCD-1003", "hora_inicio": "12:00", "hora_fin": "15:00", "maestro": "Ing. Alfredo Aguilar López", "creditos": 5}
    ]
}

# HORARIOS REALES DEL SALÓN N2 (de los archivos existentes)
HORARIOS_N2 = {
    "Lunes": [
        {"materia": "Métodos Numéricos", "codigo": "SCC-1017", "hora_inicio": "11:00", "hora_fin": "13:00", "maestro": "Lic. Juan Alberto Martínez Zamora", "creditos": 4},
        {"materia": "Tópicos Avanzados de Programación", "codigo": "SCD-1027", "hora_inicio": "12:00", "hora_fin": "15:00", "maestro": "Víctor David Maya Arce", "creditos": 5},
        {"materia": "Ecuaciones Diferenciales", "codigo": "ACF-0905", "hora_inicio": "13:00", "hora_fin": "15:00", "maestro": "Ing. Rodolfo Guadalupe Alcántara Rosales", "creditos": 5},
        {"materia": "Fundamentos de Base de Datos", "codigo": "AEF-1031", "hora_inicio": "11:00", "hora_fin": "13:00", "maestro": "Mtra. Yadira Esther Jiménez Pérez", "creditos": 5},
        {"materia": "Taller de Sistemas Operativos", "codigo": "SCA-1026", "hora_inicio": "07:00", "hora_fin": "09:00", "maestro": "Mtro. Anselmo Martínez Montalvo", "creditos": 4},
        {"materia": "Arquitectura de Computadoras", "codigo": "SCD-1003", "hora_inicio": "13:00", "hora_fin": "15:00", "maestro": "Ing. Alfredo Aguilar López", "creditos": 5},
        {"materia": "Taller de Ética", "codigo": "ACA-0907", "hora_inicio": "10:00", "hora_fin": "12:00", "maestro": "C.P. Sonia Vázquez Alcántara", "creditos": 4}
    ],
    "Miércoles": [
        {"materia": "Métodos Numéricos", "codigo": "SCC-1017", "hora_inicio": "11:00", "hora_fin": "13:00", "maestro": "Lic. Juan Alberto Martínez Zamora", "creditos": 4},
        {"materia": "Tópicos Avanzados de Programación", "codigo": "SCD-1027", "hora_inicio": "09:00", "hora_fin": "11:00", "maestro": "Víctor David Maya Arce", "creditos": 5},
        {"materia": "Ecuaciones Diferenciales", "codigo": "ACF-0905", "hora_inicio": "12:00", "hora_fin": "15:00", "maestro": "Ing. Rodolfo Guadalupe Alcántara Rosales", "creditos": 5},
        {"materia": "Fundamentos de Base de Datos", "codigo": "AEF-1031", "hora_inicio": "08:00", "hora_fin": "11:00", "maestro": "Mtra. Yadira Esther Jiménez Pérez", "creditos": 5},
        {"materia": "Taller de Sistemas Operativos", "codigo": "SCA-1026", "hora_inicio": "07:00", "hora_fin": "09:00", "maestro": "Mtro. Anselmo Martínez Montalvo", "creditos": 4},
        {"materia": "Arquitectura de Computadoras", "codigo": "SCD-1003", "hora_inicio": "09:00", "hora_fin": "12:00", "maestro": "Ing. Alfredo Aguilar López", "creditos": 5},
        {"materia": "Taller de Ética", "codigo": "ACA-0907", "hora_inicio": "13:00", "hora_fin": "15:00", "maestro": "C.P. Sonia Vázquez Alcántara", "creditos": 4}
    ]
}

# CARRERAS REALES DEL TESJI (de los archivos existentes)
CARRERAS_TESJI = [
    ("Ingeniería en Sistemas Computacionales", "ISC", 9),
    ("Ingeniería Industrial", "II", 9),
    ("Ingeniería Mecatrónica", "IM", 9),
    ("Ingeniería Civil", "IC", 9),
    ("Licenciatura en Administración", "LA", 8),
    ("Ingeniería Química", "IQ", 9),
    ("Ingeniería en Logística", "IL", 9),
    ("Ingeniería en Tecnologías de la Información y Comunicaciones", "ITIC", 9)
]

def hash_password(password: str) -> str:
    """Genera hash de contraseña"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def setup_database():
    """Configura la base de datos completa"""
    conn = sqlite3.connect('tesji_rfid_system.db')
    cursor = conn.cursor()
    
    print("🏗️ CONFIGURANDO BASE DE DATOS TESJI")
    print("=" * 50)
    
    # 1. CREAR TODAS LAS TABLAS
    print("📋 Creando tablas...")
    
    # Tabla carreras
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
    
    # Tabla usuarios
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
        semestre INTEGER DEFAULT 4,
        especialidad TEXT,
        salon TEXT,
        FOREIGN KEY (carrera_id) REFERENCES carreras (id),
        FOREIGN KEY (grupo_id) REFERENCES grupos (id)
    )
    ''')
    
    # Tabla grupos
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
    
    # Tabla materias
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
    
    # Tabla asistencias
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS asistencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
        presente BOOLEAN DEFAULT TRUE,
        usuario_id INTEGER,
        materia_id INTEGER,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    ''')
    
    # Tabla asignaciones maestro
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
    
    # Tabla horarios detallados
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
    
    print("✅ Tablas creadas")
    
    # 2. POBLAR CARRERAS
    print("🎓 Poblando carreras...")
    for nombre, codigo, semestres in CARRERAS_TESJI:
        cursor.execute('''
        INSERT OR IGNORE INTO carreras (nombre, codigo, semestres)
        VALUES (?, ?, ?)
        ''', (nombre, codigo, semestres))
    print("✅ Carreras pobladas")
    
    # 3. OBTENER CARRERA ISC
    cursor.execute('SELECT id FROM carreras WHERE codigo = "ISC"')
    carrera_isc_id = cursor.fetchone()[0]
    
    # 4. CREAR GRUPOS
    print("👥 Creando grupos...")
    cursor.execute('''
    INSERT OR IGNORE INTO grupos (nombre, carrera_id, semestre, periodo, salon, turno)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', ("Grupo N1", carrera_isc_id, 4, "2024-1", "N1", "Matutino"))
    
    cursor.execute('''
    INSERT OR IGNORE INTO grupos (nombre, carrera_id, semestre, periodo, salon, turno)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', ("Grupo N2", carrera_isc_id, 4, "2024-1", "N2", "Vespertino"))
    print("✅ Grupos creados")
    
    # 5. OBTENER IDs DE GRUPOS
    cursor.execute('SELECT id FROM grupos WHERE nombre = "Grupo N1"')
    grupo_n1_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM grupos WHERE nombre = "Grupo N2"')
    grupo_n2_id = cursor.fetchone()[0]
    
    # 6. CREAR MAESTROS
    print("👨‍🏫 Creando maestros...")
    for nombre, datos in MAESTROS_REALES.items():
        cursor.execute('SELECT id FROM usuarios WHERE matricula = ?', (datos['matricula'],))
        if not cursor.fetchone():
            password_hash = hash_password(datos['password'])
            cursor.execute('''
            INSERT INTO usuarios (
                nombre_completo, matricula, email, password_hash, rol, 
                carrera_id, especialidad, activo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nombre, datos['matricula'], datos['email'], password_hash,
                'teacher', carrera_isc_id, datos['especialidad'], True
            ))
    print("✅ Maestros creados")
    
    # 7. CREAR MATERIAS Y HORARIOS
    print("📚 Creando materias y horarios...")
    
    # Obtener todas las materias únicas de los horarios
    materias_unicas = set()
    for dia, clases in HORARIOS_N1.items():
        for clase in clases:
            materias_unicas.add((clase['materia'], clase['codigo'], clase['creditos']))
    
    for dia, clases in HORARIOS_N2.items():
        for clase in clases:
            materias_unicas.add((clase['materia'], clase['codigo'], clase['creditos']))
    
    # Crear materias
    for materia, codigo, creditos in materias_unicas:
        cursor.execute('''
        INSERT OR IGNORE INTO materias (
            nombre, carrera_id, semestre, codigo, creditos, clave_oficial, activa
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (materia, carrera_isc_id, 4, codigo, creditos, codigo, True))
    
    # Crear horarios para N1
    for dia, clases in HORARIOS_N1.items():
        for clase in clases:
            cursor.execute('SELECT id FROM materias WHERE clave_oficial = ?', (clase['codigo'],))
            materia_id = cursor.fetchone()[0]
            
            cursor.execute('''
            INSERT OR IGNORE INTO horarios_detallados (
                materia_id, grupo_id, dia_semana, hora_inicio, hora_fin, activo
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (materia_id, grupo_n1_id, dia, clase['hora_inicio'], clase['hora_fin'], True))
    
    # Crear horarios para N2
    for dia, clases in HORARIOS_N2.items():
        for clase in clases:
            cursor.execute('SELECT id FROM materias WHERE clave_oficial = ?', (clase['codigo'],))
            materia_id = cursor.fetchone()[0]
            
            cursor.execute('''
            INSERT OR IGNORE INTO horarios_detallados (
                materia_id, grupo_id, dia_semana, hora_inicio, hora_fin, activo
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (materia_id, grupo_n2_id, dia, clase['hora_inicio'], clase['hora_fin'], True))
    
    print("✅ Materias y horarios creados")
    
    # 8. ASIGNAR MAESTROS A MATERIAS
    print("📝 Asignando maestros...")
    
    # Procesar horarios N1
    for dia, clases in HORARIOS_N1.items():
        for clase in clases:
            cursor.execute('SELECT id FROM usuarios WHERE nombre_completo = ?', (clase['maestro'],))
            maestro_result = cursor.fetchone()
            if maestro_result:
                maestro_id = maestro_result[0]
                
                cursor.execute('SELECT id FROM materias WHERE clave_oficial = ?', (clase['codigo'],))
                materia_id = cursor.fetchone()[0]
                
                cursor.execute('''
                INSERT OR IGNORE INTO asignaciones_maestro (
                    maestro_id, materia_id, grupo_id, periodo, activa
                ) VALUES (?, ?, ?, ?, ?)
                ''', (maestro_id, materia_id, grupo_n1_id, "2024-1", True))
    
    # Procesar horarios N2
    for dia, clases in HORARIOS_N2.items():
        for clase in clases:
            cursor.execute('SELECT id FROM usuarios WHERE nombre_completo = ?', (clase['maestro'],))
            maestro_result = cursor.fetchone()
            if maestro_result:
                maestro_id = maestro_result[0]
                
                cursor.execute('SELECT id FROM materias WHERE clave_oficial = ?', (clase['codigo'],))
                materia_id = cursor.fetchone()[0]
                
                cursor.execute('''
                INSERT OR IGNORE INTO asignaciones_maestro (
                    maestro_id, materia_id, grupo_id, periodo, activa
                ) VALUES (?, ?, ?, ?, ?)
                ''', (maestro_id, materia_id, grupo_n2_id, "2024-1", True))
    
    print("✅ Maestros asignados")
    
    # 9. CREAR ESTUDIANTES DE EJEMPLO
    print("👨‍🎓 Creando estudiantes de ejemplo...")

    # Estudiantes con UID para pruebas
    estudiantes_ejemplo = [
        ("2233445566", "Ana Martínez Silva", "202323069", "ana.martinez@tesji.edu.mx", grupo_n1_id, "N1"),
        ("0987654321", "María González López", "202323274", "maria.gonzalez@tesji.edu.mx", grupo_n1_id, "N1"),
        ("1234567890", "Adrian Estudiante Ejemplo", "202323652", "adrian@tesji.edu.mx", grupo_n2_id, "N2"),
        ("1122334455", "Carlos Hernández Ruiz", "202323734", "carlos.hernandez@tesji.edu.mx", grupo_n2_id, "N2")
    ]

    for uid, nombre, matricula, email, grupo_id, salon in estudiantes_ejemplo:
        # Verificar si ya existe por matrícula, email o UID
        cursor.execute('SELECT id FROM usuarios WHERE matricula = ? OR email = ? OR uid = ?', (matricula, email, uid))
        if not cursor.fetchone():
            password_hash = hash_password("123456")
            cursor.execute('''
            INSERT INTO usuarios (
                uid, nombre_completo, matricula, email, password_hash, rol,
                carrera_id, grupo_id, semestre, salon, activo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                uid, nombre, matricula, email, password_hash, 'student',
                carrera_isc_id, grupo_id, 4, salon, True
            ))
            print(f"   ✅ Estudiante creado: {nombre}")
        else:
            print(f"   ⚠️ Estudiante ya existe: {nombre}")

    print("✅ Estudiantes de ejemplo procesados")
    
    # 10. CREAR ADMINISTRADOR
    print("👨‍💼 Creando administrador...")
    cursor.execute('SELECT id FROM usuarios WHERE matricula = "ADMIN001" OR email = "admin@tesji.edu.mx"')
    if not cursor.fetchone():
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
        print("   ✅ Administrador creado")
    else:
        print("   ⚠️ Administrador ya existe")

    print("✅ Administrador procesado")
    
    # 11. CONFIRMAR CAMBIOS
    conn.commit()
    
    # 12. MOSTRAR RESUMEN
    print("\n📊 RESUMEN FINAL:")
    
    cursor.execute('SELECT COUNT(*) FROM carreras')
    print(f"   🎓 Carreras: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "student"')
    print(f"   👨‍🎓 Estudiantes: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "teacher"')
    print(f"   👨‍🏫 Maestros: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "admin"')
    print(f"   👨‍💼 Administradores: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM materias')
    print(f"   📚 Materias: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM horarios_detallados')
    print(f"   ⏰ Horarios: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM asignaciones_maestro')
    print(f"   📝 Asignaciones: {cursor.fetchone()[0]}")
    
    conn.close()
    
    print("\n🎉 CONFIGURACIÓN COMPLETADA")
    print("✅ Sistema TESJI listo para usar")
    print("\n🔑 CREDENCIALES:")
    print("   Admin: admin / admin123")
    print("   Maestros: PROF001-PROF008 / 123456")
    print("   Estudiantes: 123456")

if __name__ == "__main__":
    setup_database()
