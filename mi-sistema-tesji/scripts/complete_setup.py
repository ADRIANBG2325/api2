#!/usr/bin/env python3
"""
Script completo para configurar todo el sistema TESJI desde cero
"""

import subprocess
import sys
import os

def run_script(script_path):
    """Ejecuta un script de Python"""
    try:
        print(f"\n🚀 Ejecutando: {script_path}")
        print("-" * 40)
        
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print(f"✅ {script_path} completado exitosamente")
            return True
        else:
            print(f"❌ Error en {script_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando {script_path}: {e}")
        return False

def main():
    print("🏫 CONFIGURADOR COMPLETO DEL SISTEMA TESJI")
    print("=" * 60)
    print("Este script configurará todo el sistema desde cero:")
    print("1. Inicializar base de datos")
    print("2. Poblar estructura académica")
    print("3. Crear datos de ejemplo")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("scripts"):
        print("❌ Error: No se encontró el directorio 'scripts'")
        print("💡 Asegúrate de ejecutar este script desde la carpeta raíz del proyecto")
        return
    
    scripts_to_run = [
        "scripts/initialize_database.py",
        "scripts/populate_academic_structure.py"
    ]
    
    success_count = 0
    
    for script in scripts_to_run:
        if os.path.exists(script):
            if run_script(script):
                success_count += 1
            else:
                print(f"⚠️ Falló la ejecución de {script}")
                break
        else:
            print(f"❌ No se encontró el script: {script}")
            break
    
    print("\n" + "=" * 60)
    if success_count == len(scripts_to_run):
        print("🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("\n✅ El sistema TESJI está completamente configurado")
        print("\n🚀 Para iniciar el servidor:")
        print("   python unified_server.py")
        print("\n🌐 URLs disponibles:")
        print("   - http://localhost:8001/ (Página principal)")
        print("   - http://localhost:8001/admin.html (Panel admin)")
        print("   - http://localhost:8001/login-teacher.html (Login maestros)")
        print("   - http://localhost:8001/welcome.html (RFID completo)")
    else:
        print("❌ CONFIGURACIÓN INCOMPLETA")
        print(f"   Scripts exitosos: {success_count}/{len(scripts_to_run)}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
