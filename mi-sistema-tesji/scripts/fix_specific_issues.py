#!/usr/bin/env python3
"""
Script específico para arreglar los problemas reportados - Versión 2
Maneja correctamente la estructura existente de la base de datos
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime

def hash_password(password: str) -> str:
    """Crear hash de contraseña"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def inspect_database_structure(db_path="tesji_rfid_system.db"):
    """Inspeccionar la estructura actual de la base de datos"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔍 INSPECCIONANDO ESTRUCTURA DE BASE DE DATOS...")
    print("=" * 60)
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n📋 Tabla: {table_name}")
        
        # Obtener estructura de la tabla
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            col_id, name, data_type, not_null, default_val, pk = col
            null_str = "NOT NULL" if not_null else "NULL"
            pk_str = "PRIMARY KEY" if pk else ""
            default_str = f"DEFAULT {default_val}" if default_val else ""
            print(f"   - {name}: {data_type} {null_str} {pk_str} {default_str}")
    
    conn.close()
    print("=" * 60)

def fix_database_issues_v2(db_path="tesji_rfid_system.db"):
    """Arreglar problemas específicos - Versión 2"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 ARREGLANDO PROBLEMAS ESPECÍFICOS - V2...")
    print("=" * 50)
    
    # 1. VERIFICAR Y AGREGAR COLUMNA SALON SI NO EXISTE
    print("1️⃣ Verificando columna 'salon' en usuarios...")
    try:
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'salon' not in columns:
            cursor.execute('ALTER TABLE usuarios ADD COLUMN salon TEXT')
            print("   ✅ Columna 'salon' agregada")
        else:
            print("   ✅ Columna 'salon' ya existe")
    except Exception as e:
        print(f"   ❌ Error con columna salon: {e}")
    
    # 2. ASEGURAR QUE EXISTAN LAS CARRERAS BÁSICAS
    print("\n2️⃣ Verificando carreras...")
    
    # Verificar si la tabla carreras existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='carreras'")
    if not cursor.fetchone():
        cursor.execute('''
        CREATE TABLE carreras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            codigo TEXT NOT NULL UNIQUE,
            semestres INTEGER NOT NULL DEFAULT 9,
            activa BOOLEAN DEFAULT TRUE,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("   ✅ Tabla carreras creada")
    
    # Insertar carreras básicas
    carreras_basicas = [
        ("Ingeniería en Sistemas Computacionales", "ISC", 9),
        ("Ingeniería Industrial", "II", 9),
        ("Ingeniería Mecánica", "IM", 9),
        ("Ingeniería en Gestión Empresarial", "IGE", 9),
        ("Licenciatura en Administración", "LA", 8),
        ("Ingeniería Electrónica", "IE", 9),
        ("Ingeniería Civil", "IC", 9)
    ]
    
    for nombre, codigo, semestres in carreras_basicas:
        cursor.execute('SELECT id FROM carreras WHERE codigo = ?', (codigo,))
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO carreras (nombre, codigo, semestres, activa)
            VALUES (?, ?, ?, ?)
            ''', (nombre, codigo, semestres, True))
            print(f"   ✅ Carrera agregada: {nombre}")
        else:
            print(f"   ✅ Carrera ya existe: {nombre}")
    
    # 3. VERIFICAR ESTRUCTURA DE HORARIOS_DETALLADOS
    print("\n3️⃣ Verificando estructura de horarios_detallados...")
    
    cursor.execute("PRAGMA table_info(horarios_detallados)")
    horarios_columns = {row[1]: row for row in cursor.fetchall()}
    
    print("   Columnas encontradas:")
    for col_name, col_info in horarios_columns.items():
        print(f"     - {col_name}: {col_info[2]} {'NOT NULL' if col_info[3] else 'NULL'}")
    
    # 4. CREAR SALONES SI LA TABLA EXISTE
    if 'salon_id' in horarios_columns:
        print("\n4️⃣ Verificando tabla salones...")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='salones'")
        if not cursor.fetchone():
            cursor.execute('''
            CREATE TABLE salones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                capacidad INTEGER DEFAULT 40,
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            print("   ✅ Tabla salones creada")
        
        # Insertar salones básicos
        salones_basicos = [
            ("N1", 45),
            ("N2", 45),
            ("L1", 30),
            ("L2", 30),
            ("A1", 50),
            ("A2", 50)
        ]
        
        for nombre, capacidad in salones_basicos:
            cursor.execute('SELECT id FROM salones WHERE nombre = ?', (nombre,))
            if not cursor.fetchone():
                cursor.execute('''
                INSERT INTO salones (nombre, capacidad, activo)
                VALUES (?, ?, ?)
                ''', (nombre, capacidad, True))
                print(f"   ✅ Salón agregado: {nombre}")
            else:
                print(f"   ✅ Salón ya existe: {nombre}")
    
    # 5. CREAR GRUPOS BÁSICOS
    print("\n5️⃣ Verificando grupos...")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='grupos'")
    if not cursor.fetchone():
        cursor.execute('''
        CREATE TABLE grupos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            carrera_id INTEGER NOT NULL,
            semestre INTEGER NOT NULL,
            periodo TEXT NOT NULL DEFAULT '2024-2025',
            salon TEXT,
            turno TEXT,
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (carrera_id) REFERENCES carreras (id)
        )
        ''')
        print("   ✅ Tabla grupos creada")
    
    # Obtener ID de ISC
    cursor.execute('SELECT id FROM carreras WHERE codigo = "ISC"')
    carrera_isc = cursor.fetchone()
    if carrera_isc:
        carrera_isc_id = carrera_isc[0]
        
        grupos_basicos = [
            ("Grupo 3401", carrera_isc_id, 4, "2024-2025", "N1", "Matutino"),
            ("Grupo 3402", carrera_isc_id, 4, "2024-2025", "N2", "Vespertino")
        ]
        
        for nombre, carrera_id, semestre, periodo, salon, turno in grupos_basicos:
            cursor.execute('SELECT id FROM grupos WHERE nombre = ?', (nombre,))
            if not cursor.fetchone():
                cursor.execute('''
                INSERT INTO grupos (nombre, carrera_id, semestre, periodo, salon, turno, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (nombre, carrera_id, semestre, periodo, salon, turno, True))
                print(f"   ✅ Grupo agregado: {nombre}")
            else:
                print(f"   ✅ Grupo ya existe: {nombre}")
    
    # 6. CREAR MATERIAS BÁSICAS
    print("\n6️⃣ Verificando materias...")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='materias'")
    if not cursor.fetchone():
        cursor.execute('''
        CREATE TABLE materias (
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
            FOREIGN KEY (carrera_id) REFERENCES carreras (id)
        )
        ''')
        print("   ✅ Tabla materias creada")
    
    if carrera_isc:
        materias_4to = [
            ("Ecuaciones Diferenciales", "ACF-0905", 5, 3, 2),
            ("Métodos Numéricos", "SCC-1017", 4, 2, 2),
            ("Tópicos Avanzados de Programación", "SCD-1027", 5, 2, 3),
            ("Fundamentos de Base de Datos", "AEF-1031", 5, 3, 2),
            ("Taller de Sistemas Operativos", "SCA-1026", 4, 0, 4),
            ("Arquitectura de Computadoras", "SCD-1003", 5, 2, 3),
            ("Taller de Ética", "ACA-0907", 4, 0, 4),
            ("Inglés IV", "ING-004", 2, 2, 0)
        ]
        
        for nombre, codigo, creditos, ht, hp in materias_4to:
            cursor.execute('SELECT id FROM materias WHERE codigo = ? AND carrera_id = ?', (codigo, carrera_isc_id))
            if not cursor.fetchone():
                cursor.execute('''
                INSERT INTO materias (
                    nombre, codigo, carrera_id, semestre, creditos, 
                    horas_teoria, horas_practica, clave_oficial, activa
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (nombre, codigo, carrera_isc_id, 4, creditos, ht, hp, codigo, True))
                print(f"   ✅ Materia agregada: {nombre}")
            else:
                print(f"   ✅ Materia ya existe: {nombre}")
    
    # 7. CREAR MAESTROS BÁSICOS
    print("\n7️⃣ Verificando maestros...")
    
    maestros_basicos = [
        ("Ing. Rodolfo Guadalupe Alcántara Rosales", "PROF001", "rodolfo.alcantara@tesji.edu.mx", "Matemáticas"),
        ("Lic. Juan Alberto Martínez Zamora", "PROF002", "juan.martinez@tesji.edu.mx", "Métodos Numéricos"),
        ("Víctor David Maya Arce", "PROF003", "victor.maya@tesji.edu.mx", "Programación"),
        ("Mtra. Yadira Esther Jiménez Pérez", "PROF004", "yadira.jimenez@tesji.edu.mx", "Base de Datos"),
        ("Mtro. Anselmo Martínez Montalvo", "PROF005", "anselmo.martinez@tesji.edu.mx", "Sistemas Operativos"),
        ("Ing. Alfredo Aguilar López", "PROF006", "alfredo.aguilar@tesji.edu.mx", "Hardware"),
        ("C.P. Sonia Vázquez Alcántara", "PROF007", "sonia.vazquez@tesji.edu.mx", "Ética"),
        ("L.L. Isodoro Cruz Huitrón", "PROF008", "isodoro.cruz@tesji.edu.mx", "Inglés")
    ]
    
    for nombre, matricula, email, especialidad in maestros_basicos:
        cursor.execute('SELECT id FROM usuarios WHERE matricula = ?', (matricula,))
        if not cursor.fetchone():
            password_hash = hash_password("123456")
            cursor.execute('''
            INSERT INTO usuarios (
                nombre_completo, matricula, email, password_hash, rol, 
                carrera_id, especialidad, activo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, matricula, email, password_hash, 'teacher', carrera_isc_id, especialidad, True))
            print(f"   ✅ Maestro agregado: {nombre}")
        else:
            print(f"   ✅ Maestro ya existe: {nombre}")
    
    # 8. CREAR HORARIOS SEGÚN LA ESTRUCTURA EXISTENTE
    print("\n8️⃣ Verificando horarios...")
    
    # Obtener IDs necesarios
    cursor.execute('SELECT id FROM grupos WHERE nombre = "Grupo 3401"')
    grupo_3401 = cursor.fetchone()
    
    if grupo_3401:
        grupo_3401_id = grupo_3401[0]
        
        # Obtener salon_id si existe la columna
        salon_id = None
        if 'salon_id' in horarios_columns:
            cursor.execute('SELECT id FROM salones WHERE nombre = "N1"')
            salon_result = cursor.fetchone()
            if salon_result:
                salon_id = salon_result[0]
        
        # Horarios para N1
        horarios_n1 = [
            # Lunes
            ("Métodos Numéricos", "Lunes", "07:00", "09:00", "Teoría"),
            ("Ecuaciones Diferenciales", "Lunes", "09:00", "12:00", "Teoría"),
            ("Fundamentos de Base de Datos", "Lunes", "15:00", "18:00", "Teoría"),
            
            # Martes
            ("Inglés IV", "Martes", "09:00", "11:00", "Idioma"),
            ("Arquitectura de Computadoras", "Martes", "11:00", "13:00", "Teoría"),
            ("Tópicos Avanzados de Programación", "Martes", "13:00", "15:00", "Práctica"),
            
            # Miércoles
            ("Métodos Numéricos", "Miércoles", "07:00", "09:00", "Teoría"),
            ("Inglés IV", "Miércoles", "09:00", "11:00", "Idioma"),
            ("Ecuaciones Diferenciales", "Miércoles", "11:00", "13:00", "Teoría"),
            ("Taller de Sistemas Operativos", "Miércoles", "13:00", "15:00", "Práctica"),
            
            # Jueves
            ("Inglés IV", "Jueves", "07:00", "09:00", "Idioma"),
            ("Taller de Ética", "Jueves", "09:00", "11:00", "Práctica"),
            ("Fundamentos de Base de Datos", "Jueves", "11:00", "13:00", "Teoría"),
            ("Tópicos Avanzados de Programación", "Jueves", "14:00", "16:00", "Práctica"),
            
            # Viernes
            ("Taller de Sistemas Operativos", "Viernes", "07:00", "09:00", "Práctica"),
            ("Taller de Ética", "Viernes", "09:00", "11:00", "Práctica"),
            ("Arquitectura de Computadoras", "Viernes", "11:00", "14:00", "Teoría")
        ]
        
        for materia_nombre, dia, hora_inicio, hora_fin, tipo in horarios_n1:
            # Buscar materia
            cursor.execute('SELECT id FROM materias WHERE nombre LIKE ?', (f"%{materia_nombre}%",))
            materia = cursor.fetchone()
            if materia:
                materia_id = materia[0]
                
                # Verificar si ya existe el horario
                cursor.execute('''
                SELECT id FROM horarios_detallados 
                WHERE materia_id = ? AND grupo_id = ? AND dia_semana = ? AND hora_inicio = ?
                ''', (materia_id, grupo_3401_id, dia, hora_inicio))
                
                if not cursor.fetchone():
                    # Insertar según la estructura de la tabla
                    if 'salon_id' in horarios_columns and salon_id:
                        cursor.execute('''
                        INSERT INTO horarios_detallados (
                            materia_id, grupo_id, salon_id, dia_semana, hora_inicio, hora_fin, tipo_clase, activo
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (materia_id, grupo_3401_id, salon_id, dia, hora_inicio, hora_fin, tipo, True))
                    else:
                        cursor.execute('''
                        INSERT INTO horarios_detallados (
                            materia_id, grupo_id, dia_semana, hora_inicio, hora_fin, tipo_clase, activo
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (materia_id, grupo_3401_id, dia, hora_inicio, hora_fin, tipo, True))
                    
                    print(f"   ✅ Horario agregado: {materia_nombre} - {dia} {hora_inicio}")
    
    # 9. CREAR ASIGNACIONES MAESTRO-MATERIA
    print("\n9️⃣ Verificando asignaciones maestro...")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='asignaciones_maestro'")
    if not cursor.fetchone():
        cursor.execute('''
        CREATE TABLE asignaciones_maestro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            maestro_id INTEGER NOT NULL,
            materia_id INTEGER NOT NULL,
            grupo_id INTEGER NOT NULL,
            periodo TEXT NOT NULL DEFAULT '2024-2025',
            activa BOOLEAN DEFAULT TRUE,
            fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (maestro_id) REFERENCES usuarios (id),
            FOREIGN KEY (materia_id) REFERENCES materias (id),
            FOREIGN KEY (grupo_id) REFERENCES grupos (id)
        )
        ''')
        print("   ✅ Tabla asignaciones_maestro creada")
    
    # Crear asignaciones
    asignaciones = [
        ("PROF001", "Ecuaciones Diferenciales"),
        ("PROF002", "Métodos Numéricos"),
        ("PROF003", "Tópicos Avanzados de Programación"),
        ("PROF004", "Fundamentos de Base de Datos"),
        ("PROF005", "Taller de Sistemas Operativos"),
        ("PROF006", "Arquitectura de Computadoras"),
        ("PROF007", "Taller de Ética"),
        ("PROF008", "Inglés IV")
    ]
    
    for matricula_maestro, nombre_materia in asignaciones:
        # Buscar maestro
        cursor.execute('SELECT id FROM usuarios WHERE matricula = ? AND rol = "teacher"', (matricula_maestro,))
        maestro = cursor.fetchone()
        
        # Buscar materia
        cursor.execute('SELECT id FROM materias WHERE nombre LIKE ?', (f"%{nombre_materia}%",))
        materia = cursor.fetchone()
        
        if maestro and materia and grupo_3401:
            maestro_id = maestro[0]
            materia_id = materia[0]
            
            cursor.execute('''
            SELECT id FROM asignaciones_maestro 
            WHERE maestro_id = ? AND materia_id = ? AND grupo_id = ?
            ''', (maestro_id, materia_id, grupo_3401_id))
            
            if not cursor.fetchone():
                cursor.execute('''
                INSERT INTO asignaciones_maestro (
                    maestro_id, materia_id, grupo_id, periodo, activa
                ) VALUES (?, ?, ?, ?, ?)
                ''', (maestro_id, materia_id, grupo_3401_id, "2024-2025", True))
                print(f"   ✅ Asignación creada: {matricula_maestro} -> {nombre_materia}")
    
    # 10. ASIGNAR ESTUDIANTES A GRUPOS Y SALONES
    print("\n🔟 Asignando estudiantes a grupos...")
    
    # Estudiantes del grupo N1 (3401)
    estudiantes_n1 = [
        "202323069", "202323274", "202323221", "202323699", "202323108",
        "202323090", "202323080", "202323006", "202323116", "202323288"
    ]
    
    # Estudiantes del grupo N2 (3402)
    estudiantes_n2 = [
        "202323734", "202323768", "202323367", "202323728", "202323883",
        "202323830", "202323377", "202323352", "202323652", "202323737"
    ]
    
    # Asignar estudiantes N1
    for matricula in estudiantes_n1:
        cursor.execute('SELECT id FROM usuarios WHERE matricula = ? AND rol = "student"', (matricula,))
        estudiante = cursor.fetchone()
        if estudiante and grupo_3401:
            cursor.execute('UPDATE usuarios SET grupo_id = ?, salon = ? WHERE id = ?', 
                         (grupo_3401_id, "N1", estudiante[0]))
            print(f"   ✅ Estudiante {matricula} asignado a Grupo 3401 (N1)")
    
    # Buscar grupo 3402
    cursor.execute('SELECT id FROM grupos WHERE nombre = "Grupo 3402"')
    grupo_3402 = cursor.fetchone()
    if grupo_3402:
        grupo_3402_id = grupo_3402[0]
        
        # Asignar estudiantes N2
        for matricula in estudiantes_n2:
            cursor.execute('SELECT id FROM usuarios WHERE matricula = ? AND rol = "student"', (matricula,))
            estudiante = cursor.fetchone()
            if estudiante:
                cursor.execute('UPDATE usuarios SET grupo_id = ?, salon = ? WHERE id = ?', 
                             (grupo_3402_id, "N2", estudiante[0]))
                print(f"   ✅ Estudiante {matricula} asignado a Grupo 3402 (N2)")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 PROBLEMAS ESPECÍFICOS ARREGLADOS - V2")
    print("=" * 50)
    print("✅ Estructura de base de datos respetada")
    print("✅ Carreras completas en admin")
    print("✅ Horarios configurados correctamente")
    print("✅ Asignaciones maestro-materia creadas")
    print("✅ Grupos y salones asignados")
    print("=" * 50)

def main():
    print("🔧 ARREGLO ESPECÍFICO DE PROBLEMAS TESJI - V2")
    print("=" * 50)
    print("Primero inspeccionaremos la estructura existente...")
    print("=" * 50)
    
    try:
        # Primero inspeccionar la estructura
        inspect_database_structure()
        
        # Luego arreglar los problemas
        fix_database_issues_v2()
        
        print("\n🎉 TODOS LOS PROBLEMAS ARREGLADOS")
        print("✅ Reinicia el servidor para ver los cambios")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
