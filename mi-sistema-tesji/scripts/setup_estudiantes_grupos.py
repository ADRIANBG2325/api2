#!/usr/bin/env python3
"""
Script para crear estudiantes de ejemplo y asignarlos a grupos
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime

# Estudiantes de ejemplo con datos realistas
ESTUDIANTES_EJEMPLO = [
    {
        "uid": "1234567890",
        "nombre": "Adrian Estudiante Ejemplo",
        "matricula": "202323652",
        "email": "adrian@tesji.edu.mx",
        "grupo": "N2"  # Grupo N2 según la lista real
    },
    {
        "uid": "0987654321", 
        "nombre": "María González López",
        "matricula": "202323274",
        "email": "maria.gonzalez@tesji.edu.mx",
        "grupo": "N1"  # Grupo N1 según la lista real
    },
    {
        "uid": "1122334455",
        "nombre": "Carlos Hernández Ruiz", 
        "matricula": "202323734",
        "email": "carlos.hernandez@tesji.edu.mx",
        "grupo": "N2"  # Grupo N2 según la lista real
    },
    {
        "uid": "2233445566",
        "nombre": "Ana Martínez Silva",
        "matricula": "202323069",
        "email": "ana.martinez@tesji.edu.mx", 
        "grupo": "N1"  # Grupo N1 según la lista real
    },
    {
        "uid": "3344556677",
        "nombre": "Luis García Pérez",
        "matricula": "202323652",  # Duplicado para pruebas
        "email": "luis.garcia@tesji.edu.mx",
        "grupo": "N2"
    }
]

def create_sample_students(db_path="tesji_rfid_system.db"):
    """Crea estudiantes de ejemplo"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("👨‍🎓 Creando estudiantes de ejemplo...")
    
    # Obtener carrera ISC
    cursor.execute('SELECT id FROM carreras WHERE codigo = "ISC"')
    carrera_isc = cursor.fetchone()
    if not carrera_isc:
        print("❌ Error: Carrera ISC no encontrada")
        return
    carrera_isc_id = carrera_isc[0]
    
    # Obtener grupos
    cursor.execute('SELECT id, nombre FROM grupos WHERE activo = TRUE')
    grupos = {row[1]: row[0] for row in cursor.fetchall()}
    
    for estudiante in ESTUDIANTES_EJEMPLO:
        # Verificar si ya existe
        cursor.execute('SELECT id FROM usuarios WHERE matricula = ?', (estudiante['matricula'],))
        if cursor.fetchone():
            print(f"ℹ️ Estudiante {estudiante['matricula']} ya existe")
            continue
        
        # Buscar grupo
        grupo_nombre = f"Grupo {estudiante['grupo']}"
        grupo_id = None
        for nombre, gid in grupos.items():
            if estudiante['grupo'] in nombre:
                grupo_id = gid
                break
        
        # Crear contraseña
        password = "123456"
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        password_hash_final = f"{salt}:{password_hash}"
        
        cursor.execute('''
        INSERT INTO usuarios (
            uid, nombre_completo, matricula, email, password_hash, rol, 
            carrera_id, grupo_id, semestre, activo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            estudiante['uid'],
            estudiante['nombre'],
            estudiante['matricula'],
            estudiante['email'],
            password_hash_final,
            'student',
            carrera_isc_id,
            grupo_id,
            4,  # 4to semestre
            True
        ))
        
        print(f"✅ Estudiante creado: {estudiante['nombre']} ({estudiante['matricula']}) - Grupo {estudiante['grupo']}")
    
    conn.commit()
    conn.close()
    print("✅ Estudiantes de ejemplo creados exitosamente")

def assign_existing_students_to_groups(db_path="tesji_rfid_system.db"):
    """Asigna estudiantes existentes sin grupo a grupos automáticamente"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Asignando estudiantes existentes a grupos...")
    
    # Obtener estudiantes sin grupo
    cursor.execute('''
    SELECT id, matricula, nombre_completo 
    FROM usuarios 
    WHERE rol = 'student' AND (grupo_id IS NULL OR grupo_id = 0)
    ''')
    
    estudiantes_sin_grupo = cursor.fetchall()
    
    if not estudiantes_sin_grupo:
        print("ℹ️ Todos los estudiantes ya tienen grupo asignado")
        return
    
    # Obtener grupos disponibles
    cursor.execute('SELECT id, nombre FROM grupos WHERE activo = TRUE')
    grupos = cursor.fetchall()
    
    if not grupos:
        print("❌ No hay grupos disponibles")
        return
    
    # Asignar por patrón de matrícula
    for estudiante_id, matricula, nombre in estudiantes_sin_grupo:
        try:
            # Lógica simple: números pares van a primer grupo, impares al segundo
            ultimos_digitos = int(matricula[-2:]) if len(matricula) >= 2 else 0
            grupo_index = 0 if ultimos_digitos % 2 == 0 else 1
            
            if grupo_index < len(grupos):
                grupo_id = grupos[grupo_index][0]
                grupo_nombre = grupos[grupo_index][1]
                
                cursor.execute('UPDATE usuarios SET grupo_id = ? WHERE id = ?', (grupo_id, estudiante_id))
                print(f"   ✅ {nombre} ({matricula}) → {grupo_nombre}")
            
        except (ValueError, IndexError):
            # Si hay error, asignar al primer grupo
            grupo_id = grupos[0][0]
            grupo_nombre = grupos[0][1]
            cursor.execute('UPDATE usuarios SET grupo_id = ? WHERE id = ?', (grupo_id, estudiante_id))
            print(f"   ⚠️ {nombre} ({matricula}) → {grupo_nombre} (por defecto)")
    
    conn.commit()
    conn.close()
    print("✅ Asignación de estudiantes completada")

def generate_students_report(db_path="tesji_rfid_system.db"):
    """Genera un reporte de estudiantes por grupo"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n📊 REPORTE DE ESTUDIANTES POR GRUPO")
    print("=" * 50)
    
    cursor.execute('''
    SELECT 
        g.nombre as grupo,
        g.salon,
        g.turno,
        COUNT(u.id) as total_estudiantes,
        c.codigo as carrera
    FROM grupos g
    LEFT JOIN usuarios u ON u.grupo_id = g.id AND u.rol = 'student'
    LEFT JOIN carreras c ON g.carrera_id = c.id
    WHERE g.activo = TRUE
    GROUP BY g.id
    ORDER BY g.nombre
    ''')
    
    grupos = cursor.fetchall()
    
    for grupo, salon, turno, total, carrera in grupos:
        print(f"\n📚 {grupo}")
        print(f"   🏢 Salón: {salon}")
        print(f"   🌅 Turno: {turno}")
        print(f"   🎓 Carrera: {carrera}")
        print(f"   👥 Estudiantes: {total}")
        
        # Mostrar algunos estudiantes del grupo
        cursor.execute('''
        SELECT nombre_completo, matricula, uid
        FROM usuarios 
        WHERE grupo_id = (SELECT id FROM grupos WHERE nombre = ?) AND rol = 'student'
        LIMIT 5
        ''', (grupo,))
        
        estudiantes = cursor.fetchall()
        if estudiantes:
            print("   📋 Estudiantes (muestra):")
            for nombre, matricula, uid in estudiantes:
                uid_display = uid if uid else "Sin UID"
                print(f"      - {nombre} ({matricula}) - UID: {uid_display}")
    
    # Estadísticas generales
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "student"')
    total_estudiantes = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "student" AND grupo_id IS NOT NULL')
    estudiantes_con_grupo = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "student" AND uid IS NOT NULL')
    estudiantes_con_uid = cursor.fetchone()[0]
    
    print(f"\n📈 ESTADÍSTICAS GENERALES:")
    print(f"   👥 Total estudiantes: {total_estudiantes}")
    print(f"   📚 Con grupo asignado: {estudiantes_con_grupo}")
    print(f"   🎫 Con UID registrado: {estudiantes_con_uid}")
    print(f"   ⚠️ Sin grupo: {total_estudiantes - estudiantes_con_grupo}")
    
    conn.close()
    print("=" * 50)

def main():
    print("👨‍🎓 CONFIGURADOR DE ESTUDIANTES Y GRUPOS")
    print("=" * 50)
    
    try:
        # 1. Crear estudiantes de ejemplo
        create_sample_students()
        
        # 2. Asignar estudiantes existentes a grupos
        assign_existing_students_to_groups()
        
        # 3. Generar reporte
        generate_students_report()
        
        print("\n🎉 CONFIGURACIÓN DE ESTUDIANTES COMPLETADA")
        print("✅ Los estudiantes están listos para usar el sistema RFID")
        print("\n📝 CREDENCIALES DE ESTUDIANTES:")
        print("   Contraseña: 123456 (para todos)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
