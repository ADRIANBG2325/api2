#!/usr/bin/env python3
"""
Puente Serial USB para TESJI - Versión Profesional
Comunicación robusta y confiable con el servidor
"""

import serial
import json
import requests
import time
import threading
from datetime import datetime
import logging
import serial.tools.list_ports
import subprocess
import signal
import sys
import queue
from typing import Optional, Dict, Any

# Configuración
BAUD_RATE = 115200
SERVER_URL = "http://127.0.0.1:8001"
RFID_ENDPOINT = "/api/rfid/bridge"
HEALTH_ENDPOINT = "/api/health"

# Configurar logging profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('serial_bridge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProfessionalSerialBridge:
    def __init__(self):
        self.serial_conn: Optional[serial.Serial] = None
        self.running = False
        self.puerto_detectado: Optional[str] = None
        self.data_queue = queue.Queue()
        self.stats = {
            "uids_processed": 0,
            "successful_sends": 0,
            "failed_sends": 0,
            "start_time": None
        }
    
    def verify_server_connection(self) -> bool:
        """Verifica que el servidor esté disponible"""
        try:
            logger.info("🔍 Verificando conexión con servidor...")
            response = requests.get(f"{SERVER_URL}{HEALTH_ENDPOINT}", timeout=5)
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ Servidor disponible: {health_data.get('message', 'OK')}")
                return True
            else:
                logger.error(f"❌ Servidor respondió con código {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.error("❌ No se puede conectar al servidor")
            logger.error("💡 Asegúrate de que unified_server.py esté ejecutándose")
            return False
        except Exception as e:
            logger.error(f"❌ Error verificando servidor: {e}")
            return False
    
    def close_conflicting_processes(self):
        """Cierra procesos que puedan interferir con el puerto serial"""
        try:
            # Buscar y cerrar Thonny
            result = subprocess.run(['pgrep', '-f', 'thonny'], capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                logger.warning(f"⚠️ Thonny detectado ejecutándose (PIDs: {', '.join(pids)})")
                
                response = input("¿Cerrar Thonny automáticamente? (s/n): ")
                if response.lower() in ['s', 'si', 'y', 'yes']:
                    subprocess.run(['pkill', '-f', 'thonny'])
                    time.sleep(3)
                    logger.info("✅ Thonny cerrado")
                    return True
                else:
                    logger.warning("❌ Por favor cierra Thonny manualmente")
                    return False
            return True
        except Exception as e:
            logger.warning(f"⚠️ Error verificando procesos: {e}")
            return True
    
    def find_pico_port(self) -> Optional[str]:
        """Busca automáticamente el puerto del Raspberry Pi Pico"""
        logger.info("🔍 Buscando Raspberry Pi Pico...")
        ports = serial.tools.list_ports.comports()
        
        if not ports:
            logger.error("❌ No se encontraron puertos seriales")
            return None
        
        logger.info("📋 PUERTOS DISPONIBLES:")
        for i, port in enumerate(ports):
            vid_pid = f"{hex(port.vid)}:{hex(port.pid)}" if hasattr(port, 'vid') and port.vid else "N/A"
            logger.info(f"   {i+1}. {port.device} - {port.description} (VID:PID: {vid_pid})")
        
        # Buscar Pico específicamente (VID de Raspberry Pi Foundation)
        pico_candidates = []
        for port in ports:
            if hasattr(port, 'vid') and port.vid == 0x2E8A:  # Raspberry Pi Foundation
                pico_candidates.append(port.device)
                logger.info(f"   ✅ Pico detectado: {port.device}")
            elif any(keyword in port.description.lower() for keyword in ["pico", "board", "cdc"]):
                pico_candidates.append(port.device)
                logger.info(f"   🔍 Posible Pico: {port.device}")
        
        # Probar candidatos automáticamente
        for candidate in pico_candidates:
            if self.test_port_connection(candidate):
                return candidate
        
        # Si no encuentra automáticamente, permitir selección manual
        if ports:
            logger.info("\n❓ Selecciona puerto manualmente:")
            for i, port in enumerate(ports):
                print(f"   {i+1}. {port.device}")
            
            try:
                choice = int(input("Número de puerto (1-{}): ".format(len(ports))))
                if 1 <= choice <= len(ports):
                    selected_port = ports[choice-1].device
                    if self.test_port_connection(selected_port):
                        return selected_port
            except (ValueError, KeyboardInterrupt):
                pass
        
        return None
    
    def test_port_connection(self, port: str) -> bool:
        """Prueba conexión a un puerto específico"""
        try:
            logger.info(f"🔌 Probando puerto {port}...")
            test_serial = serial.Serial(port, BAUD_RATE, timeout=2)
            
            # Probar lectura por 3 segundos
            start_time = time.time()
            data_received = False
            
            while time.time() - start_time < 3:
                if test_serial.in_waiting > 0:
                    line = test_serial.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        logger.info(f"   📥 Datos recibidos: {line[:50]}...")
                        data_received = True
                        break
                time.sleep(0.1)
            
            test_serial.close()
            
            if data_received:
                logger.info(f"   ✅ Puerto {port} tiene datos válidos")
                return True
            else:
                logger.warning(f"   ⚠️ Puerto {port} sin datos")
                return False
                
        except Exception as e:
            logger.warning(f"   ❌ Puerto {port} error: {e}")
            return False
    
    def connect_serial(self) -> bool:
        """Establece conexión serial"""
        try:
            if not self.close_conflicting_processes():
                return False
            
            self.puerto_detectado = self.find_pico_port()
            if not self.puerto_detectado:
                logger.error("❌ No se pudo detectar el Raspberry Pi Pico")
                return False
            
            logger.info(f"🔌 Conectando a {self.puerto_detectado}...")
            
            self.serial_conn = serial.Serial(
                port=self.puerto_detectado,
                baudrate=BAUD_RATE,
                timeout=2,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            time.sleep(2)  # Tiempo para estabilizar conexión
            logger.info("✅ Conexión serial establecida")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error conectando serial: {e}")
            return False
    
    def send_to_server(self, uid: str) -> Dict[str, Any]:
        """Envía UID al servidor con manejo robusto de errores"""
        try:
            data = {"tag": uid}
            
            logger.info(f"📤 Enviando al servidor: {uid}")
            
            response = requests.post(
                f"{SERVER_URL}{RFID_ENDPOINT}",
                json=data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Log detallado de la respuesta
                exists = result.get('exists', False)
                message = result.get('message', 'Sin mensaje')
                user_info = result.get('user', {})
                
                if exists:
                    logger.info(f"✅ Usuario reconocido: {user_info.get('nombre', 'N/A')} ({user_info.get('matricula', 'N/A')})")
                    logger.info(f"   Mensaje: {message}")
                else:
                    logger.warning(f"⚠️ UID no registrado: {uid}")
                    logger.info(f"   Mensaje: {message}")
                
                self.stats["successful_sends"] += 1
                return result
            else:
                logger.error(f"❌ Error del servidor: HTTP {response.status_code}")
                logger.error(f"   Respuesta: {response.text[:200]}")
                self.stats["failed_sends"] += 1
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.ConnectionError:
            logger.error("❌ No se pudo conectar al servidor")
            logger.error(f"💡 Verifica que el servidor esté en: {SERVER_URL}")
            self.stats["failed_sends"] += 1
            return {"success": False, "error": "Connection error"}
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout al enviar al servidor")
            self.stats["failed_sends"] += 1
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            logger.error(f"❌ Error enviando al servidor: {e}")
            self.stats["failed_sends"] += 1
            return {"success": False, "error": str(e)}
    
    def process_serial_data(self, line: str) -> bool:
        """Procesa datos recibidos del Pico con validación robusta"""
        try:
            line = line.strip()
            
            if not line:
                return False
            
            # Log de datos raw para debugging
            logger.debug(f"📥 Raw data: {repr(line)}")
            
            # Buscar patrones de UID
            uid_patterns = [
                "UID_DETECTED:",
                "UID:",
                "RFID:",
                "TAG:"
            ]
            
            uid = None
            for pattern in uid_patterns:
                if pattern in line:
                    uid = line.split(pattern, 1)[1].strip()
                    break
            
            # Si no encuentra patrón, asumir que toda la línea es el UID
            if not uid and len(line) >= 6 and line.replace(' ', '').replace(':', '').isalnum():
                uid = line.replace(' ', '').replace(':', '').upper()
            
            if uid and len(uid) >= 6:
                logger.info(f"\n🎫 UID DETECTADO: {uid}")
                logger.info("-" * 50)
                
                # Enviar al servidor
                result = self.send_to_server(uid)
                
                self.stats["uids_processed"] += 1
                
                logger.info("-" * 50)
                return True
            else:
                # Log de líneas que no son UIDs para debugging
                if len(line) > 3:  # Evitar spam de líneas muy cortas
                    logger.debug(f"📝 Info: {line}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error procesando datos: {e}")
            return False
    
    def serial_reader_thread(self):
        """Thread dedicado para leer datos seriales"""
        logger.info("🔄 Iniciando thread de lectura serial...")
        
        buffer = ""
        no_data_counter = 0
        
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    # Leer datos disponibles
                    data = self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8', errors='ignore')
                    buffer += data
                    no_data_counter = 0
                    
                    # Procesar líneas completas
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            self.process_serial_data(line)
                else:
                    no_data_counter += 1
                    
                    # Advertencias por falta de datos
                    if no_data_counter == 100:  # ~10 segundos
                        logger.warning("⚠️ No se reciben datos del Pico por 10 segundos")
                        logger.info("💡 Verifica que el código RFID esté ejecutándose en el Pico")
                    elif no_data_counter == 600:  # ~60 segundos
                        logger.error("❌ Sin datos por 60 segundos")
                        logger.error("💡 ¿Está el Pico conectado y funcionando?")
                        no_data_counter = 0
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Error en thread de lectura: {e}")
                time.sleep(1)
    
    def print_stats(self):
        """Imprime estadísticas del sistema"""
        if self.stats["start_time"]:
            uptime = time.time() - self.stats["start_time"]
            logger.info(f"📊 Estadísticas - Tiempo activo: {uptime:.0f}s")
            logger.info(f"   UIDs procesados: {self.stats['uids_processed']}")
            logger.info(f"   Envíos exitosos: {self.stats['successful_sends']}")
            logger.info(f"   Envíos fallidos: {self.stats['failed_sends']}")
    
    def start(self) -> bool:
        """Inicia el puente serial profesional"""
        logger.info("🎓 TESJI - Puente Serial USB Profesional")
        logger.info("=" * 60)
        
        # Verificar servidor
        if not self.verify_server_connection():
            return False
        
        # Conectar serial
        if not self.connect_serial():
            return False
        
        self.running = True
        self.stats["start_time"] = time.time()
        
        # Iniciar thread de lectura
        serial_thread = threading.Thread(target=self.serial_reader_thread, daemon=True)
        serial_thread.start()
        
        logger.info("✅ Puente serial activo")
        logger.info("💡 Acerca una tarjeta RFID al Pico...")
        logger.info(f"📱 Puerto: {self.puerto_detectado}")
        logger.info(f"🌐 Servidor: {SERVER_URL}")
        logger.info("=" * 60)
        
        try:
            # Loop principal con estadísticas periódicas
            last_stats_time = time.time()
            
            while True:
                time.sleep(1)
                
                # Mostrar estadísticas cada 30 segundos
                if time.time() - last_stats_time > 30:
                    self.print_stats()
                    last_stats_time = time.time()
                
        except KeyboardInterrupt:
            logger.info("\n👋 Deteniendo puente serial...")
            self.stop()
            return True
    
    def stop(self):
        """Detiene el puente serial"""
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
        
        self.print_stats()
        logger.info("✅ Puente serial detenido")

def main():
    logger.info("🎓 TESJI - Sistema RFID Profesional")
    logger.info("=" * 60)
    logger.info("🔧 PASOS IMPORTANTES:")
    logger.info("1. Asegúrate de que unified_server.py esté ejecutándose")
    logger.info("2. Cierra Thonny COMPLETAMENTE")
    logger.info("3. Sube el código RFID al Pico como main.py")
    logger.info("4. Desconecta y reconecta el Pico")
    logger.info("=" * 60)
    
    bridge = ProfessionalSerialBridge()
    success = bridge.start()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
