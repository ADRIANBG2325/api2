#!/usr/bin/env python3
"""
Sistema TESJI Completo - Reconstrucción Total
Incluye todas las carreras, materias, estudiantes y funcionalidades requeridas
"""

import sqlite3
import os
import hashlib
import secrets
from datetime import datetime

def delete_existing_database():
    """Elimina la base de datos existente"""
    db_files = [
        "tesji_rfid_system.db",
        "scripts/tesji_rfid_system.db"
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"🗑️ Base de datos eliminada: {db_file}")
    
    print("✅ Limpieza completada")

def hash_password(password: str) -> str:
    """Crea hash seguro para contraseñas"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def create_enhanced_tables(db_path="tesji_rfid_system.db"):
    """Crea todas las tablas mejoradas"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Creando estructura de tablas mejorada...")
    
    # 1. Tabla de carreras
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
    
    # 2. Tabla de usuarios mejorada
    cursor.execute('''
    CREATE TABLE usuarios (
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
        carrera_secundaria_id INTEGER,
        FOREIGN KEY (carrera_id) REFERENCES carreras (id),
        FOREIGN KEY (carrera_secundaria_id) REFERENCES carreras (id)
    )
    ''')
    
    # 3. Tabla de grupos mejorada
    cursor.execute('''
    CREATE TABLE grupos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo_grupo TEXT NOT NULL,
        carrera_id INTEGER NOT NULL,
        semestre INTEGER NOT NULL,
        periodo TEXT NOT NULL DEFAULT '2024-1',
        activo BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        salon TEXT,
        turno TEXT,
        capacidad INTEGER DEFAULT 50,
        FOREIGN KEY (carrera_id) REFERENCES carreras (id)
    )
    ''')
    
    # 4. Tabla de materias completa
    cursor.execute('''
    CREATE TABLE materias (
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
        prerequisitos TEXT,
        FOREIGN KEY (carrera_id) REFERENCES carreras (id)
    )
    ''')
    
    # 5. Tabla de asistencias
    cursor.execute('''
    CREATE TABLE asistencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
        presente BOOLEAN DEFAULT TRUE,
        usuario_id INTEGER,
        materia_id INTEGER,
        grupo_id INTEGER,
        observaciones TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
        FOREIGN KEY (materia_id) REFERENCES materias (id),
        FOREIGN KEY (grupo_id) REFERENCES grupos (id)
    )
    ''')
    
    # 6. Tabla de salones
    cursor.execute('''
    CREATE TABLE salones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        capacidad INTEGER DEFAULT 30,
        tipo TEXT DEFAULT 'Aula',
        activo BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        ubicacion TEXT,
        equipamiento TEXT
    )
    ''')
    
    # 7. Tabla de asignaciones maestro mejorada
    cursor.execute('''
    CREATE TABLE asignaciones_maestro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maestro_id INTEGER NOT NULL,
        materia_id INTEGER NOT NULL,
        grupo_id INTEGER NOT NULL,
        carrera_id INTEGER NOT NULL,
        periodo TEXT NOT NULL DEFAULT '2024-1',
        activa BOOLEAN DEFAULT TRUE,
        fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (maestro_id) REFERENCES usuarios (id),
        FOREIGN KEY (materia_id) REFERENCES materias (id),
        FOREIGN KEY (grupo_id) REFERENCES grupos (id),
        FOREIGN KEY (carrera_id) REFERENCES carreras (id)
    )
    ''')
    
    # 8. Tabla de horarios detallados mejorada
    cursor.execute('''
    CREATE TABLE horarios_detallados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        materia_id INTEGER NOT NULL,
        grupo_id INTEGER NOT NULL,
        carrera_id INTEGER NOT NULL,
        dia_semana TEXT NOT NULL,
        hora_inicio TEXT NOT NULL,
        hora_fin TEXT NOT NULL,
        tipo_clase TEXT DEFAULT 'Teoría',
        salon_id INTEGER,
        activo BOOLEAN DEFAULT TRUE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (materia_id) REFERENCES materias (id),
        FOREIGN KEY (grupo_id) REFERENCES grupos (id),
        FOREIGN KEY (carrera_id) REFERENCES carreras (id),
        FOREIGN KEY (salon_id) REFERENCES salones (id)
    )
    ''')
    
    # 9. Tabla de inscripciones (relación estudiante-materia)
    cursor.execute('''
    CREATE TABLE inscripciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estudiante_id INTEGER NOT NULL,
        materia_id INTEGER NOT NULL,
        grupo_id INTEGER NOT NULL,
        periodo TEXT NOT NULL DEFAULT '2024-1',
        activa BOOLEAN DEFAULT TRUE,
        fecha_inscripcion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (estudiante_id) REFERENCES usuarios (id),
        FOREIGN KEY (materia_id) REFERENCES materias (id),
        FOREIGN KEY (grupo_id) REFERENCES grupos (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Todas las tablas mejoradas creadas exitosamente")

def populate_all_carreras(db_path="tesji_rfid_system.db"):
    """Pobla todas las carreras del TESJI"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🎓 Poblando todas las carreras...")
    
    carreras = [
        ("Ingeniería en Sistemas Computacionales", "ISC", 9),
        ("Ingeniería Industrial", "II", 9),
        ("Ingeniería Mecatrónica", "IM", 9),
        ("Ingeniería Civil", "IC", 9),
        ("Licenciatura en Administración", "LA", 9),
        ("Ingeniería Química", "IQ", 9),
        ("Ingeniería en Logística", "IL", 9),
        ("Ingeniería en Tecnologías de la Información y Comunicaciones", "ITIC", 9)
    ]
    
    for nombre, codigo, semestres in carreras:
        cursor.execute('''
        INSERT INTO carreras (nombre, codigo, semestres)
        VALUES (?, ?, ?)
        ''', (nombre, codigo, semestres))
    
    conn.commit()
    conn.close()
    print(f"✅ {len(carreras)} carreras creadas")

def populate_all_materias(db_path="tesji_rfid_system.db"):
    """Pobla todas las materias de todas las carreras"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📚 Poblando todas las materias por carrera...")
    
    # Obtener IDs de carreras
    cursor.execute('SELECT id, codigo FROM carreras')
    carreras_dict = {codigo: id for id, codigo in cursor.fetchall()}
    
    # Materias por carrera y semestre
    materias_por_carrera = {
        "ISC": {
            1: ["Calculo diferencial", "Fundamentos de programacion", "Desarrollo sustentable", "Matematicas discretas", "Quimica", "Fundamentos de Programacion"],
            2: ["Calculo integral", "Programacion orientada a objetos", "Taller de administración", "Algebra lineal", "Probabilidad y estadistica", "Fisica general"],
            3: ["Calculo vectorial", "Estructura de datos", "Fundamentos de telecomunicaciones", "Investigacion de operaciones", "Sistemas operaticos l", "Principio electricos y aplicaciones digitales"],
            4: ["Ecuaciones diferenciales", "Metodos numericos", "Topicos avanzados de programacion", "Fundamentos de bases de datos", "Taller de sistemas operativos", "Arquitectura de computadoras", "Taller de etica"],
            5: ["Lenguaje y automatas l", "Redes computacionales", "Taller de base de datos", "Simulacion", "Fundametos de ingenieria software", "Lenguaje de interfaz", "Contabilidad financiera"],
            6: ["Lenguajes y autonomas ll", "Administracion de redes", "Administracion de bases de datos", "Programacion web", "Ingenieria de software", "Sistemas programables"],
            7: ["Programacion logica y funcional", "Comunicación y enrutamiento de redes de datos", "Taller de investigacion l", "Desarrollo de aplicaciones para dispositivos moviles", "Gestion de proyectos de software", "Internet de las cosas", "Graficacion"],
            8: ["Inteligencia artificial", "Ciberseguridad", "Taller de investigacion ll", "Programacion reactiva", "Sistemas distribuidos", "Cultura empresarial"],
            9: ["Residencias profecionales"]
        },
        "II": {
            1: ["Fundamentos de investigacion", "Taller de etica", "Calculo diferencial", "Taller de herramientas intelectiales", "Quimica", "Dibujo industrial"],
            2: ["Electricidad y electronica industrial", "Propiedades de materiales", "Calculo integral", "Analisis de la realidad nacional", "Taller de liderazgo"],
            3: ["Metodoligia y normalizacion", "Alguebra lineal", "Calculo vectorial", "Economia", "Estadistica inferencial l", "Estudio de trabajo l", "Higiene y seguridad industrial"],
            4: ["Proceso de fabricacion", "Fisica", "Algoritmos y lenguajes de programacion", "Investigacion de operaciones l", "Estadistica inferencial ll", "Estudio de trabajo ll", "Desarrollo sustentable"],
            5: ["Administracion de proyectos", "Gestion de costos", "Administracion de operaciones l", "Investigacion de operaciones ll", "Control estadistico de la calidad", "Ergonomia"],
            6: ["Taller de investigaciones l", "Investigacion economica", "Administracion de operaciones ll", "Simulacion", "Administracion del mantenimiento", "Mercadotecnia"],
            7: ["Taller de investigaciones ll", "Planeacion financiera", "Planeacion y diseño de instalaciones", "Sistema de manufactura", "Logistica y cadenas di simulacion", "Gestion de los sistemas de calidad", "Ingenieria de sistemas"],
            8: ["Formacion y evaluacion de proyectos", "Relaciones industriales"],
            9: ["Residencias profecionales", "Especialidad"]
        },
        "IM": {
            1: ["Quimica", "Calcul diferencial", "Taller de etica", "Dibujo asistido por computadora", "Metodologia y normalizacion", "Fundamentos de investigacion"],
            2: ["Calculo integral", "Algebra lineal", "Ciencia e ingenieria de los materiales", "Estadistica y control de calidad", "Programacion basica", "Administracion y contabilidad", "Taller de investigacion l"],
            3: ["Calculo vectorial", "Procesos de fabricacion", "Electromagnetismo", "Estatica", "Metodos numericos", "Desarrollo sustentable", "Taller de investigacion ll"],
            4: ["Ecuaciones diferenciales", "Fundamentos de termoninamica", "Mecanica de materiales", "Dinamica", "Analisis de citcuitos electronicos", "Electronica analógica"],
            5: ["Maquinas electricas", "Mecanismo", "Analisis de fluidos", "Electronica digital", "Programacio avanzada", "Circuitos hidraulicos y neumaticos"],
            6: ["Electronica de potencia aplicada", "Instrumentacion", "Diseño de benmentos mecanicos", "Vibraciones mecanicas", "Dinamica de sistemas"],
            7: ["Mantenimiento", "Manufactura avanzada", "Microcontroladores", "Control", "Manufactura integrada por compuradora", "Diseño avanzado y manufactura"],
            8: ["Formacion y evaluacion de proyectos", "Controladores logicos programables", "Robotica", "Control robotico", "Automatizacion industrial", "Instrumentacion avanzada"],
            9: ["Residencia profecional"]
        },
        "IC": {
            1: ["Fundamentos de investigacion", "Calculo diferencial", "Taller de etica", "Quimica", "Software en ingenieria civil", "Dibujo en ingenieria civil", "Tutorias", "Taller de matematicas l"],
            2: ["Calculo vectorial", "Geología", "Probabilidad y estadistica", "Topografia", "Matematicas y procesos constructivos", "Calculo integral", "Tutorias ll", "Taller de matematicas ll"],
            3: ["Estatica", "Ecuaciones diferenciales", "Algebra lineal", "Carreteras", "Tecnologia dol concreto", "Sistemas de transporte", "Tutorias lll"],
            4: ["Fundamentos de macanica de los medios continuos", "Metodos numericos", "Mecanicas de suelos", "Maquinaria pesada y movimiento de tierra", "Dinamica", "Modelos de optimizacion de recursos", "Tutorias lV"],
            5: ["Mecanica de materiales", "Desarrollo sustentable", "Macanica de suelos aplicada", "Costos y presupuestos", "Taller de investigacion l", "Hidraulica básica", "Servicio social"],
            6: ["Analisis estructural", "Instalacion de los edificios", "Diseño y construcioon de pavimentos", "Administracion de la construccion", "Hidrologia superficial", "Hidraulica de canales", "Servicio social"],
            7: ["Analisis estructural avanzado", "Diseño de elentos de concreto reforzado", "Taller de investigaciones ll", "Abastecimiento de agua", "Topolografia de obras", "Normatividad y seguridad en la construccion", "Planeacion y control de obra"],
            8: ["Diseño estructural de cimentaciones", "Diseño e elentos de acero", "Formulacion y evaluacion de proyectos", "Alcantarillado", "Construccion pesada", "Construccion de estructuras de concreto", "Construccion de estructuras de acero"],
            9: ["Residencia profecional"]
        },
        "LA": {
            1: ["Teoria general de la administracion", "Informatica para la administracion", "Taller de etica", "Fundamentos de investigacion", "Matematicas aplicadas a la administracion", "Contabilidad general"],
            2: ["Funcion administrativa l", "Estadistica para la administracion l", "Derecho laboral y seuridad social", "Comunicación corporativa", "Taller de desarrollo humano", "Costos de manufactura"],
            3: ["Funcion adinistrativa ll", "Estadistica para la administracion ll", "Derecho empresarial", "Comportamiento organizacional", "Dinamica social", "Contabilidad general"],
            4: ["Gestion estrategica del capital humano l", "Procesos estructurales", "Metodos cuantitativos para la administracion", "Fundamentos de mercadotecnia", "Economia empresarial", "Matematicas financieras"],
            5: ["Gestion estrategica del capital humano ll", "Derecho fisico", "Mezcla de mercadotecnia", "Macroeonimia", "Administracion financiera l", "Desarrollo sustentable"],
            6: ["Gestion de la retribucion", "Produccion", "Taller de investigacion l", "Sistema de informacion de mercadorecnia", "Innovacion y emprendedurismo", "Administracion financiera ll"],
            7: ["Plan de negocios", "Procesos de direccion", "Taller de investigacion ll", "Administracion de la calidad", "Economia internacional", "Diagnosticos y evaluacion empresarial"],
            8: ["Consulta empresarial", "Formulacion y evaluacio de proyectos", "Desarrollo organizacional"],
            9: ["Residencia profecional", "Especialidad"]
        },
        "IQ": {
            1: ["Taller de etica", "Fundamentos de investigacion", "Calculo diferencial", "Quimica inorganica", "Programacion", "Dibujo asistido por computadora"],
            2: ["Algebra lineal", "Macanica clasica", "Calculo integral", "Quimica organica l", "Termodinamica", "Quimica analitica"],
            3: ["Analisis de datos experimentales", "Electricidad, magnetismo y optica", "Calculo vectorial", "Quimica organica ll", "Balance de materia y energia", "Gestion de calidad"],
            4: ["Metodos numerocos", "Ecuaciones diferenciales", "Macanismo de transferencia", "Ingenieria ambintal", "Fisicoquimica l", "Analisis instrumental"],
            5: ["Taller de investigacion l", "Procesos de separacion ll", "Laboratorio integral l", "Reactores quimicos"],
            6: ["Taller de investigacion l", "Procesos de separacion ll", "Laboratorio integral l", "Rectores quimicos"],
            7: ["Taller de administracion", "Taller de investigacion ll", "Procesos de separacion lll", "Salud y segurida en el trabajo", "Laboratorio integral ll"],
            8: ["Laboratorio integral lll", "Instrumentacion y control", "Ingenieria de proyectos", "Simulacion e procesos"],
            9: ["Residencia profecional", "Especialidad"]
        },
        "IL": {
            1: ["Introduccion a la ingenieria logistica", "Calculo diferencial", "Quimica", "Fundamentos de administracion", "Dibujo asistido por computadora", "Economia"],
            2: ["Taller de etica", "Calculo integral", "Probavilidad y estadistica", "Desarrollo humano y organización", "Contabilidad y costo"],
            3: ["Cadena de suministro", "Algebra lineal", "Estadistica inferencial l", "Fundamentos de derecho", "Mecanica clasica", "Finanzas"],
            4: ["Compras", "Tipologia del producto", "Estadistica inferencial ll", "Entorno economico", "Topicos de ingenieria mécanica", "Bases de datos"],
            5: ["Almacenes", "Inventario", "Investigacion de operaciones l", "Higiene y seguridad", "Procesos de fabricacion y manejo de materiales", "Mercadotecnia"],
            6: ["Trafico y transporte", "Cultura de calidad", "Investigacion de operaciones ll", "Desarrollo sustentable", "Taller de investigacion l", "Empaque, envase y embalaje"],
            7: ["Servicio al cliente", "Programacion de procesos productivos", "Modelo de simulacion y logistica", "Legislacion aduanero", "Taller de investigacion ll", "Ingenieria economica"],
            8: ["Inovacion", "Comercion internacional", "Formulacion y evaluacion de proyectos", "Geografia para el transporte"],
            9: ["Residencia profecional", "Especialidad", "Gestion de proyectos"]
        },
        "ITIC": {
            1: ["Calculo diferencial", "Fundamentos de programacion", "Matematicas discretas l", "Fundamentos de redes", "Telecomunicaciones", "Introduccion a las TIC´S"],
            2: ["Calculo integral", "Programacionorientada a objetos", "Matematicas discretas ll", "Redes de comunicación", "Probabilidad y estadistica", "Arquitectura de computadoras"],
            3: ["Matematicas aplicadas a comunicaciones", "Estructura y organización de datos", "Sistemas operativos l", "Fundamentos de bases de datos", "Electricidad y magnetismo", "Algebra lineal"],
            4: ["Analisis de señales y sistemas de comunicación", "Programacion ll", "Sistemas operaticos ll", "Taller de bases de datos", "Circuitos electricos y electronicos", "Ingenieroa de software"],
            5: ["Fundamentos de investigacion", "Redes emergentes", "Contabilidad y costos", "Bases de datos distribuidas", "Taller de ingenieria de software", "Ciberseguridad"],
            6: ["Taller de investigacion l", "Programacion web", "Administracion general", "Administracion y seguridad de redes", "Desarrollo de aplicaciones para dispositivos moviles", "Interaccion humano computadora"],
            7: ["Taller de investigacion ll", "Negocios electricos l", "Matematicas para la tamo de decisiones", "Tecnología inalámbrica", "Desarrollo de aplicaciones de realidad aumentada", "Internet de las cosas", "Desarrollo de emprendedores"],
            8: ["Administracion de proyectos", "Negocios electricos ll", "Desarrollo sustentable", "Auditoria en tecnologias de la informacion", "Ingenieria del conocimiento", "Herramientas para el analisis de datos masivos (BIG DATA)", "Computo en la nube"],
            9: ["Taller de tica", "Residencia profecional"]
        }
    }
    
    # Insertar materias
    total_materias = 0
    for codigo_carrera, semestres in materias_por_carrera.items():
        carrera_id = carreras_dict.get(codigo_carrera)
        if not carrera_id:
            continue
            
        for semestre, materias in semestres.items():
            for materia in materias:
                if materia.strip():  # Solo si no está vacío
                    cursor.execute('''
                    INSERT INTO materias (nombre, carrera_id, semestre, creditos, activa)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (materia.strip(), carrera_id, semestre, 5, True))
                    total_materias += 1
    
    conn.commit()
    conn.close()
    print(f"✅ {total_materias} materias creadas para todas las carreras")

def create_grupos_isc(db_path="tesji_rfid_system.db"):
    """Crea los grupos específicos de ISC"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("👥 Creando grupos de ISC...")
    
    # Obtener ID de carrera ISC
    cursor.execute('SELECT id FROM carreras WHERE codigo = "ISC"')
    carrera_isc = cursor.fetchone()
    if not carrera_isc:
        print("❌ Error: Carrera ISC no encontrada")
        return
    carrera_isc_id = carrera_isc[0]
    
    grupos = [
        ("Grupo 3102", "3102", carrera_isc_id, 4, "2024-1", "N1", "Matutino", 50),
        ("Grupo 3101", "3101", carrera_isc_id, 4, "2024-1", "N2", "Matutino", 50)
    ]
    
    for nombre, codigo, carrera_id, semestre, periodo, salon, turno, capacidad in grupos:
        cursor.execute('''
        INSERT INTO grupos (nombre, codigo_grupo, carrera_id, semestre, periodo, salon, turno, capacidad)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, codigo, carrera_id, semestre, periodo, salon, turno, capacidad))
    
    conn.commit()
    conn.close()
    print(f"✅ {len(grupos)} grupos de ISC creados")

def populate_estudiantes_reales(db_path="tesji_rfid_system.db"):
    """Pobla los estudiantes reales del TESJI"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("👨‍🎓 Poblando estudiantes reales...")
    
    # Obtener IDs necesarios
    cursor.execute('SELECT id FROM carreras WHERE codigo = "ISC"')
    carrera_isc_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM grupos WHERE codigo_grupo = "3102"')
    grupo_3102_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM grupos WHERE codigo_grupo = "3101"')
    grupo_3101_id = cursor.fetchone()[0]
    
    # Estudiantes del Grupo 3102 (N1)
    estudiantes_3102 = [
        ("202323734", "AGUIRRE MARTINEZ CESAR ALEJANDRO"),
        ("202323768", "ALVAREZ RIVAS CLAUDIA CAMILA"),
        ("202323367", "ANAYA MARTINEZ OMAR"),
        ("202323728", "ANTONIO ALMAZAN LUIS ALBERTO"),
        ("202323883", "ARCE DE JESÚS EDUARDO"),
        ("202323830", "ARCHUNDIA BERNABEZ VALENTIN"),
        ("202323377", "ARCINIEGA FLORES EDUARDO"),
        ("202323352", "BARANDA CRUZ EDUARDO JAVIER"),
        ("202323652", "BAUTISTA GUERRERO ADRIÁN"),
        ("202323737", "BECERRIL GONZALEZ ADRIANA"),
        ("202323458", "BECERRIL HERNANDEZ MISAELL"),
        ("202323762", "CAMACHO HERNANDEZ ALEXANDER"),
        ("202323355", "CAMACHO VEGA CESAR"),
        ("202323750", "CARPIO MARTINEZ JORGE"),
        ("202323315", "ESPINOSA GUADARRAMA REYNA"),
        ("202323732", "FRANCO JULIAN CHRISTIAN"),
        ("202323445", "GARCIA ANDRADE GUSTAVO"),
        ("202323403", "GARCIA RAMIREZ KARINA CRISTAL"),
        ("202323394", "GARCIA MENDOZA EDUARDO"),
        ("202323424", "GARCÍA TORRES ALEJANDRO"),
        ("202323752", "JUAN GARCIA ISAEL"),
        ("202323881", "LARA SANTIAGO NADIA DIOSELINA"),
        ("202323877", "MANUEL GONZALEZ BRYAN"),
        ("202323850", "MARTINEZ LAGUNAS JUAN ALEXIS"),
        ("202323885", "MARTINEZ MARTÍNEZ LUIS ENRIQUE"),
        ("202323725", "MARTINEZ ZEMPOALA ALEXIS"),
        ("202323386", "MEDINA SUAREZ YARET"),
        ("202323446", "MIRANDA ORTEGA JOSÉ FRANCISCO"),
        ("202323891", "MORENO MARTINEZ CESAR ALBERTO"),
        ("202323887", "MONROY FRAGOSO ANGEL ERUBIEL"),
        ("202323774", "MONROY ROSALES ÁNGEL RAFAEL"),
        ("202323464", "OROZCO ARCE CARLOS DANIEL"),
        ("202323092", "PADILLA MENDOZA XOCHITL"),
        ("202323112", "RAMIREZ HERNANDEZ JENIFER"),
        ("202323723", "RODRÍGUEZ MORALES BRANDON"),
        ("202323413", "RODRIGUEZ MAYORGA JOSE MANUEL"),
        ("202323892", "RODRIGUEZ URBANO DULCE ADANEY"),
        ("202323730", "SAMANO SANCHEZ JOSE ANGEL"),
        ("202323843", "SANCHEZ HERNANDEZ JORGE ARTURO"),
        ("202323896", "SANCHEZ OSORIO MISSAEL"),
        ("202323758", "SANTIAGO ARCE JOSE ANTONIO"),
        ("202323398", "SANTIAGO SOTELO JUAN MANUEL"),
        ("202323420", "UGALDE GONZALEZ BENITO OSWALDO"),
        ("202323382", "VIDAL VIDAL LUZ ESTRELLA"),
        ("202323449", "ZAMUDIO BECERRIL JOSÉ GUADALUPE")
    ]
    
    # Estudiantes del Grupo 3101 (N2)
    estudiantes_3101 = [
        ("202323069", "ACELES MIRANDA ANGEL EDUARDO"),
        ("202323274", "AUMAZÁN MARTÍNEZ YANET"),
        ("202323221", "ARCE ARCE CITLAUT"),
        ("202323699", "ARCE CRUZ ALONDRA"),
        ("202323108", "ARCE GABRIEL LUZ JIMENA"),
        ("202323090", "CAMACHO OSOBIO LINDA ESTRELLA"),
        ("202323080", "CAPETILLO BONIFACIO DE ALONDRA"),
        ("202323006", "CARLOS MARCIAL DIEGO"),
        ("202323116", "CASIMIRO CRUZ JOSÉ ANTONIO"),
        ("202323288", "CASTILLO DURAN VICTOR MANUEL"),
        ("202323306", "CASTRO CRUZ LUIS ALBERTO"),
        ("202323370", "CRUZ CASTILLO SERGIO URIEL"),
        ("202323261", "CRUZ HIDALGO DIANA"),
        ("202323695", "DE JESUS MARTINEZ TANIA"),
        ("202323251", "GARCÍA ALCÁNTARA CINTIA YAZMIN"),
        ("202323346", "GARCÍA BERMÚDEZ ÉRICK CHRISTOPHER"),
        ("202323100", "GRANADOS PEREZ EVELYN"),
        ("202323027", "GUERRERO GALINDO JIMENA"),
        ("202323193", "GUERRERO VIDAL LAZMIN"),
        ("202323083", "HERNÁNDEZ BLAS YULISSA"),
        ("202323053", "HERNÁNDEZ GUTIÉRREZ REBECA"),
        ("202323009", "HERNÁNDEZ LÓPEZ KEVIN YAEL"),
        ("202323376", "HERNÁNDEZ LUNA MAURICIO"),
        ("202323334", "JIMÉNEZ BOLAÑOS MARÍA FERNANDA"),
        ("202323070", "JIMÉNEZ VEGA KAREN ASUCENA"),
        ("202323130", "MARTINEZ ALLENDE SANDRA LIZBETH"),
        ("202323118", "MARTINEZ CHAVEZ CESAR ANTONIO"),
        ("202323117", "MARTINEZ MARTINEZ OSCAR EMILIO"),
        ("202323106", "MATÍAS CABRERA SALVADOR"),
        ("202323746", "MIRANDA VEGA MARÍA TERESA"),
        ("202323399", "MONTOYA GARCIA GAEL"),
        ("202323098", "NAVARRETE PÉREZ JOSÉ ARMANDO"),
        ("202323045", "NOLASCO LÓPEZ DIEGO ARTURO"),
        ("202323671", "OCAMPO RIVERA LUIS CARLOS"),
        ("202323880", "PICHARDO MIRANDA ALEXIS URIEL"),
        ("202323103", "RAMÍREZ GONZÁLEZ CESAR JAVIER")
    ]
    
    # Insertar estudiantes del grupo 3102 (N1)
    for matricula, nombre in estudiantes_3102:
        cursor.execute('''
        INSERT INTO usuarios (
            matricula, nombre_completo, rol, carrera_id, grupo_id, 
            semestre, salon, activo, email
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (matricula, nombre, "student", carrera_isc_id, grupo_3102_id, 4, "N1", True, f"{matricula}@tesji.edu.mx"))
    
    # Insertar estudiantes del grupo 3101 (N2)
    for matricula, nombre in estudiantes_3101:
        cursor.execute('''
        INSERT INTO usuarios (
            matricula, nombre_completo, rol, carrera_id, grupo_id, 
            semestre, salon, activo, email
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (matricula, nombre, "student", carrera_isc_id, grupo_3101_id, 4, "N2", True, f"{matricula}@tesji.edu.mx"))
    
    conn.commit()
    conn.close()
    print(f"✅ {len(estudiantes_3102)} estudiantes del grupo 3102 (N1) creados")
    print(f"✅ {len(estudiantes_3101)} estudiantes del grupo 3101 (N2) creados")

def create_horario_n1(db_path="tesji_rfid_system.db"):
    """Crea el horario específico del N1"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("⏰ Creando horario del N1...")
    
    # Obtener IDs necesarios
    cursor.execute('SELECT id FROM carreras WHERE codigo = "ISC"')
    carrera_isc_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM grupos WHERE codigo_grupo = "3102"')
    grupo_3102_id = cursor.fetchone()[0]
    
    # Mapeo de materias a IDs
    materias_map = {}
    materias_horario = [
        "Metodos numericos", "Ecuaciones diferenciales", "Arquitectura de computadoras",
        "Topicos avanzados de programacion", "Fundamentos de bases de datos", 
        "Taller de sistemas operativos", "Taller de etica"
    ]
    
    for materia_nombre in materias_horario:
        cursor.execute('''
        SELECT id FROM materias 
        WHERE LOWER(nombre) LIKE ? AND carrera_id = ? AND semestre = 4
        ''', (f"%{materia_nombre.lower()}%", carrera_isc_id))
        result = cursor.fetchone()
        if result:
            materias_map[materia_nombre] = result[0]
    
    # Horario del N1
    horarios = [
        # Lunes
        ("Metodos numericos", "Lunes", "07:00", "09:00", "Teoría"),
        ("Ecuaciones diferenciales", "Lunes", "09:00", "11:00", "Teoría"),
        ("Tutorías", "Lunes", "12:00", "14:00", "Tutoría"),
        
        # Martes
        ("Arquitectura de computadoras", "Martes", "11:00", "13:00", "Teoría"),
        ("Topicos avanzados de programacion", "Martes", "13:00", "14:00", "Práctica"),
        ("Fundamentos de bases de datos", "Martes", "14:00", "18:00", "Teoría"),
        
        # Miércoles
        ("Metodos numericos", "Miércoles", "07:00", "09:00", "Teoría"),
        ("Ecuaciones diferenciales", "Miércoles", "11:00", "13:00", "Teoría"),
        ("Taller de sistemas operativos", "Miércoles", "13:00", "15:00", "Práctica"),
        
        # Jueves
        ("Taller de etica", "Jueves", "10:00", "12:00", "Práctica"),
        ("Fundamentos de bases de datos", "Jueves", "12:00", "14:00", "Teoría"),
        ("Topicos avanzados de programacion", "Jueves", "14:00", "17:00", "Práctica"),
        
        # Viernes
        ("Taller de sistemas operativos", "Viernes", "07:00", "09:00", "Práctica"),
        ("Taller de etica", "Viernes", "09:00", "12:00", "Práctica"),
        ("Arquitectura de computadoras", "Viernes", "12:00", "15:00", "Teoría")
    ]
    
    for materia_nombre, dia, hora_inicio, hora_fin, tipo in horarios:
        materia_id = materias_map.get(materia_nombre)
        if materia_id:
            cursor.execute('''
            INSERT INTO horarios_detallados (
                materia_id, grupo_id, carrera_id, dia_semana, 
                hora_inicio, hora_fin, tipo_clase, activo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (materia_id, grupo_3102_id, carrera_isc_id, dia, hora_inicio, hora_fin, tipo, True))
    
    conn.commit()
    conn.close()
    print(f"✅ Horario del N1 creado con {len(horarios)} clases")

def create_admin_and_sample_teachers(db_path="tesji_rfid_system.db"):
    """Crea administrador y maestros de ejemplo"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("👨‍💼 Creando administrador y maestros...")
    
    # Obtener ID de carrera ISC
    cursor.execute('SELECT id FROM carreras WHERE codigo = "ISC"')
    carrera_isc_id = cursor.fetchone()[0]
    
    # Crear administrador
    admin_password = hash_password("admin123")
    cursor.execute('''
    INSERT INTO usuarios (
        uid, nombre_completo, matricula, email, password_hash, rol, activo
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        "ADMIN001",
        "Administrador del Sistema TESJI",
        "ADMIN001",
        "admin@tesji.edu.mx",
        admin_password,
        "admin",
        True
    ))
    
    # Crear maestros de ejemplo
    maestros = [
        {
            "uid": "PROF001",
            "nombre": "Ing. Rodolfo Guadalupe Alcántara Rosales",
            "matricula": "PROF001",
            "email": "rodolfo.alcantara@tesji.edu.mx",
            "especialidad": "Ecuaciones Diferenciales",
            "carrera_id": carrera_isc_id
        },
        {
            "uid": "PROF002",
            "nombre": "Lic. Juan Alberto Martínez Zamora",
            "matricula": "PROF002",
            "email": "juan.martinez@tesji.edu.mx",
            "especialidad": "Métodos Numéricos",
            "carrera_id": carrera_isc_id
        },
        {
            "uid": "PROF003",
            "nombre": "Víctor David Maya Arce",
            "matricula": "PROF003",
            "email": "victor.maya@tesji.edu.mx",
            "especialidad": "Programación",
            "carrera_id": carrera_isc_id
        },
        {
            "uid": "PROF004",
            "nombre": "Mtra. Yadira Esther Jiménez Pérez",
            "matricula": "PROF004",
            "email": "yadira.jimenez@tesji.edu.mx",
            "especialidad": "Base de Datos",
            "carrera_id": carrera_isc_id
        }
    ]
    
    password_hash = hash_password("123456")
    
    for maestro in maestros:
        cursor.execute('''
        INSERT INTO usuarios (
            uid, nombre_completo, matricula, email, password_hash, 
            rol, carrera_id, especialidad, activo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            maestro["uid"],
            maestro["nombre"],
            maestro["matricula"],
            maestro["email"],
            password_hash,
            "teacher",
            maestro["carrera_id"],
            maestro["especialidad"],
            True
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ Administrador y {len(maestros)} maestros creados")

def generate_final_report(db_path="tesji_rfid_system.db"):
    """Genera reporte final completo"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📊 SISTEMA TESJI COMPLETO - REPORTE FINAL")
    print("="*80)
    
    # Estadísticas generales
    cursor.execute("SELECT COUNT(*) FROM carreras WHERE activa = 1")
    total_carreras = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM materias WHERE activa = 1")
    total_materias = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'student' AND activo = 1")
    total_estudiantes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'teacher' AND activo = 1")
    total_maestros = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM grupos WHERE activo = 1")
    total_grupos = cursor.fetchone()[0]
    
    print(f"🎓 Carreras: {total_carreras}")
    print(f"📚 Materias: {total_materias}")
    print(f"👨‍🎓 Estudiantes: {total_estudiantes}")
    print(f"👨‍🏫 Maestros: {total_maestros}")
    print(f"📋 Grupos: {total_grupos}")
    
    # Estudiantes por grupo
    print("\n👥 ESTUDIANTES POR GRUPO:")
    cursor.execute('''
    SELECT g.nombre, g.salon, COUNT(u.id) as estudiantes
    FROM grupos g
    LEFT JOIN usuarios u ON g.id = u.grupo_id AND u.rol = 'student' AND u.activo = 1
    WHERE g.activo = 1
    GROUP BY g.id
    ORDER BY g.nombre
    ''')
    for nombre, salon, estudiantes in cursor.fetchall():
        print(f"   {nombre} (Salón {salon}): {estudiantes} estudiantes")
    
    # Materias por carrera
    print("\n📚 MATERIAS POR CARRERA:")
    cursor.execute('''
    SELECT c.nombre, COUNT(m.id) as materias
    FROM carreras c
    LEFT JOIN materias m ON c.id = m.carrera_id AND m.activa = 1
    WHERE c.activa = 1
    GROUP BY c.id
    ORDER BY c.nombre
    ''')
    for carrera, materias in cursor.fetchall():
        print(f"   {carrera}: {materias} materias")
    
    print("\n🔑 CREDENCIALES DEL SISTEMA:")
    print("   👨‍💼 Admin: admin / admin123")
    print("   👨‍🏫 Maestros: PROF001-PROF004 / 123456")
    print("   👨‍🎓 Estudiantes: Acceso por RFID (sin contraseña)")
    
    print("\n✅ FUNCIONALIDADES IMPLEMENTADAS:")
    print("   📋 Gestión completa de carreras y materias")
    print("   👥 Gestión de estudiantes con asignación automática")
    print("   👨‍🏫 Gestión de maestros con múltiples carreras")
    print("   ⏰ Sistema de horarios por grupo")
    print("   📊 Filtros por carrera y semestre")
    print("   🔧 Panel administrativo completo")
    
    print("\n🚀 SISTEMA LISTO PARA PRODUCCIÓN")
    print("="*80)
    
    conn.close()

def main():
    print("🏗️ RECONSTRUCTOR COMPLETO DEL SISTEMA TESJI")
    print("="*60)
    print("⚠️  ADVERTENCIA: Esto eliminará TODA la información existente")
    print("✨ Se creará un sistema completamente nuevo con todas las funcionalidades")
    
    try:
        print("\n🚀 Iniciando reconstrucción completa...")
        
        # 1. Eliminar base de datos existente
        delete_existing_database()
        
        # 2. Crear estructura mejorada
        create_enhanced_tables()
        
        # 3. Poblar datos básicos
        populate_all_carreras()
        populate_all_materias()
        
        # 4. Crear grupos y estudiantes
        create_grupos_isc()
        populate_estudiantes_reales()
        
        # 5. Crear horarios
        create_horario_n1()
        
        # 6. Crear usuarios del sistema
        create_admin_and_sample_teachers()
        
        # 7. Reporte final
        generate_final_report()
        
        print("\n🎉 ¡SISTEMA TESJI COMPLETAMENTE RECONSTRUIDO!")
        print("🔗 Ejecuta 'python unified_server.py' para iniciar el servidor")
        
    except Exception as e:
        print(f"❌ Error durante la reconstrucción: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
