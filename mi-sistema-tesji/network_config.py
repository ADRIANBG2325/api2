#!/usr/bin/env python3
"""
Configuración de Red Avanzada para TESJI
Permite acceso simultáneo desde múltiples dispositivos
"""

import socket
import netifaces
import subprocess
import platform
import threading
import time
import requests
import json
from datetime import datetime

class NetworkManager:
    def __init__(self):
        self.interfaces = []
        self.primary_ip = None
        self.network_name = None
        self.connected_devices = set()
        self.monitoring = False
        
    def scan_network_interfaces(self):
        """Escanea todas las interfaces de red disponibles"""
        interfaces = []
        
        try:
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr['addr']
                        if ip != '127.0.0.1' and not ip.startswith('169.254'):
                            interface_info = {
                                'interface': interface,
                                'ip': ip,
                                'netmask': addr.get('netmask', '255.255.255.0'),
                                'broadcast': addr.get('broadcast', ''),
                                'type': self._get_interface_type(interface),
                                'active': self._test_interface(ip)
                            }
                            interfaces.append(interface_info)
        except Exception as e:
            print(f"Error escaneando interfaces: {e}")
            
        self.interfaces = interfaces
        return interfaces
    
    def _get_interface_type(self, interface_name):
        """Determina el tipo de interfaz"""
        interface_name = interface_name.lower()
        if any(x in interface_name for x in ['wifi', 'wlan', 'wireless']):
            return 'WiFi'
        elif any(x in interface_name for x in ['eth', 'ethernet', 'en']):
            return 'Ethernet'
        elif 'lo' in interface_name:
            return 'Loopback'
        elif any(x in interface_name for x in ['usb', 'rndis']):
            return 'USB'
        else:
            return 'Desconocido'
    
    def _test_interface(self, ip):
        """Prueba si una interfaz está activa"""
        try:
            # Crear socket de prueba
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            sock.bind((ip, 0))
            sock.close()
            return True
        except:
            return False
    
    def get_best_ip(self):
        """Obtiene la mejor IP para el servidor"""
        if not self.interfaces:
            self.scan_network_interfaces()
        
        # Prioridades: WiFi > Ethernet > USB > Otros
        priorities = {'WiFi': 4, 'Ethernet': 3, 'USB': 2, 'Desconocido': 1}
        
        best_interface = None
        best_priority = 0
        
        for interface in self.interfaces:
            if interface['active']:
                priority = priorities.get(interface['type'], 1)
                if priority > best_priority:
                    best_priority = priority
                    best_interface = interface
        
        if best_interface:
            self.primary_ip = best_interface['ip']
            return best_interface['ip']
        
        return '127.0.0.1'
    
    def get_network_name(self):
        """Obtiene el nombre de la red WiFi actual"""
        try:
            system = platform.system()
            if system == "Linux":
                # Intentar con iwgetid
                result = subprocess.run(['iwgetid', '-r'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    self.network_name = result.stdout.strip()
                    return self.network_name
                
                # Intentar con nmcli
                result = subprocess.run(['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'], 
                                      capture_output=True, text=True, timeout=5)
                for line in result.stdout.split('\n'):
                    if line.startswith('yes:'):
                        self.network_name = line.split(':', 1)[1]
                        return self.network_name
                        
            elif system == "Darwin":  # macOS
                result = subprocess.run(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I'], 
                                      capture_output=True, text=True, timeout=5)
                for line in result.stdout.split('\n'):
                    if 'SSID' in line:
                        self.network_name = line.split(':')[1].strip()
                        return self.network_name
                        
            elif system == "Windows":
                result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                      capture_output=True, text=True, timeout=5)
                # Parsear resultado para obtener red activa
                self.network_name = "Red Windows"
                return self.network_name
                
        except Exception as e:
            print(f"No se pudo obtener nombre de red: {e}")
        
        self.network_name = "Red Local"
        return self.network_name
    
    def scan_connected_devices(self):
        """Escanea dispositivos conectados en la red"""
        if not self.primary_ip:
            self.get_best_ip()
        
        if not self.primary_ip or self.primary_ip == '127.0.0.1':
            return []
        
        # Obtener rango de red
        ip_parts = self.primary_ip.split('.')
        network_base = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
        
        devices = []
        threads = []
        
        def ping_device(ip):
            try:
                # Usar ping según el sistema operativo
                system = platform.system().lower()
                if system == "windows":
                    cmd = ['ping', '-n', '1', '-w', '1000', ip]
                else:
                    cmd = ['ping', '-c', '1', '-W', '1', ip]
                
                result = subprocess.run(cmd, capture_output=True, timeout=2)
                if result.returncode == 0:
                    devices.append({
                        'ip': ip,
                        'status': 'online',
                        'timestamp': datetime.now().isoformat()
                    })
            except:
                pass
        
        # Escanear rango de IPs (solo las más comunes para ser rápido)
        common_ips = [1, 2, 3, 4, 5, 10, 20, 50, 100, 101, 102, 103, 104, 105]
        
        for i in common_ips:
            ip = f"{network_base}.{i}"
            if ip != self.primary_ip:
                thread = threading.Thread(target=ping_device, args=(ip,))
                threads.append(thread)
                thread.start()
        
        # Esperar a que terminen todos los threads
        for thread in threads:
            thread.join()
        
        return devices
    
    def generate_qr_urls(self):
        """Genera URLs para códigos QR"""
        if not self.primary_ip:
            self.get_best_ip()
        
        urls = {
            'principal': f"http://{self.primary_ip}:8001/",
            'rfid': f"http://{self.primary_ip}:8001/welcome.html",
            'admin': f"http://{self.primary_ip}:8001/admin.html",
            'maestros': f"http://{self.primary_ip}:8001/login-teacher.html",
            'estudiantes': f"http://{self.primary_ip}:8001/student.html"
        }
        
        return urls
    
    def get_network_info(self):
        """Obtiene información completa de la red"""
        self.scan_network_interfaces()
        self.get_best_ip()
        self.get_network_name()
        
        return {
            'primary_ip': self.primary_ip,
            'network_name': self.network_name,
            'interfaces': self.interfaces,
            'total_interfaces': len([i for i in self.interfaces if i['active']]),
            'urls': self.generate_qr_urls(),
            'timestamp': datetime.now().isoformat()
        }
    
    def start_monitoring(self, callback=None):
        """Inicia monitoreo de red en tiempo real"""
        self.monitoring = True
        
        def monitor_loop():
            last_ip = self.primary_ip
            while self.monitoring:
                try:
                    current_ip = self.get_best_ip()
                    if current_ip != last_ip:
                        print(f"🔄 Cambio de IP detectado: {last_ip} → {current_ip}")
                        if callback:
                            callback(last_ip, current_ip)
                        last_ip = current_ip
                    
                    time.sleep(5)  # Verificar cada 5 segundos
                except Exception as e:
                    print(f"Error en monitoreo: {e}")
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        print("🔍 Monitor de red iniciado")
    
    def stop_monitoring(self):
        """Detiene el monitoreo"""
        self.monitoring = False
        print("🔍 Monitor de red detenido")

# Instancia global
network_manager = NetworkManager()

def print_network_report():
    """Imprime reporte completo de red"""
    info = network_manager.get_network_info()
    
    print("🌐 REPORTE DE RED TESJI")
    print("=" * 60)
    print(f"📡 Red actual: {info['network_name']}")
    print(f"🔗 IP principal: {info['primary_ip']}")
    print(f"📱 Interfaces activas: {info['total_interfaces']}")
    print()
    
    print("🖥️  INTERFACES DISPONIBLES:")
    for interface in info['interfaces']:
        status = "✅ ACTIVA" if interface['active'] else "❌ INACTIVA"
        print(f"   {interface['interface']} ({interface['type']}): {interface['ip']} - {status}")
    
    print()
    print("🔗 URLS DE ACCESO:")
    for name, url in info['urls'].items():
        print(f"   {name.capitalize()}: {url}")
    
    print()
    print("📱 ACCESO DESDE DISPOSITIVOS MÓVILES:")
    print(f"   Conecta tu teléfono/tablet a la red: {info['network_name']}")
    print(f"   Abre el navegador y ve a: http://{info['primary_ip']}:8001")
    print("=" * 60)

if __name__ == "__main__":
    print_network_report()
