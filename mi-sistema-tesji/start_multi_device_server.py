#!/usr/bin/env python3
"""
Iniciador del Servidor Multi-Dispositivo TESJI
"""

import sys
import os
import asyncio
from network_config import network_manager, print_network_report
from multi_device_server import setup_websocket_routes, connection_manager

# Importar el servidor principal
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from unified_server import app, logger

def setup_multi_device_features():
    """Configura características multi-dispositivo"""
    
    # Configurar WebSocket routes
    setup_websocket_routes(app)
    
    # Configurar CORS para múltiples dispositivos
    from fastapi.middleware.cors import CORSMiddleware
    
    # Permitir acceso desde cualquier dispositivo en la red local
    network_info = network_manager.get_network_info()
    allowed_origins = [
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        f"http://{network_info['primary_ip']}:8001"
    ]
    
    # Agregar IPs de la red local
    if network_info['primary_ip']:
        ip_parts = network_info['primary_ip'].split('.')
        network_base = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
        
        # Agregar rango común de IPs
        for i in range(1, 255):
            allowed_origins.append(f"http://{network_base}.{i}:8001")
    
    # Reconfigurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Permitir todos los orígenes para desarrollo
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    logger.info("🌐 Configuración multi-dispositivo activada")
    logger.info(f"📱 Orígenes permitidos: {len(allowed_origins)} IPs")

def main():
    """Función principal"""
    print("🎓 TESJI - Sistema Multi-Dispositivo")
    print("=" * 60)
    
    # Configurar características multi-dispositivo
    setup_multi_device_features()
    
    # Mostrar información de red
    print_network_report()
    
    # Iniciar monitoreo de red
    def on_network_change(old_ip, new_ip):
        logger.info(f"🔄 IP cambió de {old_ip} a {new_ip}")
        logger.info(f"🔗 Nueva URL: http://{new_ip}:8001")
    
    network_manager.start_monitoring(callback=on_network_change)
    
    print("\n🚀 INSTRUCCIONES DE USO:")
    print("1. Conecta todos tus dispositivos a la misma red WiFi")
    print("2. En cada dispositivo, abre el navegador")
    print(f"3. Ve a: http://{network_manager.get_best_ip()}:8001")
    print("4. ¡Todos los dispositivos se sincronizarán automáticamente!")
    print("\n📱 DISPOSITIVOS COMPATIBLES:")
    print("   ✅ Teléfonos Android/iPhone")
    print("   ✅ Tablets iPad/Android")
    print("   ✅ Laptops/Computadoras")
    print("   ✅ Raspberry Pi con pantalla")
    print("=" * 60)
    
    # Importar uvicorn aquí para evitar conflictos
    import uvicorn
    
    try:
        # Iniciar servidor
        uvicorn.run(
            app,
            host="0.0.0.0",  # Escuchar en todas las interfaces
            port=8001,
            reload=False,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")
        network_manager.stop_monitoring()
    except Exception as e:
        print(f"❌ Error: {e}")
        network_manager.stop_monitoring()

if __name__ == "__main__":
    main()
