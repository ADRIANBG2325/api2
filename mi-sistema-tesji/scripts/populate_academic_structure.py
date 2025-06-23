#!/usr/bin/env python3
"""
Script para poblar la base de datos con la estructura académica completa del TESJI
Incluye todas las carreras, semestres y materias
"""

import sqlite3
import json
from datetime import datetime

# Estructura académica completa del TESJI
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
            ],
            5: [
                "Lenguajes y Autómatas I",
                "Redes de Computadoras",
                "Taller de Base de Datos",
                "Simulación",
                "Fundamentos de Ingeniería de Software",
                "Lenguaje de Interfaz",
                "Contabilidad Financiera"
            ],
            6: [
                "Lenguajes y Autómatas II",
                "Administración de Redes",
                "Administración de Bases de Datos",
                "Programación Web",
                "Ingeniería de Software",
                "Sistemas Programables"
            ],
            7: [
                "Programación Lógica y Funcional",
                "Comunicación y Enrutamiento de Redes de Datos",
                "Taller de Investigación I",
                "Desarrollo de Aplicaciones para Dispositivos Móviles",
                "Gestión de Proyectos de Software",
                "Internet de las Cosas",
                "Graficación"
            ],
            8: [
                "Inteligencia Artificial",
                "Ciberseguridad",
                "Taller de Investigación II",
                "Programación Reactiva",
                "Sistemas Distribuidos",
                "Cultura Empresarial"
            ],
            9: [
                "Residencias Profesionales"
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
            ],
            2: [
                "Electricidad y Electrónica Industrial",
                "Propiedades de Materiales",
                "Cálculo Integral",
                "Análisis de la Realidad Nacional",
                "Taller de Liderazgo"
            ],
            3: [
                "Metodología y Normalización",
                "Álgebra Lineal",
                "Cálculo Vectorial",
                "Economía",
                "Estadística Inferencial I",
                "Estudio de Trabajo I",
                "Higiene y Seguridad Industrial"
            ],
            4: [
                "Procesos de Fabricación",
                "Física",
                "Algoritmos y Lenguajes de Programación",
                "Investigación de Operaciones I",
                "Estadística Inferencial II",
                "Estudio de Trabajo II",
                "Desarrollo Sustentable"
            ],
            5: [
                "Administración de Proyectos",
                "Gestión de Costos",
                "Administración de Operaciones I",
                "Investigación de Operaciones II",
                "Control Estadístico de la Calidad",
                "Ergonomía"
            ],
            6: [
                "Taller de Investigación I",
                "Investigación de Operaciones",
                "Administración de Operaciones II",
                "Simulación",
                "Administración del Mantenimiento",
                "Mercadotecnia"
            ],
            7: [
                "Taller de Investigación II",
                "Planeación Financiera",
                "Planeación y Diseño de Instalaciones",
                "Sistemas de Manufactura",
                "Logística y Cadenas de Suministro",
                "Gestión de los Sistemas de Calidad",
                "Ingeniería de Sistemas"
            ],
            8: [
                "Formulación y Evaluación de Proyectos",
                "Relaciones Industriales"
            ],
            9: [
                "Residencias Profesionales",
                "Especialidad"
            ]
        }
    },
    "Ingeniería Mecatrónica": {
        "codigo": "IM",
        "semestres": 9,
        "materias": {
            1: [
                "Química",
                "Cálculo Diferencial",
                "Taller de Ética",
                "Dibujo Asistido por Computadora",
                "Metodología y Normalización",
                "Fundamentos de Investigación"
            ],
            2: [
                "Cálculo Integral",
                "Álgebra Lineal",
                "Ciencia e Ingeniería de los Materiales",
                "Estadística y Control de Calidad",
                "Programación Básica",
                "Administración y Contabilidad",
                "Taller de Investigación I"
            ],
            3: [
                "Cálculo Vectorial",
                "Procesos de Fabricación",
                "Electromagnetismo",
                "Estática",
                "Métodos Numéricos",
                "Desarrollo Sustentable",
                "Taller de Investigación II"
            ],
            4: [
                "Ecuaciones Diferenciales",
                "Fundamentos de Termodinámica",
                "Mecánica de Materiales",
                "Dinámica",
                "Análisis de Circuitos Electrónicos",
                "Electrónica Analógica"
            ],
            5: [
                "Máquinas Eléctricas",
                "Mecanismos",
                "Análisis de Fluidos",
                "Electrónica Digital",
                "Programación Avanzada",
                "Circuitos Hidráulicos y Neumáticos"
            ],
            6: [
                "Electrónica de Potencia Aplicada",
                "Instrumentación",
                "Diseño de Elementos Mecánicos",
                "Vibraciones Mecánicas",
                "Dinámica de Sistemas"
            ],
            7: [
                "Mantenimiento",
                "Manufactura Avanzada",
                "Microcontroladores",
                "Control",
                "Manufactura Integrada por Computadora",
                "Diseño Avanzado y Manufactura"
            ],
            8: [
                "Formulación y Evaluación de Proyectos",
                "Controladores Lógicos Programables",
                "Robótica",
                "Control Robótico",
                "Automatización Industrial",
                "Instrumentación Avanzada"
            ],
            9: [
                "Residencia Profesional"
            ]
        }
    },
    "Ingeniería Civil": {
        "codigo": "IC",
        "semestres": 9,
        "materias": {
            1: [
                "Fundamentos de Investigación",
                "Cálculo Diferencial",
                "Taller de Ética",
                "Química",
                "Software en Ingeniería Civil",
                "Dibujo en Ingeniería Civil",
                "Tutorías",
                "Taller de Matemáticas I"
            ],
            2: [
                "Cálculo Vectorial",
                "Geología",
                "Probabilidad y Estadística",
                "Topografía",
                "Materiales y Procesos Constructivos",
                "Cálculo Integral",
                "Tutorías II",
                "Taller de Matemáticas II"
            ],
            3: [
                "Estática",
                "Ecuaciones Diferenciales",
                "Álgebra Lineal",
                "Carreteras",
                "Tecnología del Concreto",
                "Sistemas de Transporte",
                "Tutorías III"
            ],
            4: [
                "Fundamentos de Mecánica de los Medios Continuos",
                "Métodos Numéricos",
                "Mecánica de Suelos",
                "Maquinaria Pesada y Movimiento de Tierra",
                "Dinámica",
                "Modelos de Optimización de Recursos",
                "Tutorías IV"
            ],
            5: [
                "Mecánica de Materiales",
                "Desarrollo Sustentable",
                "Mecánica de Suelos Aplicada",
                "Costos y Presupuestos",
                "Taller de Investigación I",
                "Hidráulica Básica",
                "Servicio Social"
            ],
            6: [
                "Análisis Estructural",
                "Instalaciones de los Edificios",
                "Diseño y Construcción de Pavimentos",
                "Administración de la Construcción",
                "Hidrología Superficial",
                "Hidráulica de Canales",
                "Servicio Social"
            ],
            7: [
                "Análisis Estructural Avanzado",
                "Diseño de Elementos de Concreto Reforzado",
                "Taller de Investigación II",
                "Abastecimiento de Agua",
                "Topografía de Obras",
                "Normatividad y Seguridad en la Construcción",
                "Planeación y Control de Obra"
            ],
            8: [
                "Diseño Estructural de Cimentaciones",
                "Diseño de Elementos de Acero",
                "Formulación y Evaluación de Proyectos",
                "Alcantarillado",
                "Construcción Pesada",
                "Construcción de Estructuras de Concreto",
                "Construcción de Estructuras de Acero"
            ],
            9: [
                "Residencia Profesional"
            ]
        }
    },
    "Licenciatura en Administración": {
        "codigo": "LA",
        "semestres": 9,
        "materias": {
            1: [
                "Teoría General de la Administración",
                "Informática para la Administración",
                "Taller de Ética",
                "Fundamentos de Investigación",
                "Matemáticas Aplicadas a la Administración",
                "Contabilidad General"
            ],
            2: [
                "Función Administrativa I",
                "Estadística para la Administración I",
                "Derecho Laboral y Seguridad Social",
                "Comunicación Corporativa",
                "Taller de Desarrollo Humano",
                "Costos de Manufactura"
            ],
            3: [
                "Función Administrativa II",
                "Estadística para la Administración II",
                "Derecho Empresarial",
                "Comportamiento Organizacional",
                "Dinámica Social",
                "Contabilidad Administrativa"
            ],
            4: [
                "Gestión Estratégica del Capital Humano I",
                "Procesos Estructurales",
                "Métodos Cuantitativos para la Administración",
                "Fundamentos de Mercadotecnia",
                "Economía Empresarial",
                "Matemáticas Financieras"
            ],
            5: [
                "Gestión Estratégica del Capital Humano II",
                "Derecho Fiscal",
                "Mezcla de Mercadotecnia",
                "Macroeconomía",
                "Administración Financiera I",
                "Desarrollo Sustentable"
            ],
            6: [
                "Gestión de la Retribución",
                "Producción",
                "Taller de Investigación I",
                "Sistema de Información de Mercadotecnia",
                "Innovación y Emprendedurismo",
                "Administración Financiera II"
            ],
            7: [
                "Plan de Negocios",
                "Procesos de Dirección",
                "Taller de Investigación II",
                "Administración de la Calidad",
                "Economía Internacional",
                "Diagnósticos y Evaluación Empresarial"
            ],
            8: [
                "Consultoría Empresarial",
                "Formulación y Evaluación de Proyectos",
                "Desarrollo Organizacional"
            ],
            9: [
                "Residencia Profesional",
                "Especialidad"
            ]
        }
    },
    "Ingeniería Química": {
        "codigo": "IQ",
        "semestres": 9,
        "materias": {
            1: [
                "Taller de Ética",
                "Fundamentos de Investigación",
                "Cálculo Diferencial",
                "Química Inorgánica",
                "Programación",
                "Dibujo Asistido por Computadora"
            ],
            2: [
                "Álgebra Lineal",
                "Mecánica Clásica",
                "Cálculo Integral",
                "Química Orgánica I",
                "Termodinámica",
                "Química Analítica"
            ],
            3: [
                "Análisis de Datos Experimentales",
                "Electricidad, Magnetismo y Óptica",
                "Cálculo Vectorial",
                "Química Orgánica II",
                "Balance de Materia y Energía",
                "Gestión de Calidad"
            ],
            4: [
                "Métodos Numéricos",
                "Ecuaciones Diferenciales",
                "Mecanismos de Transferencia",
                "Ingeniería Ambiental",
                "Fisicoquímica I",
                "Análisis Instrumental"
            ],
            5: [
                "Taller de Investigación I",
                "Procesos de Separación I",
                "Laboratorio Integral I",
                "Reactores Químicos"
            ],
            6: [
                "Taller de Investigación I",
                "Procesos de Separación II",
                "Laboratorio Integral I",
                "Reactores Químicos"
            ],
            7: [
                "Taller de Administración",
                "Taller de Investigación II",
                "Procesos de Separación III",
                "Salud y Seguridad en el Trabajo",
                "Laboratorio Integral II"
            ],
            8: [
                "Laboratorio Integral III",
                "Instrumentación y Control",
                "Ingeniería de Proyectos",
                "Simulación de Procesos"
            ],
            9: [
                "Residencia Profesional",
                "Especialidad"
            ]
        }
    },
    "Ingeniería en Logística": {
        "codigo": "IL",
        "semestres": 9,
        "materias": {
            1: [
                "Introducción a la Ingeniería Logística",
                "Cálculo Diferencial",
                "Química",
                "Fundamentos de Administración",
                "Dibujo Asistido por Computadora",
                "Economía"
            ],
            2: [
                "Taller de Ética",
                "Cálculo Integral",
                "Probabilidad y Estadística",
                "Desarrollo Humano y Organización",
                "Contabilidad y Costos"
            ],
            3: [
                "Cadena de Suministro",
                "Álgebra Lineal",
                "Estadística Inferencial I",
                "Fundamentos de Derecho",
                "Mecánica Clásica",
                "Finanzas"
            ],
            4: [
                "Compras",
                "Tipología del Producto",
                "Estadística Inferencial II",
                "Entorno Económico",
                "Tópicos de Ingeniería Mecánica",
                "Bases de Datos"
            ],
            5: [
                "Almacenes",
                "Inventarios",
                "Investigación de Operaciones I",
                "Higiene y Seguridad",
                "Procesos de Fabricación y Manejo de Materiales",
                "Mercadotecnia"
            ],
            6: [
                "Tráfico y Transporte",
                "Cultura de Calidad",
                "Investigación de Operaciones II",
                "Desarrollo Sustentable",
                "Taller de Investigación I",
                "Empaque, Envase y Embalaje"
            ],
            7: [
                "Servicio al Cliente",
                "Programación de Procesos Productivos",
                "Modelos de Simulación y Logística",
                "Legislación Aduanera",
                "Taller de Investigación II",
                "Ingeniería Económica"
            ],
            8: [
                "Innovación",
                "Comercio Internacional",
                "Formulación y Evaluación de Proyectos",
                "Geografía para el Transporte"
            ],
            9: [
                "Residencia Profesional",
                "Especialidad",
                "Gestión de Proyectos"
            ]
        }
    },
    "Ingeniería en Tecnologías de la Información y Comunicaciones": {
        "codigo": "ITIC",
        "semestres": 9,
        "materias": {
            1: [
                "Cálculo Diferencial",
                "Fundamentos de Programación",
                "Matemáticas Discretas I",
                "Fundamentos de Redes",
                "Telecomunicaciones",
                "Introducción a las TIC's"
            ],
            2: [
                "Cálculo Integral",
                "Programación Orientada a Objetos",
                "Matemáticas Discretas II",
                "Redes de Comunicación",
                "Probabilidad y Estadística",
                "Arquitectura de Computadoras"
            ],
            3: [
                "Matemáticas Aplicadas a Comunicaciones",
                "Estructura y Organización de Datos",
                "Sistemas Operativos I",
                "Fundamentos de Bases de Datos",
                "Electricidad y Magnetismo",
                "Álgebra Lineal"
            ],
            4: [
                "Análisis de Señales y Sistemas de Comunicación",
                "Programación II",
                "Sistemas Operativos II",
                "Taller de Bases de Datos",
                "Circuitos Eléctricos y Electrónicos",
                "Ingeniería de Software"
            ],
            5: [
                "Fundamentos de Investigación",
                "Redes Emergentes",
                "Contabilidad y Costos",
                "Bases de Datos Distribuidas",
                "Taller de Ingeniería de Software",
                "Ciberseguridad"
            ],
            6: [
                "Taller de Investigación I",
                "Programación Web",
                "Administración General",
                "Administración y Seguridad de Redes",
                "Desarrollo de Aplicaciones para Dispositivos Móviles",
                "Interacción Humano Computadora",
                "Desarrollo de Emprendedores"
            ],
            7: [
                "Taller de Investigación II",
                "Negocios Electrónicos I",
                "Matemáticas para la Toma de Decisiones",
                "Tecnología Inalámbrica",
                "Desarrollo de Aplicaciones de Realidad Aumentada",
                "Internet de las Cosas"
            ],
            8: [
                "Administración de Proyectos",
                "Negocios Electrónicos II",
                "Desarrollo Sustentable",
                "Auditoría en Tecnologías de la Información",
                "Ingeniería del Conocimiento",
                "Herramientas para el Análisis de Datos Masivos (BIG DATA)",
                "Cómputo en la Nube"
            ],
            9: [
                "Taller de Ética",
                "Residencia Profesional"
            ]
        }
    }
}

def create_academic_tables(db_path="tesji_rfid_system.db"):
    """Crea las tablas necesarias para la estructura académica"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
    
    conn.commit()
    conn.close()
    print("✅ Tablas académicas creadas/actualizadas exitosamente")

def populate_academic_data(db_path="tesji_rfid_system.db"):
    """Pobla la base de datos con la estructura académica completa"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📚 Poblando estructura académica del TESJI...")
    
    for carrera_nombre, carrera_data in ACADEMIC_STRUCTURE.items():
        print(f"   📖 Procesando: {carrera_nombre}")
        
        # Insertar carrera
        cursor.execute('''
        INSERT OR IGNORE INTO carreras (nombre, codigo, semestres)
        VALUES (?, ?, ?)
        ''', (carrera_nombre, carrera_data["codigo"], carrera_data["semestres"]))
        
        # Obtener ID de la carrera
        cursor.execute('SELECT id FROM carreras WHERE nombre = ?', (carrera_nombre,))
        result = cursor.fetchone()
        if result:
            carrera_id = result[0]
            
            # Insertar materias por semestre
            for semestre, materias in carrera_data["materias"].items():
                for materia_nombre in materias:
                    # Generar código de materia
                    codigo_materia = f"{carrera_data['codigo']}-{semestre:02d}-{len(materia_nombre.split())}"
                    
                    cursor.execute('''
                    INSERT OR IGNORE INTO materias (nombre, carrera_id, semestre, codigo)
                    VALUES (?, ?, ?, ?)
                    ''', (materia_nombre, carrera_id, semestre, codigo_materia))
            
            # Crear grupos por defecto para cada semestre
            for semestre in range(1, carrera_data["semestres"] + 1):
                grupo_nombre = f"{carrera_data['codigo']}-{semestre:02d}01"
                cursor.execute('''
                INSERT OR IGNORE INTO grupos (nombre, carrera_id, semestre, periodo)
                VALUES (?, ?, ?, ?)
                ''', (grupo_nombre, carrera_id, semestre, "2024-2025"))
    
    conn.commit()
    conn.close()
    print("✅ Estructura académica poblada exitosamente")

def main():
    print("🏫 CONFIGURADOR DE ESTRUCTURA ACADÉMICA TESJI")
    print("="*50)
    
    try:
        # 1. Crear tablas
        create_academic_tables()
        
        # 2. Poblar datos académicos
        populate_academic_data()
        
        print("\n🎉 CONFIGURACIÓN ACADÉMICA COMPLETADA")
        print("✅ El sistema TESJI está listo con toda la estructura académica")
        
        # Verificar datos
        conn = sqlite3.connect("tesji_rfid_system.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM carreras")
        total_carreras = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM materias")
        total_materias = cursor.fetchone()[0]
        
        print(f"\n📊 RESUMEN:")
        print(f"   🎓 Carreras: {total_carreras}")
        print(f"   📚 Materias: {total_materias}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
