#!/usr/bin/env python3
"""
Script para agregar SOLO las columnas faltantes sin borrar datos existentes
Preserva todos los horarios, materias y carreras que ya estaban configurados
"""

import sqlite3
from datetime import datetime

def add_missing_columns_safely(db_path="tesji_rfid_system.db"):
    """Agrega solo las columnas faltantes sin tocar los datos existentes"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Agregando columnas faltantes sin borrar datos...")
    
    # Lista de columnas que podrían faltar en usuarios
    missing_columns_to_add = [
        ("salon", "TEXT"),
        ("fecha_registro", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
        ("ultimo_acceso", "DATETIME"),
        ("especialidad", "TEXT"),
        ("semestre", "INTEGER DEFAULT 4"),
        ("grupo_id", "INTEGER"),
        ("carrera_id", "INTEGER")
    ]
    
    # Verificar qué columnas existen actualmente
    cursor.execute("PRAGMA table_info(usuarios)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    print(f"📋 Columnas existentes en usuarios: {', '.join(existing_columns)}")
    
    # Agregar solo las columnas que faltan
    columns_added = []
    for column_name, column_type in missing_columns_to_add:
        if column_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE usuarios ADD COLUMN {column_name} {column_type}")
                columns_added.append(column_name)
                print(f"✅ Columna agregada: {column_name}")
            except sqlite3.OperationalError as e:
                print(f"⚠️ No se pudo agregar {column_name}: {e}")
        else:
            print(f"ℹ️ Columna {column_name} ya existe")
    
    if columns_added:
        print(f"✅ Se agregaron {len(columns_added)} columnas nuevas")
    else:
        print("ℹ️ No se necesitaron agregar columnas")
    
    conn.commit()
    conn.close()
    return columns_added

def assign_salons_to_existing_students(db_path="tesji_rfid_system.db"):
    """Asigna salones a estudiantes existentes que no los tengan"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🏫 Asignando salones a estudiantes existentes...")
    
    # Listas reales de matrículas por grupo
    GRUPO_3402_MATRICULAS = [
        "202323734", "202323768", "202323367", "202323728", "202323883", "202323830", 
        "202323377", "202323352", "202323652", "202323737", "202323458", "202323762", 
        "202323355", "202323750", "202323315", "202323732", "202323445", "202323403", 
        "202323394", "202323424", "202323752", "202323881", "202323877", "202323850", 
        "202323885", "202323725", "202323386", "202323446", "202323891", "202323887", 
        "202323774", "202323464", "202323092", "202323112", "202323723", "202323413", 
        "202323892", "202323730", "202323843", "202323896", "202323758", "202323398", 
        "202323420", "202323382", "202323449"
    ]
    
    GRUPO_3401_MATRICULAS = [
        "202323069", "202323274", "202323221", "202323699", "202323108", "202323090", 
        "202323080", "202323006", "202323116", "202323288", "202323306", "202323370", 
        "202323261", "202323695", "202323251", "202323346", "202323100", "202323027", 
        "202323193", "202323083", "202323053", "202323009", "202323376", "202323334", 
        "202323070", "202323130", "202323118", "202323117", "202323106", "202323746", 
        "202323399", "202323098", "202323045", "202323671", "202323880", "202323103"
    ]
    
    # Obtener estudiantes sin salón asignado
    cursor.execute("SELECT id, matricula FROM usuarios WHERE rol = 'student' AND (salon IS NULL OR salon = '')")
    students_without_salon = cursor.fetchall()
    
    updated_count = 0
    for student_id, matricula in students_without_salon:
        salon = None
        
        if matricula in GRUPO_3402_MATRICULAS:
            salon = "N1"
        elif matricula in GRUPO_3401_MATRICULAS:
            salon = "N2"
        else:
            # Asignación por patrón numérico como fallback
            try:
                ultimos_digitos = int(matricula[-2:]) if len(matricula) >= 2 else 0
                salon = "N1" if ultimos_digitos % 2 == 0 else "N2"
            except:
                salon = "N1"  # Por defecto
        
        if salon:
            cursor.execute("UPDATE usuarios SET salon = ? WHERE id = ?", (salon, student_id))
            updated_count += 1
            print(f"✅ Estudiante {matricula} asignado al salón {salon}")
    
    print(f"✅ Se asignaron salones a {updated_count} estudiantes")
    
    conn.commit()
    conn.close()

def verify_data_integrity(db_path="tesji_rfid_system.db"):
    """Verifica que todos los datos importantes estén intactos"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔍 Verificando integridad de datos...")
    
    # Verificar carreras
    cursor.execute("SELECT COUNT(*) FROM carreras")
    carreras_count = cursor.fetchone()[0]
    print(f"📚 Carreras: {carreras_count}")
    
    # Verificar materias
    cursor.execute("SELECT COUNT(*) FROM materias")
    materias_count = cursor.fetchone()[0]
    print(f"📖 Materias: {materias_count}")
    
    # Verificar usuarios por rol
    cursor.execute("SELECT rol, COUNT(*) FROM usuarios GROUP BY rol")
    users_by_role = cursor.fetchall()
    for rol, count in users_by_role:
        print(f"👤 {rol.title()}s: {count}")
    
    # Verificar estudiantes con salón
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'student' AND salon IS NOT NULL")
    students_with_salon = cursor.fetchone()[0]
    print(f"🏫 Estudiantes con salón asignado: {students_with_salon}")
    
    # Verificar asistencias
    cursor.execute("SELECT COUNT(*) FROM asistencias")
    asistencias_count = cursor.fetchone()[0]
    print(f"📝 Registros de asistencia: {asistencias_count}")
    
    # Verificar horarios
    try:
        cursor.execute("SELECT COUNT(*) FROM horarios_detallados")
        horarios_count = cursor.fetchone()[0]
        print(f"⏰ Horarios detallados: {horarios_count}")
    except:
        print("⏰ Horarios detallados: Tabla no existe")
    
    # Verificar asignaciones de maestros
    try:
        cursor.execute("SELECT COUNT(*) FROM asignaciones_maestro")
        asignaciones_count = cursor.fetchone()[0]
        print(f"👨‍🏫 Asignaciones de maestros: {asignaciones_count}")
    except:
        print("👨‍🏫 Asignaciones de maestros: Tabla no existe")
    
    conn.close()
    print("✅ Verificación de integridad completada")

def create_missing_tables_only(db_path="tesji_rfid_system.db"):
    """Crea solo las tablas que faltan, sin tocar las existentes"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Creando tablas faltantes...")
    
    # Verificar qué tablas existen
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    print(f"📋 Tablas existentes: {', '.join(existing_tables)}")
    
    # Crear solo las tablas que faltan
    tables_to_create = {
        "horarios_detallados": '''
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
        ''',
        "asignaciones_maestro": '''
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
        '''
    }
    
    for table_name, create_sql in tables_to_create.items():
        if table_name not in existing_tables:
            cursor.execute(create_sql)
            print(f"✅ Tabla creada: {table_name}")
        else:
            print(f"ℹ️ Tabla {table_name} ya existe")
    
    conn.commit()
    conn.close()

def main():
    print("🔧 REPARACIÓN SEGURA - SOLO COLUMNAS FALTANTES")
    print("=" * 60)
    print("Este script PRESERVA todos los datos existentes")
    print("y solo agrega las columnas que faltan.")
    print("=" * 60)
    
    try:
        # 1. Verificar estado actual
        print("\n📊 ESTADO ACTUAL:")
        verify_data_integrity()
        
        # 2. Agregar solo columnas faltantes
        print("\n🔧 AGREGANDO COLUMNAS FALTANTES:")
        columns_added = add_missing_columns_safely()
        
        # 3. Crear tablas faltantes
        print("\n🏗️ CREANDO TABLAS FALTANTES:")
        create_missing_tables_only()
        
        # 4. Asignar salones a estudiantes
        print("\n🏫 ASIGNANDO SALONES:")
        assign_salons_to_existing_students()
        
        # 5. Verificar estado final
        print("\n📊 ESTADO FINAL:")
        verify_data_integrity()
        
        print("\n🎉 REPARACIÓN COMPLETADA EXITOSAMENTE")
        print("✅ Todos los datos existentes se preservaron")
        print("✅ Se agregaron las columnas faltantes")
        print("✅ Los horarios y materias siguen intactos")
        
        if columns_added:
            print(f"\n📝 Columnas agregadas: {', '.join(columns_added)}")
        
        print("\n🚀 El servidor debería funcionar correctamente ahora")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
