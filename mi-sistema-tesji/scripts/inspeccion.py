#!/usr/bin/env python3
"""
Inspector completo de base de datos TESJI
Este script analiza toda la estructura y contenido de la base de datos
"""

import sqlite3
import json
from datetime import datetime
import os

def inspect_database(db_path="tesji_rfid_system.db"):
    """Inspecciona completamente la base de datos"""
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔍 INSPECTOR DE BASE DE DATOS TESJI")
    print("=" * 80)
    print(f"📁 Archivo: {db_path}")
    print(f"📅 Fecha de inspección: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 1. OBTENER TODAS LAS TABLAS
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📋 TABLAS ENCONTRADAS: {len(tables)}")
    print("-" * 40)
    for i, table in enumerate(tables, 1):
        print(f"{i:2d}. {table}")
    
    # 2. ANALIZAR CADA TABLA
    for table_name in tables:
        print(f"\n" + "="*60)
        print(f"🔍 TABLA: {table_name.upper()}")
        print("="*60)
        
        # Estructura de la tabla
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\n📊 ESTRUCTURA ({len(columns)} columnas):")
        print("-" * 50)
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            pk_text = " [PK]" if pk else ""
            null_text = " NOT NULL" if not_null else ""
            default_text = f" DEFAULT {default_val}" if default_val else ""
            print(f"  {col_name:<20} {col_type:<15}{pk_text}{null_text}{default_text}")
        
        # Contar registros
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_records = cursor.fetchone()[0]
        
        print(f"\n📈 REGISTROS: {total_records}")
        
        if total_records > 0:
            # Mostrar algunos registros de ejemplo
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            sample_records = cursor.fetchall()
            
            if sample_records:
                print(f"\n📝 MUESTRA DE DATOS (primeros 5 registros):")
                print("-" * 50)
                
                # Headers
                column_names = [desc[0] for desc in cursor.description]
                header = " | ".join(f"{name:<15}" for name in column_names)
                print(header)
                print("-" * len(header))
                
                # Data rows
                for record in sample_records:
                    row = " | ".join(f"{str(val):<15}" for val in record)
                    print(row)
        
        # Análisis específico por tabla
        analyze_table_specific(cursor, table_name, total_records)
    
    # 3. ANÁLISIS DE RELACIONES
    print(f"\n" + "="*80)
    print("🔗 ANÁLISIS DE RELACIONES")
    print("="*80)
    analyze_relationships(cursor)
    
    # 4. PROBLEMAS POTENCIALES
    print(f"\n" + "="*80)
    print("⚠️ DIAGNÓSTICO DE PROBLEMAS")
    print("="*80)
    diagnose_problems(cursor)
    
    # 5. RESUMEN EJECUTIVO
    print(f"\n" + "="*80)
    print("📊 RESUMEN EJECUTIVO")
    print("="*80)
    generate_summary(cursor, tables)
    
    conn.close()

def analyze_table_specific(cursor, table_name, total_records):
    """Análisis específico por tipo de tabla"""
    
    if table_name == "usuarios":
        print(f"\n🔍 ANÁLISIS ESPECÍFICO - USUARIOS:")
        
        # Por rol
        cursor.execute("SELECT rol, COUNT(*) FROM usuarios GROUP BY rol")
        roles = cursor.fetchall()
        for rol, count in roles:
            print(f"  - {rol}: {count}")
        
        # Usuarios con UID
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE uid IS NOT NULL AND uid != ''")
        with_uid = cursor.fetchone()[0]
        print(f"  - Con UID: {with_uid}")
        
        # Usuarios activos
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 1")
        active = cursor.fetchone()[0]
        print(f"  - Activos: {active}")
    
    elif table_name == "grupos":
        print(f"\n🔍 ANÁLISIS ESPECÍFICO - GRUPOS:")
        
        # Por carrera
        cursor.execute("""
        SELECT c.nombre, COUNT(g.id) 
        FROM grupos g 
        LEFT JOIN carreras c ON g.carrera_id = c.id 
        GROUP BY c.nombre
        """)
        by_career = cursor.fetchall()
        for career, count in by_career:
            career_name = career or "Sin carrera"
            print(f"  - {career_name}: {count}")
        
        # Estudiantes por grupo
        cursor.execute("""
        SELECT g.nombre, COUNT(u.id) as estudiantes
        FROM grupos g 
        LEFT JOIN usuarios u ON g.id = u.grupo_id AND u.rol = 'student'
        GROUP BY g.id, g.nombre
        ORDER BY estudiantes DESC
        """)
        students_per_group = cursor.fetchall()
        print(f"  📚 Estudiantes por grupo:")
        for group_name, student_count in students_per_group:
            print(f"    - {group_name}: {student_count} estudiantes")
    
    elif table_name == "materias":
        print(f"\n🔍 ANÁLISIS ESPECÍFICO - MATERIAS:")
        
        # Por semestre
        cursor.execute("SELECT semestre, COUNT(*) FROM materias GROUP BY semestre ORDER BY semestre")
        by_semester = cursor.fetchall()
        for semester, count in by_semester:
            print(f"  - Semestre {semester}: {count}")
        
        # Por carrera
        cursor.execute("""
        SELECT c.nombre, COUNT(m.id) 
        FROM materias m 
        LEFT JOIN carreras c ON m.carrera_id = c.id 
        GROUP BY c.nombre
        """)
        by_career = cursor.fetchall()
        for career, count in by_career:
            career_name = career or "Sin carrera"
            print(f"  - {career_name}: {count}")
    
    elif table_name == "asistencias":
        print(f"\n🔍 ANÁLISIS ESPECÍFICO - ASISTENCIAS:")
        
        # Por fecha
        cursor.execute("""
        SELECT DATE(fecha) as dia, COUNT(*) 
        FROM asistencias 
        GROUP BY DATE(fecha) 
        ORDER BY dia DESC 
        LIMIT 7
        """)
        by_date = cursor.fetchall()
        print(f"  📅 Últimos 7 días:")
        for date, count in by_date:
            print(f"    - {date}: {count}")
        
        # Presentes vs ausentes
        cursor.execute("SELECT presente, COUNT(*) FROM asistencias GROUP BY presente")
        attendance = cursor.fetchall()
        for present, count in attendance:
            status = "Presentes" if present else "Ausentes"
            print(f"  - {status}: {count}")

def analyze_relationships(cursor):
    """Analiza las relaciones entre tablas"""
    
    print("\n🔗 Relaciones encontradas:")
    
    # Usuarios sin grupo
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE grupo_id IS NULL AND rol = 'student'")
    students_no_group = cursor.fetchone()[0]
    if students_no_group > 0:
        print(f"  ⚠️ Estudiantes sin grupo: {students_no_group}")
    
    # Grupos sin estudiantes
    cursor.execute("""
    SELECT COUNT(*) FROM grupos g 
    WHERE NOT EXISTS (SELECT 1 FROM usuarios u WHERE u.grupo_id = g.id AND u.rol = 'student')
    """)
    empty_groups = cursor.fetchone()[0]
    if empty_groups > 0:
        print(f"  ⚠️ Grupos sin estudiantes: {empty_groups}")
    
    # Materias sin asignaciones
    cursor.execute("""
    SELECT COUNT(*) FROM materias m 
    WHERE NOT EXISTS (SELECT 1 FROM asignaciones_maestro am WHERE am.materia_id = m.id)
    """)
    unassigned_subjects = cursor.fetchone()[0]
    if unassigned_subjects > 0:
        print(f"  ⚠️ Materias sin maestro asignado: {unassigned_subjects}")
    
    # Maestros sin asignaciones
    cursor.execute("""
    SELECT COUNT(*) FROM usuarios u 
    WHERE u.rol = 'teacher' AND NOT EXISTS (
        SELECT 1 FROM asignaciones_maestro am WHERE am.maestro_id = u.id
    )
    """)
    unassigned_teachers = cursor.fetchone()[0]
    if unassigned_teachers > 0:
        print(f"  ⚠️ Maestros sin materias asignadas: {unassigned_teachers}")

def diagnose_problems(cursor):
    """Diagnostica problemas comunes"""
    
    problems = []
    
    # Verificar tablas esenciales
    essential_tables = ['usuarios', 'carreras', 'materias', 'grupos', 'asistencias']
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    for table in essential_tables:
        if table not in existing_tables:
            problems.append(f"❌ Tabla esencial faltante: {table}")
    
    # Verificar datos básicos
    cursor.execute("SELECT COUNT(*) FROM carreras")
    if cursor.fetchone()[0] == 0:
        problems.append("❌ No hay carreras registradas")
    
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'student'")
    if cursor.fetchone()[0] == 0:
        problems.append("❌ No hay estudiantes registrados")
    
    cursor.execute("SELECT COUNT(*) FROM grupos")
    if cursor.fetchone()[0] == 0:
        problems.append("❌ No hay grupos registrados")
    
    # Verificar integridad referencial
    cursor.execute("""
    SELECT COUNT(*) FROM usuarios u 
    WHERE u.carrera_id IS NOT NULL 
    AND NOT EXISTS (SELECT 1 FROM carreras c WHERE c.id = u.carrera_id)
    """)
    if cursor.fetchone()[0] > 0:
        problems.append("⚠️ Usuarios con carrera_id inválido")
    
    cursor.execute("""
    SELECT COUNT(*) FROM usuarios u 
    WHERE u.grupo_id IS NOT NULL 
    AND NOT EXISTS (SELECT 1 FROM grupos g WHERE g.id = u.grupo_id)
    """)
    if cursor.fetchone()[0] > 0:
        problems.append("⚠️ Usuarios con grupo_id inválido")
    
    # Mostrar problemas
    if problems:
        for problem in problems:
            print(f"  {problem}")
    else:
        print("  ✅ No se encontraron problemas críticos")

def generate_summary(cursor, tables):
    """Genera un resumen ejecutivo"""
    
    summary = {}
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        summary[table] = cursor.fetchone()[0]
    
    print(f"\n📊 Conteo de registros por tabla:")
    for table, count in summary.items():
        print(f"  {table:<25}: {count:>6} registros")
    
    # Estadísticas clave
    print(f"\n🎯 Estadísticas clave:")
    
    if 'usuarios' in summary:
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'student'")
        students = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'teacher'")
        teachers = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'admin'")
        admins = cursor.fetchone()[0]
        
        print(f"  👨‍🎓 Estudiantes: {students}")
        print(f"  👨‍🏫 Maestros: {teachers}")
        print(f"  👨‍💼 Administradores: {admins}")
    
    if 'asistencias' in summary:
        cursor.execute("SELECT COUNT(DISTINCT DATE(fecha)) FROM asistencias")
        days_with_attendance = cursor.fetchone()[0]
        print(f"  📅 Días con asistencias: {days_with_attendance}")
    
    # Estado general
    total_records = sum(summary.values())
    print(f"\n📈 Total de registros en BD: {total_records}")
    
    if total_records == 0:
        print("  🚨 BASE DE DATOS VACÍA - Necesita inicialización")
    elif total_records < 100:
        print("  ⚠️ BASE DE DATOS CON POCOS DATOS - Puede necesitar población")
    else:
        print("  ✅ BASE DE DATOS CON DATOS SUFICIENTES")

def main():
    """Función principal"""
    print("🔍 INSPECTOR DE BASE DE DATOS TESJI")
    print("Este script analizará completamente tu base de datos")
    print("-" * 50)
    
    # Buscar archivos de base de datos
    possible_paths = [
        "tesji_rfid_system.db",
        "scripts/tesji_rfid_system.db",
        "../tesji_rfid_system.db"
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No se encontró la base de datos en las ubicaciones esperadas:")
        for path in possible_paths:
            print(f"  - {path}")
        print("\n💡 Asegúrate de que el archivo tesji_rfid_system.db existe")
        return
    
    try:
        inspect_database(db_path)
        
        print(f"\n" + "="*80)
        print("✅ INSPECCIÓN COMPLETADA")
        print("="*80)
        print("📋 Ahora puedes compartir toda esta información para diagnosticar problemas")
        
    except Exception as e:
        print(f"❌ Error durante la inspección: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
