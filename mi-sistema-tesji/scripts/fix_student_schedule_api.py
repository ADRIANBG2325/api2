#!/usr/bin/env python3
"""
Script para verificar y arreglar los datos de horarios en la base de datos
"""

import sqlite3
import sys
import os

# Agregar el directorio padre al path para importar el servidor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_and_fix_database():
    """Verificar y arreglar la base de datos"""
    
    print("🔧 VERIFICANDO Y ARREGLANDO BASE DE DATOS")
    print("=" * 60)
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('tesji_rfid_system.db')
        cursor = conn.cursor()
        
        # 1. Verificar estudiantes con UID conocidos
        print("👥 VERIFICANDO ESTUDIANTES:")
        cursor.execute("""
        SELECT id, nombre_completo, matricula, uid, grupo_id, rol 
        FROM usuarios 
        WHERE rol = 'student' AND uid IN ('2233445566', '0987654321')
        """)
        
        estudiantes = cursor.fetchall()
        print(f"✅ Estudiantes encontrados: {len(estudiantes)}")
        
        for est in estudiantes:
            print(f"   - {est[1]} | {est[2]} | UID: {est[3]} | Grupo: {est[4]}")
        
        # 2. Verificar grupos
        print("\n🏫 VERIFICANDO GRUPOS:")
        cursor.execute("SELECT id, nombre, salon, turno, semestre FROM grupos WHERE activo = 1")
        grupos = cursor.fetchall()
        
        for grupo in grupos:
            print(f"   - ID: {grupo[0]} | {grupo[1]} | Salón: {grupo[2]} | {grupo[3]}")
        
        # 3. Verificar horarios detallados
        print("\n📅 VERIFICANDO HORARIOS DETALLADOS:")
        cursor.execute("""
        SELECT COUNT(*) as total,
               COUNT(DISTINCT grupo_id) as grupos_con_horarios,
               COUNT(DISTINCT materia_id) as materias_con_horarios
        FROM horarios_detallados 
        WHERE activo = 1
        """)
        
        stats = cursor.fetchone()
        print(f"   - Total horarios: {stats[0]}")
        print(f"   - Grupos con horarios: {stats[1]}")
        print(f"   - Materias con horarios: {stats[2]}")
        
        # 4. Verificar horarios específicos del grupo N1 (ID 2)
        print("\n📚 HORARIOS DEL GRUPO N1 (ID: 2):")
        cursor.execute("""
        SELECT DISTINCT
            hd.dia_semana,
            hd.hora_inicio,
            hd.hora_fin,
            m.nombre as materia,
            m.clave_oficial as codigo,
            hd.tipo_clase,
            m.creditos
        FROM horarios_detallados hd
        JOIN materias m ON hd.materia_id = m.id
        WHERE hd.grupo_id = 2 AND hd.activo = 1
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
        """)
        
        horarios_n1 = cursor.fetchall()
        print(f"✅ Horarios encontrados para grupo N1: {len(horarios_n1)}")
        
        dias_agrupados = {}
        for horario in horarios_n1:
            dia = horario[0]
            if dia not in dias_agrupados:
                dias_agrupados[dia] = []
            dias_agrupados[dia].append(horario)
        
        for dia, horarios in dias_agrupados.items():
            print(f"\n📅 {dia.upper()}:")
            for h in horarios:
                print(f"   {h[1]}-{h[2]} | {h[3]} ({h[4]}) | {h[5]} | {h[6]} créditos")
        
        # 5. Verificar asignaciones de maestros
        print("\n👨‍🏫 VERIFICANDO ASIGNACIONES DE MAESTROS:")
        cursor.execute("""
        SELECT COUNT(*) as total_asignaciones,
               COUNT(DISTINCT maestro_id) as maestros_asignados,
               COUNT(DISTINCT grupo_id) as grupos_con_maestros
        FROM asignaciones_maestro 
        WHERE activa = 1
        """)
        
        maestros_stats = cursor.fetchone()
        print(f"   - Total asignaciones: {maestros_stats[0]}")
        print(f"   - Maestros asignados: {maestros_stats[1]}")
        print(f"   - Grupos con maestros: {maestros_stats[2]}")
        
        # 6. Asignar estudiantes al grupo N1 si no están asignados
        print("\n🔧 ASIGNANDO ESTUDIANTES AL GRUPO N1:")
        
        # Estudiantes específicos del grupo N1
        estudiantes_n1 = [
            ('2233445566', 'Ana Martínez Silva', '202323069'),
            ('0987654321', 'María González López', '202323274')
        ]
        
        for uid, nombre, matricula in estudiantes_n1:
            # Verificar si el estudiante existe
            cursor.execute("SELECT id, grupo_id FROM usuarios WHERE uid = ? AND rol = 'student'", (uid,))
            estudiante = cursor.fetchone()
            
            if estudiante:
                if estudiante[1] != 2:  # Si no está en el grupo N1
                    cursor.execute("UPDATE usuarios SET grupo_id = 2 WHERE id = ?", (estudiante[0],))
                    print(f"   ✅ {nombre} asignado al grupo N1")
                else:
                    print(f"   ℹ️ {nombre} ya está en el grupo N1")
            else:
                # Crear el estudiante si no existe
                cursor.execute("""
                INSERT INTO usuarios (uid, nombre_completo, matricula, rol, grupo_id, activo)
                VALUES (?, ?, ?, 'student', 2, 1)
                """, (uid, nombre, matricula))
                print(f"   ✅ {nombre} creado y asignado al grupo N1")
        
        # Confirmar cambios
        conn.commit()
        
        print("\n✅ VERIFICACIÓN Y CORRECCIÓN COMPLETADA")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_and_fix_database()
