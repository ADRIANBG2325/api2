#!/usr/bin/env python3
"""
Script para limpiar y configurar la base de datos con asignaciones de maestros
"""

import sqlite3
import os
from datetime import datetime

def setup_database():
    """Configura la base de datos con las tablas necesarias"""
    
    # Conectar a la base de datos
    db_path = "tesji_rfid_system.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Configurando base de datos...")
    
    try:
        # Crear tabla de asignaciones de maestros si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS asignaciones_maestro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            maestro_id INTEGER NOT NULL,
            materia_id INTEGER NOT NULL,
            grupo_id INTEGER NOT NULL,
            periodo TEXT NOT NULL DEFAULT '2024-1',
            activa BOOLEAN NOT NULL DEFAULT 1,
            fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (maestro_id) REFERENCES usuarios (id),
            FOREIGN KEY (materia_id) REFERENCES materias (id),
            FOREIGN KEY (grupo_id) REFERENCES grupos (id)
        )
        """)
        
        # Crear tabla de horarios detallados si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS horarios_detallados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            grupo_id INTEGER NOT NULL,
            dia_semana TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fin TEXT NOT NULL,
            tipo_clase TEXT DEFAULT 'Teoría',
            activo BOOLEAN NOT NULL DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (materia_id) REFERENCES materias (id),
            FOREIGN KEY (grupo_id) REFERENCES grupos (id)
        )
        """)
        
        # Limpiar usuarios de prueba excepto los esenciales
        cursor.execute("DELETE FROM usuarios WHERE uid LIKE 'TEST%' AND uid NOT IN ('TEST001', 'TEST002')")
        
        # Insertar maestros de ejemplo si no existen
        maestros_ejemplo = [
            ('PROF001', 'Dr. Juan Carlos Pérez López', 'PROF001', 'juan.perez@tesji.edu.mx', 'profesor123', 'teacher', 1, 'Programación y Bases de Datos'),
            ('PROF002', 'Lic. Juan Alberto Martínez Zamora', 'PROF002', 'juan.martinez@tesji.edu.mx', 'profesor123', 'teacher', 1, 'Métodos Numéricos'),
            ('PROF003', 'Ing. Rodolfo Guadalupe Alcántara Rosales', 'PROF003', 'rodolfo.alcantara@tesji.edu.mx', 'profesor123', 'teacher', 1, 'Ecuaciones Diferenciales'),
            ('PROF004', 'Mtra. Yadira Esther Jiménez Pérez', 'PROF004', 'yadira.jimenez@tesji.edu.mx', 'profesor123', 'teacher', 1, 'Fundamentos de Base de Datos'),
            ('PROF005', 'Víctor David Maya Arce', 'PROF005', 'victor.maya@tesji.edu.mx', 'profesor123', 'teacher', 1, 'Tópicos Avanzados de Programación')
        ]
        
        for uid, nombre, matricula, email, password, rol, carrera_id, especialidad in maestros_ejemplo:
            cursor.execute("""
            INSERT OR IGNORE INTO usuarios (uid, nombre_completo, matricula, email, password_hash, rol, carrera_id, especialidad, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (uid, nombre, matricula, email, f"salt:{password}", rol, carrera_id, especialidad))
        
        # Insertar materias de 4° semestre ISC si no existen
        materias_4to = [
            ('Métodos Numéricos', 'SCC-1017', 4, 4, 1),
            ('Ecuaciones Diferenciales', 'ACF-0905', 5, 4, 1),
            ('Fundamentos de Base de Datos', 'AEF-1031', 5, 4, 1),
            ('Tópicos Avanzados de Programación', 'SCD-1027', 5, 4, 1),
            ('Arquitectura de Computadoras', 'SCD-1003', 5, 4, 1),
            ('Taller de Sistemas Operativos', 'SCA-1026', 4, 4, 1),
            ('Taller de Ética', 'ACA-0907', 4, 4, 1),
            ('Inglés IV', 'ING-004', 2, 4, 1)
        ]
        
        for nombre, codigo, creditos, semestre, carrera_id in materias_4to:
            cursor.execute("""
            INSERT OR IGNORE INTO materias (nombre, codigo, creditos, semestre, carrera_id, activa)
            VALUES (?, ?, ?, ?, ?, 1)
            """, (nombre, codigo, creditos, semestre, carrera_id))
        
        # Crear grupos si no existen
        grupos = [
            ('Grupo 3402', 1, 4, '2024-1', 'N1', 'Matutino'),
            ('Grupo 3401', 1, 4, '2024-1', 'N2', 'Matutino')
        ]
        
        for nombre, carrera_id, semestre, periodo, salon, turno in grupos:
            cursor.execute("""
            INSERT OR IGNORE INTO grupos (nombre, carrera_id, semestre, periodo, salon, turno, activo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (nombre, carrera_id, semestre, periodo, salon, turno))
        
        # Crear asignaciones de ejemplo
        print("📚 Creando asignaciones de ejemplo...")
        
        # Obtener IDs de maestros y materias
        cursor.execute("SELECT id FROM usuarios WHERE matricula = 'PROF002'")  # Juan Alberto Martínez
        maestro_metodos = cursor.fetchone()
        
        cursor.execute("SELECT id FROM usuarios WHERE matricula = 'PROF003'")  # Rodolfo Alcántara
        maestro_ecuaciones = cursor.fetchone()
        
        cursor.execute("SELECT id FROM usuarios WHERE matricula = 'PROF004'")  # Yadira Jiménez
        maestro_bd = cursor.fetchone()
        
        cursor.execute("SELECT id FROM usuarios WHERE matricula = 'PROF005'")  # Víctor Maya
        maestro_topicos = cursor.fetchone()
        
        cursor.execute("SELECT id FROM materias WHERE codigo = 'SCC-1017'")  # Métodos Numéricos
        materia_metodos = cursor.fetchone()
        
        cursor.execute("SELECT id FROM materias WHERE codigo = 'ACF-0905'")  # Ecuaciones Diferenciales
        materia_ecuaciones = cursor.fetchone()
        
        cursor.execute("SELECT id FROM materias WHERE codigo = 'AEF-1031'")  # Fundamentos BD
        materia_bd = cursor.fetchone()
        
        cursor.execute("SELECT id FROM materias WHERE codigo = 'SCD-1027'")  # Tópicos Avanzados
        materia_topicos = cursor.fetchone()
        
        cursor.execute("SELECT id FROM grupos WHERE nombre = 'Grupo 3402'")  # Grupo N1
        grupo_3402 = cursor.fetchone()
        
        cursor.execute("SELECT id FROM grupos WHERE nombre = 'Grupo 3401'")  # Grupo N2
        grupo_3401 = cursor.fetchone()
        
        # Crear asignaciones
        asignaciones = []
        if all([maestro_metodos, materia_metodos, grupo_3402]):
            asignaciones.append((maestro_metodos[0], materia_metodos[0], grupo_3402[0], '2024-1'))
        
        if all([maestro_ecuaciones, materia_ecuaciones, grupo_3402]):
            asignaciones.append((maestro_ecuaciones[0], materia_ecuaciones[0], grupo_3402[0], '2024-1'))
        
        if all([maestro_bd, materia_bd, grupo_3402]):
            asignaciones.append((maestro_bd[0], materia_bd[0], grupo_3402[0], '2024-1'))
        
        if all([maestro_topicos, materia_topicos, grupo_3402]):
            asignaciones.append((maestro_topicos[0], materia_topicos[0], grupo_3402[0], '2024-1'))
        
        for maestro_id, materia_id, grupo_id, periodo in asignaciones:
            cursor.execute("""
            INSERT OR IGNORE INTO asignaciones_maestro (maestro_id, materia_id, grupo_id, periodo, activa)
            VALUES (?, ?, ?, ?, 1)
            """, (maestro_id, materia_id, grupo_id, periodo))
        
        conn.commit()
        print("✅ Base de datos configurada exitosamente")
        print(f"   - Maestros creados: {len(maestros_ejemplo)}")
        print(f"   - Materias creadas: {len(materias_4to)}")
        print(f"   - Grupos creados: {len(grupos)}")
        print(f"   - Asignaciones creadas: {len(asignaciones)}")
        
    except Exception as e:
        print(f"❌ Error configurando base de datos: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    setup_database()
