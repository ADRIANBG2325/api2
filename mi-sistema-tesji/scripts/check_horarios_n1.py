#!/usr/bin/env python3
"""
Script para consultar los horarios específicos del grupo N1
"""

import sqlite3
import sys
import os

def check_n1_schedule():
    """Consulta los horarios del grupo N1"""
    
    # Buscar la base de datos
    db_paths = [
        "tesji_rfid_system.db",
        "../tesji_rfid_system.db",
        "scripts/tesji_rfid_system.db"
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No se encontró la base de datos")
        return
    
    print(f"📊 Consultando base de datos: {db_path}")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verificar grupos existentes
        print("🏫 GRUPOS EXISTENTES:")
        cursor.execute("""
        SELECT id, nombre, salon, turno, semestre, carrera_id 
        FROM grupos 
        WHERE activo = 1
        ORDER BY nombre
        """)
        
        grupos = cursor.fetchall()
        for grupo in grupos:
            print(f"   ID: {grupo[0]} | Nombre: {grupo[1]} | Salón: {grupo[2]} | Turno: {grupo[3]} | Semestre: {grupo[4]}")
        
        print("\n" + "=" * 80)
        
        # 2. Buscar específicamente grupo N1
        print("🎯 BUSCANDO GRUPO N1:")
        cursor.execute("""
        SELECT id, nombre, salon, turno, semestre, carrera_id 
        FROM grupos 
        WHERE nombre LIKE '%N1%' AND activo = 1
        """)
        
        grupo_n1 = cursor.fetchone()
        if not grupo_n1:
            print("❌ No se encontró grupo N1")
            
            # Buscar grupos similares
            cursor.execute("""
            SELECT id, nombre, salon, turno, semestre 
            FROM grupos 
            WHERE (nombre LIKE '%1%' OR salon LIKE '%N1%' OR salon LIKE '%1%') AND activo = 1
            """)
            similares = cursor.fetchall()
            if similares:
                print("🔍 Grupos similares encontrados:")
                for grupo in similares:
                    print(f"   ID: {grupo[0]} | Nombre: {grupo[1]} | Salón: {grupo[2]} | Turno: {grupo[3]}")
            
            conn.close()
            return
        
        print(f"✅ Grupo N1 encontrado:")
        print(f"   ID: {grupo_n1[0]}")
        print(f"   Nombre: {grupo_n1[1]}")
        print(f"   Salón: {grupo_n1[2]}")
        print(f"   Turno: {grupo_n1[3]}")
        print(f"   Semestre: {grupo_n1[4]}")
        
        grupo_n1_id = grupo_n1[0]
        
        print("\n" + "=" * 80)
        
        # 3. Consultar horarios del grupo N1
        print("📅 HORARIOS DEL GRUPO N1:")
        cursor.execute("""
        SELECT 
            hd.dia_semana,
            hd.hora_inicio,
            hd.hora_fin,
            m.nombre as materia,
            m.clave_oficial as codigo,
            hd.tipo_clase,
            m.creditos,
            u.nombre_completo as maestro
        FROM horarios_detallados hd
        JOIN materias m ON hd.materia_id = m.id
        LEFT JOIN asignaciones_maestro am ON am.materia_id = m.id AND am.grupo_id = hd.grupo_id
        LEFT JOIN usuarios u ON am.maestro_id = u.id
        WHERE hd.grupo_id = ? AND hd.activo = 1
        ORDER BY 
            CASE hd.dia_semana 
                WHEN 'Lunes' THEN 1 
                WHEN 'Martes' THEN 2 
                WHEN 'Miércoles' THEN 3 
                WHEN 'Jueves' THEN 4 
                WHEN 'Viernes' THEN 5 
                WHEN 'Sábado' THEN 6 
                WHEN 'Domingo' THEN 7 
            END,
            hd.hora_inicio
        """, (grupo_n1_id,))
        
        horarios = cursor.fetchall()
        
        if not horarios:
            print("❌ No se encontraron horarios para el grupo N1")
            
            # Verificar si existen horarios en general
            cursor.execute("SELECT COUNT(*) FROM horarios_detallados WHERE activo = 1")
            total_horarios = cursor.fetchone()[0]
            print(f"📊 Total de horarios en la base de datos: {total_horarios}")
            
        else:
            print(f"✅ Se encontraron {len(horarios)} clases para el grupo N1:")
            print()
            
            # Organizar por día
            horarios_por_dia = {}
            for horario in horarios:
                dia = horario[0]
                if dia not in horarios_por_dia:
                    horarios_por_dia[dia] = []
                horarios_por_dia[dia].append(horario)
            
            # Mostrar horarios organizados
            dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
            
            for dia in dias_orden:
                if dia in horarios_por_dia:
                    print(f"📅 {dia.upper()}:")
                    for horario in horarios_por_dia[dia]:
                        print(f"   {horario[1]} - {horario[2]} | {horario[3]} ({horario[4]}) | {horario[5]} | {horario[6]} créditos")
                        if horario[7]:
                            print(f"      👨‍🏫 Maestro: {horario[7]}")
                        print()
        
        print("=" * 80)
        
        # 4. Consultar estudiantes del grupo N1
        print("👥 ESTUDIANTES DEL GRUPO N1:")
        cursor.execute("""
        SELECT nombre_completo, matricula, uid, email
        FROM usuarios 
        WHERE grupo_id = ? AND rol = 'student' AND activo = 1
        ORDER BY nombre_completo
        """, (grupo_n1_id,))
        
        estudiantes = cursor.fetchall()
        print(f"✅ {len(estudiantes)} estudiantes en el grupo N1:")
        
        for i, estudiante in enumerate(estudiantes[:10], 1):  # Mostrar solo los primeros 10
            print(f"   {i}. {estudiante[0]} | {estudiante[1]} | UID: {estudiante[2]}")
        
        if len(estudiantes) > 10:
            print(f"   ... y {len(estudiantes) - 10} estudiantes más")
        
        print("\n" + "=" * 80)
        
        # 5. Verificar materias del grupo N1
        print("📚 MATERIAS DEL GRUPO N1:")
        cursor.execute("""
        SELECT DISTINCT
            m.nombre,
            m.clave_oficial,
            m.creditos,
            m.semestre
        FROM materias m
        JOIN horarios_detallados hd ON m.id = hd.materia_id
        WHERE hd.grupo_id = ? AND hd.activo = 1
        ORDER BY m.nombre
        """, (grupo_n1_id,))
        
        materias = cursor.fetchall()
        print(f"✅ {len(materias)} materias asignadas al grupo N1:")
        
        for materia in materias:
            print(f"   📖 {materia[0]} ({materia[1]}) | {materia[2]} créditos | Semestre {materia[3]}")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ Consulta completada exitosamente")
        
        # Generar código JavaScript para el frontend
        if horarios:
            print("\n🔧 CÓDIGO JAVASCRIPT PARA EL FRONTEND:")
            print("const HORARIO_GRUPO_N1 = {")
            
            for dia in dias_orden:
                if dia in horarios_por_dia:
                    print(f'  "{dia}": [')
                    for horario in horarios_por_dia[dia]:
                        print(f'    {{')
                        print(f'      materia: "{horario[3]}",')
                        print(f'      codigo: "{horario[4]}",')
                        print(f'      salon: "{grupo_n1[2]}",')
                        print(f'      hora_inicio: "{horario[1]}",')
                        print(f'      hora_fin: "{horario[2]}",')
                        print(f'      tipo: "{horario[5]}",')
                        print(f'      creditos: {horario[6]},')
                        print(f'      maestro: "{horario[7] or "Por asignar"}"')
                        print(f'    }},')
                    print(f'  ],')
                else:
                    print(f'  "{dia}": [],')
            
            print("};")
        
    except Exception as e:
        print(f"❌ Error consultando la base de datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 CONSULTA DE HORARIOS DEL GRUPO N1")
    print("=" * 80)
    check_n1_schedule()
