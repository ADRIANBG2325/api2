#!/usr/bin/env python3
"""
Servidor Unificado TESJI - Sistema Completo CORREGIDO
Versión Final - TODOS los errores solucionados
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Boolean, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, validator
from datetime import datetime, time, timedelta
import json
import time as time_module
import logging
import uvicorn
import sys
import os
import hashlib
import secrets
import jwt
from typing import Optional, List, Dict, Any
import sqlite3
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException
from starlette import status
import socket
import netifaces
import threading
import subprocess
import platform

# Configurar logging profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tesji_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuración
SECRET_KEY = os.environ.get("TESJI_SECRET_KEY", "tesji_secret_key_2024_super_secure")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

# HTTP Bearer authentication scheme
security = HTTPBearer(auto_error=False)

# Base de datos
SQLALCHEMY_DATABASE_URL = "sqlite:///./tesji_rfid_system.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Variable global para RFID
active_rfid_sessions = {}

# Estadísticas del servidor
server_stats = {
    "start_time": None,
    "rfid_requests": 0,
    "successful_recognitions": 0,
    "failed_recognitions": 0,
    "new_registrations": 0
}

# LISTAS REALES DE ESTUDIANTES POR GRUPO
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

# HORARIOS REALES
HORARIO_SALON_N1 = {
    "Lunes": [
        {
            "materia": "Métodos Numéricos",
            "codigo": "SCC-1017",
            "salon": "N1",
            "hora_inicio": "07:00",
            "hora_fin": "09:00",
            "tipo": "Teoría",
            "creditos": 4,
            "maestro": "Lic. Juan Alberto Martínez Zamora",
            "horario": "07:00 - 09:00"
        },
        {
            "materia": "Ecuaciones Diferenciales",
            "codigo": "ACF-0905",
            "salon": "N1",
            "hora_inicio": "09:00",
            "hora_fin": "12:00",
            "tipo": "Teoría",
            "creditos": 5,
            "maestro": "Ing. Rodolfo Guadalupe Alcántara Rosales",
            "horario": "09:00 - 12:00"
        },
        {
            "materia": "Tutorías",
            "codigo": "TUT-001",
            "salon": "N1",
            "hora_inicio": "12:00",
            "hora_fin": "14:00",
            "tipo": "Tutoría",
            "creditos": 0,
            "maestro": "Tutor Asignado",
            "horario": "12:00 - 14:00"
        },
        {
            "materia": "Fundamentos de Base de Datos",
            "codigo": "AEF-1031",
            "salon": "N1",
            "hora_inicio": "15:00",
            "hora_fin": "18:00",
            "tipo": "Teoría",
            "creditos": 5,
            "maestro": "Mtra. Yadira Esther Jiménez Pérez",
            "horario": "15:00 - 18:00"
        }
    ],
    "Martes": [
        {
            "materia": "Inglés",
            "codigo": "ING-001",
            "salon": "N1",
            "hora_inicio": "09:00",
            "hora_fin": "11:00",
            "tipo": "Idioma",
            "creditos": 2,
            "maestro": "L.L. Isodoro Cruz Huitrón",
            "horario": "09:00 - 11:00"
        },
        {
            "materia": "Arquitectura de Computadoras",
            "codigo": "SCD-1003",
            "salon": "N1",
            "hora_inicio": "11:00",
            "hora_fin": "13:00",
            "tipo": "Teoría",
            "creditos": 5,
            "maestro": "Ing. Alfredo Aguilar López",
            "horario": "11:00 - 13:00"
        },
        {
            "materia": "Tópicos Avanzados de Programación",
            "codigo": "SCD-1027",
            "salon": "N1",
            "hora_inicio": "13:00",
            "hora_fin": "15:00",
            "tipo": "Práctica",
            "creditos": 5,
            "maestro": "Víctor David Maya Arce",
            "horario": "13:00 - 15:00"
        }
    ],
    "Miércoles": [
        {
            "materia": "Métodos Numéricos",
            "codigo": "SCC-1017",
            "salon": "N1",
            "hora_inicio": "07:00",
            "hora_fin": "09:00",
            "tipo": "Teoría",
            "creditos": 4,
            "maestro": "Lic. Juan Alberto Martínez Zamora",
            "horario": "07:00 - 09:00"
        },
        {
            "materia": "Inglés",
            "codigo": "ING-001",
            "salon": "N1",
            "hora_inicio": "09:00",
            "hora_fin": "11:00",
            "tipo": "Idioma",
            "creditos": 2,
            "maestro": "L.L. Isodoro Cruz Huitrón",
            "horario": "09:00 - 11:00"
        },
        {
            "materia": "Ecuaciones Diferenciales",
            "codigo": "ACF-0905",
            "salon": "N1",
            "hora_inicio": "11:00",
            "hora_fin": "13:00",
            "tipo": "Teoría",
            "creditos": 5,
            "maestro": "Ing. Rodolfo Guadalupe Alcántara Rosales",
            "horario": "11:00 - 13:00"
        },
        {
            "materia": "Taller de Sistemas Operativos",
            "codigo": "SCA-1026",
            "salon": "N1",
            "hora_inicio": "13:00",
            "hora_fin": "15:00",
            "tipo": "Práctica",
            "creditos": 4,
            "maestro": "Mtro. Anselmo Martínez Montalvo",
            "horario": "13:00 - 15:00"
        }
    ],
    "Jueves": [
        {
            "materia": "Inglés",
            "codigo": "ING-001",
            "salon": "N1",
            "hora_inicio": "07:00",
            "hora_fin": "09:00",
            "tipo": "Idioma",
            "creditos": 2,
            "maestro": "L.L. Isodoro Cruz Huitrón",
            "horario": "07:00 - 09:00"
        },
        {
            "materia": "Taller de Ética",
            "codigo": "ACA-0907",
            "salon": "N1",
            "hora_inicio": "09:00",
            "hora_fin": "11:00",
            "tipo": "Práctica",
            "creditos": 4,
            "maestro": "C.P. Sonia Vázquez Alcántara",
            "horario": "09:00 - 11:00"
        },
        {
            "materia": "Fundamentos de Base de Datos",
            "codigo": "AEF-1031",
            "salon": "N1",
            "hora_inicio": "11:00",
            "hora_fin": "13:00",
            "tipo": "Teoría",
            "creditos": 5,
            "maestro": "Mtra. Yadira Esther Jiménez Pérez",
            "horario": "11:00 - 13:00"
        },
        {
            "materia": "Tópicos Avanzados de Programación",
            "codigo": "SCD-1027",
            "salon": "N1",
            "hora_inicio": "14:00",
            "hora_fin": "16:00",
            "tipo": "Práctica",
            "creditos": 5,
            "maestro": "Víctor David Maya Arce",
            "horario": "14:00 - 16:00"
        }
    ],
    "Viernes": [
        {
            "materia": "Taller de Sistemas Operativos",
            "codigo": "SCA-1026",
            "salon": "N1",
            "hora_inicio": "07:00",
            "hora_fin": "09:00",
            "tipo": "Práctica",
            "creditos": 4,
            "maestro": "Mtro. Anselmo Martínez Montalvo",
            "horario": "07:00 - 09:00"
        },
        {
            "materia": "Taller de Ética",
            "codigo": "ACA-0907",
            "salon": "N1",
            "hora_inicio": "09:00",
            "hora_fin": "11:00",
            "tipo": "Práctica",
            "creditos": 4,
            "maestro": "C.P. Sonia Vázquez Alcántara",
            "horario": "09:00 - 11:00"
        },
        {
            "materia": "Arquitectura de Computadoras",
            "codigo": "SCD-1003",
            "salon": "N1",
            "hora_inicio": "11:00",
            "hora_fin": "14:00",
            "tipo": "Teoría",
            "creditos": 5,
            "maestro": "Ing. Alfredo Aguilar López",
            "horario": "11:00 - 14:00"
        }
    ],
    "Sábado": [],
    "Domingo": []
}

# Horario temporal para Salón N2 (hasta que se proporcione el real)
HORARIO_SALON_N2 = {
    "Lunes": [
        {
            "materia": "Programación Avanzada",
            "codigo": "PRG-002",
            "salon": "N2",
            "hora_inicio": "08:00",
            "hora_fin": "10:00",
            "tipo": "Práctica",
            "creditos": 5,
            "maestro": "Ing. Ejemplo N2",
            "horario": "08:00 - 10:00"
        }
    ],
    "Martes": [],
    "Miércoles": [
        {
            "materia": "Base de Datos Avanzada",
            "codigo": "BDA-002",
            "salon": "N2",
            "hora_inicio": "10:00",
            "hora_fin": "12:00",
            "tipo": "Teoría",
            "creditos": 5,
            "maestro": "Mtra. Ejemplo N2",
            "horario": "10:00 - 12:00"
        }
    ],
    "Jueves": [],
    "Viernes": [],
    "Sábado": [],
    "Domingo": []
}

# Función mejorada para obtener IP automáticamente
def get_network_interfaces():
    """Obtiene todas las interfaces de red disponibles"""
    interfaces = []
    try:
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if ip != '127.0.0.1' and not ip.startswith('169.254'):
                        interfaces.append({
                            'interface': interface,
                            'ip': ip,
                            'netmask': addr.get('netmask', ''),
                            'type': get_interface_type(interface)
                        })
    except Exception as e:
        logger.warning(f"Error obteniendo interfaces: {e}")
    
    return interfaces

def get_interface_type(interface_name):
    """Determina el tipo de interfaz de red"""
    interface_name = interface_name.lower()
    if 'wifi' in interface_name or 'wlan' in interface_name or 'wireless' in interface_name:
        return 'WiFi'
    elif 'eth' in interface_name or 'ethernet' in interface_name or 'en' in interface_name:
        return 'Ethernet'
    elif 'lo' in interface_name:
        return 'Loopback'
    else:
        return 'Desconocido'

def get_best_ip():
    """Obtiene la mejor IP disponible para el servidor"""
    interfaces = get_network_interfaces()
    
    if not interfaces:
        return "127.0.0.1"
    
    wifi_interfaces = [i for i in interfaces if i['type'] == 'WiFi']
    ethernet_interfaces = [i for i in interfaces if i['type'] == 'Ethernet']
    
    if wifi_interfaces:
        return wifi_interfaces[0]['ip']
    elif ethernet_interfaces:
        return ethernet_interfaces[0]['ip']
    else:
        return interfaces[0]['ip']

def get_network_info():
    """Obtiene información completa de la red"""
    interfaces = get_network_interfaces()
    best_ip = get_best_ip()
    
    network_info = {
        'primary_ip': best_ip,
        'interfaces': interfaces,
        'network_name': get_network_name(),
        'total_interfaces': len(interfaces)
    }
    
    return network_info

def get_network_name():
    """Obtiene el nombre de la red WiFi actual"""
    try:
        system = platform.system()
        if system == "Windows":
            result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                  capture_output=True, text=True)
            return "Red Windows"
        elif system == "Darwin":
            result = subprocess.run(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I'], 
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'SSID' in line:
                    return line.split(':')[1].strip()
        elif system == "Linux":
            result = subprocess.run(['iwgetid', '-r'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
    except Exception as e:
        logger.debug(f"No se pudo obtener nombre de red: {e}")
    
    return "Red Local"

# Monitor de cambios de red
class NetworkMonitor:
    def __init__(self, callback=None):
        self.callback = callback
        self.current_ip = None
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Inicia el monitoreo de cambios de red"""
        if not self.monitoring:
            self.monitoring = True
            self.current_ip = get_best_ip()
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("🔍 Monitor de red iniciado")
    
    def stop_monitoring(self):
        """Detiene el monitoreo"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        logger.info("🔍 Monitor de red detenido")
    
    def _monitor_loop(self):
        """Loop principal del monitor"""
        while self.monitoring:
            try:
                new_ip = get_best_ip()
                if new_ip != self.current_ip:
                    logger.info(f"🔄 Cambio de IP detectado: {self.current_ip} → {new_ip}")
                    old_ip = self.current_ip
                    self.current_ip = new_ip
                    
                    if self.callback:
                        self.callback(old_ip, new_ip)
                
                time_module.sleep(5)
            except Exception as e:
                logger.error(f"Error en monitor de red: {e}")
                time_module.sleep(10)

# Instancia global del monitor
network_monitor = NetworkMonitor()

def on_network_change(old_ip, new_ip):
    """Callback cuando cambia la red"""
    network_info = get_network_info()
    logger.info("=" * 60)
    logger.info("🌐 CAMBIO DE RED DETECTADO")
    logger.info(f"   IP anterior: {old_ip}")
    logger.info(f"   IP nueva: {new_ip}")
    logger.info(f"   Red: {network_info['network_name']}")
    logger.info(f"   Interfaces activas: {network_info['total_interfaces']}")
    logger.info("   URLs actualizadas:")
    logger.info(f"   - Local: http://127.0.0.1:8001")
    logger.info(f"   - Red:   http://{new_ip}:8001")
    logger.info("=" * 60)

network_monitor.callback = on_network_change

# Modelos de base de datos
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True)
    nombre_completo = Column(String, nullable=False)
    matricula = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    rol = Column(String, default="student")
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    ultimo_acceso = Column(DateTime)
    carrera_id = Column(Integer)
    grupo_id = Column(Integer)
    semestre = Column(Integer, default=4)
    especialidad = Column(String)
    salon = Column(String)

class Asistencia(Base):
    __tablename__ = "asistencias"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    presente = Column(Boolean, default=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    materia_id = Column(Integer)

class Carrera(Base):
    __tablename__ = "carreras"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)
    codigo = Column(String, nullable=False, unique=True)
    semestres = Column(Integer, nullable=False, default=9)
    activa = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

class Materia(Base):
    __tablename__ = "materias"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    carrera_id = Column(Integer, ForeignKey("carreras.id"))
    semestre = Column(Integer, nullable=False)
    codigo = Column(String)
    creditos = Column(Integer, default=5)
    activa = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    horas_teoria = Column(Integer, default=0)
    horas_practica = Column(Integer, default=0)
    clave_oficial = Column(String)

class Grupo(Base):
    __tablename__ = "grupos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    carrera_id = Column(Integer, ForeignKey("carreras.id"))
    semestre = Column(Integer, nullable=False)
    periodo = Column(String, nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    salon = Column(String)
    turno = Column(String)

class AsignacionMaestro(Base):
    __tablename__ = "asignaciones_maestro"
    
    id = Column(Integer, primary_key=True, index=True)
    maestro_id = Column(Integer, ForeignKey("usuarios.id"))
    materia_id = Column(Integer, ForeignKey("materias.id"))
    grupo_id = Column(Integer, ForeignKey("grupos.id"))
    periodo = Column(String, nullable=False, default="2024-1")
    activa = Column(Boolean, default=True)
    fecha_asignacion = Column(DateTime, default=datetime.utcnow)
    
class HorarioDetallado(Base):
    __tablename__ = "horarios_detallados"
    
    id = Column(Integer, primary_key=True, index=True)
    materia_id = Column(Integer, ForeignKey("materias.id"))
    grupo_id = Column(Integer, ForeignKey("grupos.id"))
    dia_semana = Column(String, nullable=False)
    hora_inicio = Column(String, nullable=False)
    hora_fin = Column(String, nullable=False)
    tipo_clase = Column(String, default="Teoría")
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Esquemas Pydantic
class TagRFID(BaseModel):
    tag: str

class StudentRegistration(BaseModel):
    uid: str
    nombre_completo: str
    matricula: str
    email: str
    password: Optional[str] = "123456"
    carrera_id: Optional[int] = 1
    semestre: Optional[int] = 4

class TeacherRegistration(BaseModel):
    nombre_completo: str
    matricula: str
    email: str
    password: str
    uid: Optional[str] = None
    carrera_id: Optional[int] = 1
    especialidad: Optional[str] = None

class AdminLogin(BaseModel):
    username: str
    password: str

class TeacherLogin(BaseModel):
    matricula: str
    password: str

class SubjectCreate(BaseModel):
    nombre: str
    codigo: Optional[str] = None
    semestre: int
    creditos: int = 5
    carrera_id: int

# Funciones de utilidad
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, password_hash = hashed.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"❌ Error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
            headers={"WWW-Authenticate": "Bearer"},
        )

def assign_group_by_matricula(matricula: str, db: Session) -> tuple:
    """
    Asigna grupo y salón automáticamente basado en las listas reales de estudiantes del TESJI
    Retorna: (grupo_id, salon)
    """
    try:
        logger.info(f"🔍 Verificando matrícula: {matricula}")
        
        # Verificar si ya existe una asignación manual
        from sqlalchemy import text
        result = db.execute(text("""
        SELECT g.id, u.salon FROM grupos g 
        JOIN usuarios u ON u.grupo_id = g.id 
        WHERE u.matricula = ? AND u.rol = 'student'
        """), (matricula,))
        
        existing = result.fetchone()
        if existing:
            logger.info(f"✅ Asignación existente encontrada: Grupo {existing[0]}, Salón {existing[1]}")
            return existing[0], existing[1]
        
        # Asignación basada en listas reales
        if matricula in GRUPO_3402_MATRICULAS:
            # Buscar o crear grupo 3402
            grupo = db.query(Grupo).filter(Grupo.nombre.like("%3402%")).first()
            if not grupo:
                # Crear grupo 3402 si no existe
                carrera_isc = db.query(Carrera).filter(Carrera.codigo == "ISC").first()
                if carrera_isc:
                    grupo = Grupo(
                        nombre="Grupo 3402",
                        carrera_id=carrera_isc.id,
                        semestre=4,
                        periodo="2024-1",
                        salon="N1",
                        turno="Matutino"
                    )
                    db.add(grupo)
                    db.commit()
                    db.refresh(grupo)
            
            if grupo:
                logger.info(f"✅ Matrícula {matricula} asignada al Grupo 3402 - Salón N1")
                return grupo.id, "N1"
                
        elif matricula in GRUPO_3401_MATRICULAS:
            # Buscar o crear grupo 3401
            grupo = db.query(Grupo).filter(Grupo.nombre.like("%3401%")).first()
            if not grupo:
                # Crear grupo 3401 si no existe
                carrera_isc = db.query(Carrera).filter(Carrera.codigo == "ISC").first()
                if carrera_isc:
                    grupo = Grupo(
                        nombre="Grupo 3401",
                        carrera_id=carrera_isc.id,
                        semestre=4,
                        periodo="2024-1",
                        salon="N2",
                        turno="Matutino"
                    )
                    db.add(grupo)
                    db.commit()
                    db.refresh(grupo)
            
            if grupo:
                logger.info(f"✅ Matrícula {matricula} asignada al Grupo 3401 - Salón N2")
                return grupo.id, "N2"
        
        # Si no está en ninguna lista, asignar por patrón numérico como fallback
        logger.warning(f"⚠️ Matrícula {matricula} no encontrada en listas oficiales")
        try:
            ultimos_digitos = int(matricula[-2:]) if len(matricula) >= 2 else 0
            
            if ultimos_digitos % 2 == 0:
                grupo = db.query(Grupo).filter(Grupo.nombre.like("%3402%")).first()
                salon = "N1"
            else:
                grupo = db.query(Grupo).filter(Grupo.nombre.like("%3401%")).first()
                salon = "N2"
            
            if grupo:
                logger.info(f"⚠️ Matrícula {matricula} asignada por patrón numérico: {grupo.nombre} - Salón {salon}")
                return grupo.id, salon
            
        except ValueError:
            pass
        
        # Último recurso: asignar al primer grupo disponible
        grupo = db.query(Grupo).filter(Grupo.activo == True).first()
        if grupo:
            salon = grupo.salon or "N1"
            logger.info(f"⚠️ Matrícula {matricula} asignada al primer grupo disponible: {grupo.nombre} - Salón {salon}")
            return grupo.id, salon
            
    except Exception as e:
        logger.error(f"Error asignando grupo para matrícula {matricula}: {e}")
        return None, None

    return None, None

def get_student_schedule_by_salon(salon: str) -> dict:
    """Obtiene el horario según el salón asignado"""
    if salon == "N1":
        return HORARIO_SALON_N1
    elif salon == "N2":
        return HORARIO_SALON_N2
    else:
        # Horario por defecto
        return HORARIO_SALON_N1

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema RFID TESJI - Completo",
    description="Sistema de control de asistencias con RFID - Versión Final",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.mount("/templates", StaticFiles(directory="templates"), name="templates")
except:
    pass

# Rutas para servir páginas HTML
@app.get("/welcome.html", response_class=HTMLResponse)
async def serve_welcome():
    try:
        with open("templates/welcome.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Página no encontrada</h1>", status_code=404)

@app.get("/admin.html", response_class=HTMLResponse)
async def serve_admin():
    try:
        with open("templates/admin.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Página no encontrada</h1>", status_code=404)

@app.get("/teacher.html", response_class=HTMLResponse)
async def serve_teacher():
    try:
        with open("templates/enhanced-teacher.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Página no encontrada</h1>", status_code=404)

@app.get("/student.html", response_class=HTMLResponse)
async def serve_student():
    try:
        with open("templates/student.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Página no encontrada</h1>", status_code=404)

@app.get("/login-teacher.html", response_class=HTMLResponse)
async def serve_teacher_login():
    try:
        with open("templates/login-teacher.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Página no encontrada</h1>", status_code=404)

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time_module.time()
    
    logger.info(f"📥 {request.method} {request.url.path} - {request.client.host}")
    
    response = await call_next(request)
    
    process_time = time_module.time() - start_time
    logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
    
    return response

# ==================== ENDPOINTS PRINCIPALES ====================

@app.post("/api/rfid")
async def process_rfid_main(tag_data: TagRFID, request: Request, db: Session = Depends(get_db)):
    """Endpoint principal para procesar RFID"""
    global server_stats
    server_stats["rfid_requests"] += 1
    
    try:
        logger.info(f"🎫 RFID RECIBIDO: {tag_data.tag}")
        logger.info(f"   Origen: {request.client.host}")
        logger.info(f"   Timestamp: {datetime.now().isoformat()}")
        
        # Buscar usuario en base de datos
        logger.info(f"🔍 Buscando usuario con UID: {tag_data.tag}")
        usuario = db.query(Usuario).filter(Usuario.uid == tag_data.tag).first()
        
        if usuario:
            logger.info(f"✅ Usuario encontrado: {usuario.nombre_completo} ({usuario.matricula}) - {usuario.rol}")
            
            if usuario.rol == "student":
                # Registrar asistencia para estudiante
                logger.info("📝 Registrando asistencia...")
                
                # Verificar si ya tiene asistencia hoy
                hoy = datetime.now().date()
                asistencia_existente = db.query(Asistencia).filter(
                    Asistencia.usuario_id == usuario.id,
                    Asistencia.fecha >= datetime.combine(hoy, time.min),
                    Asistencia.fecha <= datetime.combine(hoy, time.max)
                ).first()
                
                if not asistencia_existente:
                    nueva_asistencia = Asistencia(
                        usuario_id=usuario.id,
                        presente=True,
                        fecha=datetime.now()
                    )
                    db.add(nueva_asistencia)
                    db.commit()
                    logger.info("✅ Asistencia registrada exitosamente")
                    mensaje = f"Bienvenido {usuario.nombre_completo}. Asistencia registrada."
                else:
                    logger.info("ℹ️ Asistencia ya registrada hoy")
                    mensaje = f"Bienvenido {usuario.nombre_completo}. Asistencia ya registrada hoy."
                
                server_stats["successful_recognitions"] += 1
                
                # Obtener información del grupo y salón
                grupo_info = None
                if usuario.grupo_id:
                    grupo = db.query(Grupo).filter(Grupo.id == usuario.grupo_id).first()
                    if grupo:
                        grupo_info = {
                            "nombre": grupo.nombre,
                            "salon": usuario.salon or grupo.salon,
                            "turno": grupo.turno
                        }
                
                response_data = {
                    "type": "rfid_detected",
                    "success": True,
                    "exists": True,
                    "message": mensaje,
                    "uid": tag_data.tag,
                    "timestamp": time_module.time(),
                    "user": {
                        "id": usuario.id,
                        "nombre": usuario.nombre_completo,
                        "matricula": usuario.matricula,
                        "rol": usuario.rol,
                        "uid": usuario.uid,
                        "salon": usuario.salon,
                        "grupo": grupo_info
                    },
                    "attendance_registered": not bool(asistencia_existente)
                }
            else:
                # Usuario no estudiante
                logger.info(f"ℹ️ Usuario {usuario.rol} detectado")
                server_stats["successful_recognitions"] += 1
                
                response_data = {
                    "type": "rfid_detected",
                    "success": True,
                    "exists": True,
                    "message": f"Usuario {usuario.rol} detectado: {usuario.nombre_completo}",
                    "uid": tag_data.tag,
                    "timestamp": time_module.time(),
                    "user": {
                        "id": usuario.id,
                        "nombre": usuario.nombre_completo,
                        "matricula": usuario.matricula,
                        "rol": usuario.rol,
                        "uid": usuario.uid
                    },
                    "user_role": usuario.rol
                }
        else:
            # Usuario no encontrado
            logger.warning(f"⚠️ UID no registrado: {tag_data.tag}")
            server_stats["failed_recognitions"] += 1
            
            response_data = {
                "type": "rfid_detected",
                "success": True,
                "exists": False,
                "message": "UID no registrado. Nuevo usuario detectado.",
                "uid": tag_data.tag,
                "timestamp": time_module.time(),
                "show_registration": True
            }
        
        # Guardar para consulta posterior
        session_key = f"{tag_data.tag}_{int(time_module.time())}"
        active_rfid_sessions[tag_data.tag] = {
            "uid": tag_data.tag,
            "timestamp": time_module.time(),
            "data": response_data,
            "session_key": session_key
        }

        # Limpiar sesiones expiradas
        current_time = time_module.time()
        expired_sessions = [uid for uid, session in active_rfid_sessions.items() 
                           if current_time - session["timestamp"] > 300]
        for uid in expired_sessions:
            del active_rfid_sessions[uid]
        
        logger.info(f"💾 Respuesta preparada: exists={response_data['exists']}")
        logger.info("=" * 60)
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ ERROR procesando RFID: {e}")
        logger.error(f"   UID: {tag_data.tag}")
        logger.error(f"   Origen: {request.client.host}")
        
        error_response = {
            "type": "error",
            "success": False,
            "message": f"Error interno del servidor: {str(e)}",
            "uid": tag_data.tag,
            "timestamp": time_module.time()
        }
        
        return error_response

@app.post("/api/rfid/bridge")
async def rfid_bridge_endpoint(tag_data: TagRFID, request: Request, db: Session = Depends(get_db)):
    """Endpoint específico para el puente serial"""
    logger.info(f"🌉 BRIDGE REQUEST: {tag_data.tag} desde {request.client.host}")
    
    result = await process_rfid_main(tag_data, request, db)
    
    logger.info(f"🌉 BRIDGE RESPONSE: UID={tag_data.tag}, exists={result.get('exists')}")
    
    return result

@app.get("/api/rfid/last/{uid}")
async def get_rfid_by_uid(uid: str, db: Session = Depends(get_db)):
    """Obtiene datos RFID de un usuario específico"""
    global active_rfid_sessions
    
    if uid in active_rfid_sessions:
        session = active_rfid_sessions[uid]
        tiempo_transcurrido = time_module.time() - session["timestamp"]
        
        if tiempo_transcurrido < 300:
            return session["data"]
    
    try:
        usuario = db.query(Usuario).filter(Usuario.uid == uid).first()
        if usuario:
            return {
                "uid": uid,
                "timestamp": time_module.time(),
                "user": {
                    "id": usuario.id,
                    "nombre": usuario.nombre_completo,
                    "matricula": usuario.matricula,
                    "rol": usuario.rol,
                    "uid": usuario.uid,
                    "salon": usuario.salon
                },
                "exists": True,
                "message": f"Datos de {usuario.nombre_completo}"
            }
    except Exception as e:
        logger.error(f"Error buscando usuario {uid}: {e}")
    
    return {"uid": None, "timestamp": None, "message": "No hay datos RFID para este usuario"}

@app.get("/api/rfid/last")
async def get_last_rfid():
    """Obtiene el último UID RFID procesado"""
    global active_rfid_sessions
    
    logger.debug(f"🔍 Consulta último RFID de todas las sesiones activas")
    
    if not active_rfid_sessions:
        return {"uid": None, "timestamp": None, "message": "No hay datos RFID recientes"}
    
    latest_session = None
    latest_timestamp = 0
    
    for uid, session in active_rfid_sessions.items():
        if session["timestamp"] > latest_timestamp:
            latest_timestamp = session["timestamp"]
            latest_session = session
    
    if latest_session:
        tiempo_transcurrido = time_module.time() - latest_session["timestamp"]
        
        if tiempo_transcurrido < 30:
            logger.debug("✅ Devolviendo datos RFID válidos")
            return latest_session["data"]
        else:
            logger.debug(f"⏰ Datos RFID expirados ({tiempo_transcurrido:.2f}s)")
    
    return {"uid": None, "timestamp": None, "message": "No hay datos RFID recientes"}

@app.post("/api/register-student")
async def register_student(student_data: StudentRegistration, request: Request, db: Session = Depends(get_db)):
    """Registra un nuevo estudiante con asignación automática de grupo y salón"""
    global server_stats
    
    try:
        logger.info(f"📝 REGISTRO DE ESTUDIANTE: {student_data.matricula}")
        logger.info(f"   UID: {student_data.uid}")
        logger.info(f"   Nombre: {student_data.nombre_completo}")
        
        # Verificar duplicados
        if db.query(Usuario).filter(Usuario.uid == student_data.uid).first():
            logger.warning(f"⚠️ UID ya registrado: {student_data.uid}")
            raise HTTPException(status_code=400, detail="Este UID ya está registrado")
        
        if db.query(Usuario).filter(Usuario.matricula == student_data.matricula).first():
            logger.warning(f"⚠️ Matrícula ya registrada: {student_data.matricula}")
            raise HTTPException(status_code=400, detail="Esta matrícula ya está registrada")
        
        if db.query(Usuario).filter(Usuario.email == student_data.email).first():
            logger.warning(f"⚠️ Email ya registrado: {student_data.email}")
            raise HTTPException(status_code=400, detail="Este email ya está registrado")
        
        # Asignar grupo y salón automáticamente
        grupo_id, salon = assign_group_by_matricula(student_data.matricula, db)
        if grupo_id and salon:
            logger.info(f"✅ Asignación automática: Grupo {grupo_id}, Salón {salon}")
        
        # Crear estudiante
        nuevo_usuario = Usuario(
            uid=student_data.uid,
            nombre_completo=student_data.nombre_completo,
            matricula=student_data.matricula,
            email=student_data.email,
            password_hash=hash_password(student_data.password) if student_data.password else None,
            rol="student",
            carrera_id=student_data.carrera_id,
            grupo_id=grupo_id,
            semestre=student_data.semestre,
            salon=salon
        )
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        server_stats["new_registrations"] += 1
        
        logger.info(f"✅ Estudiante registrado exitosamente: ID {nuevo_usuario.id}")
        
        return {
            "success": True,
            "message": "Estudiante registrado exitosamente",
            "user": {
                "id": nuevo_usuario.id,
                "nombre": nuevo_usuario.nombre_completo,
                "matricula": nuevo_usuario.matricula,
                "email": nuevo_usuario.email,
                "rol": nuevo_usuario.rol,
                "uid": nuevo_usuario.uid,
                "carrera_id": nuevo_usuario.carrera_id,
                "semestre": nuevo_usuario.semestre,
                "grupo_id": nuevo_usuario.grupo_id,
                "salon": nuevo_usuario.salon
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error registrando estudiante: {e}")
        db.rollback()
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/api/admin/login")
async def admin_login(request: Request, admin_data: AdminLogin):
    """Login exclusivo para administradores"""
    try:
        logger.info(f"🔐 LOGIN ADMIN: {admin_data.username}")
        
        ADMIN_CREDENTIALS = {
            "admin": "admin123",
            "tesji_admin": "tesji2024",
            "administrador": "admin123"
        }
        
        if admin_data.username not in ADMIN_CREDENTIALS:
            logger.warning(f"❌ Usuario admin no válido: {admin_data.username}")
            return {"success": False, "message": "Usuario administrador no válido"}
        
        if ADMIN_CREDENTIALS[admin_data.username] != admin_data.password:
            logger.warning(f"❌ Contraseña admin incorrecta: {admin_data.username}")
            return {"success": False, "message": "Contraseña incorrecta"}
        
        access_token = create_access_token(
            data={"sub": "admin", "rol": "admin", "username": admin_data.username}
        )
        
        logger.info(f"✅ Login admin exitoso: {admin_data.username}")
        
        return {
            "success": True,
            "message": "Login de administrador exitoso",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "username": admin_data.username,
                "rol": "admin",
                "nombre": "Administrador del Sistema"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error en login admin: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/api/teacher/login")
async def teacher_login(request: Request, teacher_data: TeacherLogin, db: Session = Depends(get_db)):
    """Login exclusivo para maestros"""
    try:
        logger.info(f"🔐 LOGIN MAESTRO: {teacher_data.matricula}")
        
        user = db.query(Usuario).filter(
            Usuario.matricula == teacher_data.matricula,
            Usuario.rol == "teacher"
        ).first()
        
        if not user:
            logger.warning(f"❌ Maestro no encontrado: {teacher_data.matricula}")
            return {"success": False, "message": "Maestro no encontrado"}
        
        if not user.password_hash or not verify_password(teacher_data.password, user.password_hash):
            logger.warning(f"❌ Contraseña incorrecta: {teacher_data.matricula}")
            return {"success": False, "message": "Contraseña incorrecta"}
        
        access_token = create_access_token(
            data={"sub": str(user.id), "rol": "teacher", "matricula": user.matricula}
        )
        
        logger.info(f"✅ Login maestro exitoso: {user.nombre_completo}")
        
        return {
            "success": True,
            "message": "Login de maestro exitoso",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "nombre": user.nombre_completo,
                "matricula": user.matricula,
                "email": user.email,
                "rol": user.rol,
                "carrera_id": user.carrera_id,
                "especialidad": user.especialidad
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error en login maestro: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/api/teacher/register")
async def teacher_register(teacher_data: TeacherRegistration, request: Request, db: Session = Depends(get_db)):
    """Registra un nuevo maestro"""
    try:
        logger.info(f"📝 REGISTRO DE MAESTRO: {teacher_data.matricula}")
        
        # Verificar duplicados
        if db.query(Usuario).filter(Usuario.matricula == teacher_data.matricula).first():
            return {"success": False, "message": "Esta matrícula ya está registrada"}
        
        if db.query(Usuario).filter(Usuario.email == teacher_data.email).first():
            return {"success": False, "message": "Este email ya está registrado"}
        
        if teacher_data.uid and db.query(Usuario).filter(Usuario.uid == teacher_data.uid).first():
            return {"success": False, "message": "Este UID ya está registrado"}
        
        # Crear maestro
        nuevo_maestro = Usuario(
            uid=teacher_data.uid,
            nombre_completo=teacher_data.nombre_completo,
            matricula=teacher_data.matricula,
            email=teacher_data.email,
            password_hash=hash_password(teacher_data.password),
            rol="teacher",
            carrera_id=teacher_data.carrera_id,
            especialidad=teacher_data.especialidad
        )
        
        db.add(nuevo_maestro)
        db.commit()
        db.refresh(nuevo_maestro)
        
        logger.info(f"✅ Maestro registrado: {nuevo_maestro.nombre_completo}")
        
        return {
            "success": True,
            "message": "Maestro registrado exitosamente",
            "user": {
                "id": nuevo_maestro.id,
                "nombre": nuevo_maestro.nombre_completo,
                "matricula": nuevo_maestro.matricula,
                "email": nuevo_maestro.email,
                "rol": nuevo_maestro.rol,
                "carrera_id": nuevo_maestro.carrera_id,
                "especialidad": nuevo_maestro.especialidad
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error registrando maestro: {e}")
        db.rollback()
        return {"success": False, "message": f"Error: {str(e)}"}

# ENDPOINTS DE HORARIOS OPTIMIZADOS

@app.get("/api/student/schedule")
async def get_student_schedule(uid: str = None, db: Session = Depends(get_db)):
    """Obtiene el horario del estudiante por UID - Solo su horario asignado"""
    try:
        if not uid:
            return {"success": False, "message": "UID requerido"}
        
        logger.info(f"📅 Consultando horario para UID: {uid}")
        
        # Buscar estudiante por UID
        student = db.query(Usuario).filter(
            Usuario.uid == uid,
            Usuario.rol == "student"
        ).first()
        
        if not student:
            logger.warning(f"❌ Estudiante no encontrado para UID: {uid}")
            return {"success": False, "message": "Estudiante no encontrado"}
        
        logger.info(f"✅ Estudiante encontrado: {student.nombre_completo} (Salón: {student.salon})")
        
        # Obtener horario según el salón asignado
        salon = student.salon or "N1"  # Por defecto N1 si no tiene salón
        schedule_by_day = get_student_schedule_by_salon(salon)
        
        # Obtener información del grupo
        grupo_info = {"nombre": "Sin grupo", "salon": salon, "turno": "Matutino", "semestre": student.semestre}
        if student.grupo_id:
            grupo = db.query(Grupo).filter(Grupo.id == student.grupo_id).first()
            if grupo:
                grupo_info = {
                    "nombre": grupo.nombre,
                    "salon": salon,
                    "turno": grupo.turno or "Matutino",
                    "semestre": grupo.semestre
                }
        
        # Obtener carrera
        carrera_nombre = "Ingeniería en Sistemas Computacionales"
        if student.carrera_id:
            carrera = db.query(Carrera).filter(Carrera.id == student.carrera_id).first()
            if carrera:
                carrera_nombre = carrera.nombre
        
        grupo_info["carrera"] = carrera_nombre
        
        # Calcular estadísticas
        materias_unicas = set()
        total_clases = 0
        dias_con_clases = 0
        
        for dia, clases in schedule_by_day.items():
            if clases:
                dias_con_clases += 1
                total_clases += len(clases)
                for clase in clases:
                    materias_unicas.add(clase["materia"])
        
        response_data = {
            "success": True,
            "student": {
                "nombre": student.nombre_completo,
                "matricula": student.matricula,
                "uid": student.uid,
                "salon": salon
            },
            "group": grupo_info,
            "schedule_by_day": schedule_by_day,
            "total_subjects": len(materias_unicas),
            "total_classes": total_clases,
            "days_with_classes": dias_con_clases
        }
        
        logger.info(f"✅ Horario procesado exitosamente para Salón {salon}")
        logger.info(f"   - Materias: {len(materias_unicas)}")
        logger.info(f"   - Clases totales: {total_clases}")
        logger.info(f"   - Días con clases: {dias_con_clases}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo horario del estudiante: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "message": f"Error interno: {str(e)}"}

@app.get("/api/schedule/today")
async def get_today_schedule(uid: str = None, role: str = "student", db: Session = Depends(get_db)):
    """Obtiene el horario de hoy para estudiante"""
    try:
        from datetime import datetime
        
        # Obtener día actual en español
        dias_semana = {
            0: "Lunes", 1: "Martes", 2: "Miércoles", 
            3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
        }
        hoy = dias_semana[datetime.now().weekday()]
        
        if role == "student":
            # Obtener horario completo del estudiante
            schedule_response = await get_student_schedule(uid, db)
            if not schedule_response["success"]:
                return schedule_response
            
            # Filtrar solo el día de hoy
            today_classes = schedule_response["schedule_by_day"].get(hoy, [])
            
            return {
                "success": True,
                "today": hoy,
                "classes": today_classes,
                "student": schedule_response["student"],
                "group": schedule_response["group"]
            }
        
        else:
            return {"success": False, "message": "Función para maestros requiere autenticación"}
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo horario de hoy: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/api/teacher/schedule")
async def get_teacher_schedule(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Obtiene el horario completo del maestro"""
    try:
        if not credentials:
            return {"success": False, "message": "Token requerido"}
        
        payload = verify_token(credentials.credentials)
        teacher_id = payload.get("sub")
        
        if not teacher_id:
            return {"success": False, "message": "Token inválido"}
        
        # Buscar maestro
        teacher = db.query(Usuario).filter(
            Usuario.id == teacher_id,
            Usuario.rol == "teacher"
        ).first()
        
        if not teacher:
            return {"success": False, "message": "Maestro no encontrado"}
        
        # Horario de ejemplo para maestros (basado en materias reales del TESJI)
        schedule_by_day = {
            "Lunes": [
                {
                    "materia": "Tópicos Avanzados de Programación",
                    "codigo": "SCD-1027",
                    "grupo": "Grupo N1",
                    "salon": "N1",
                    "hora_inicio": "13:00",
                    "hora_fin": "15:00",
                    "tipo": "Práctica",
                    "creditos": 5,
                },
                {
                    "materia": "Fundamentos de Base de Datos",
                    "codigo": "AEF-1031",
                    "grupo": "Grupo N1",
                    "salon": "N1",
                    "hora_inicio": "15:00",
                    "hora_fin": "18:00",
                    "tipo": "Teoría",
                    "creditos": 5,
                }
            ],
            "Martes": [
                {
                    "materia": "Tópicos Avanzados de Programación",
                    "codigo": "SCD-1027",
                    "grupo": "Grupo N1",
                    "salon": "N1",
                    "hora_inicio": "13:00",
                    "hora_fin": "15:00",
                    "tipo": "Práctica",
                    "creditos": 5,
                }
            ],
            "Miércoles": [
                {
                    "materia": "Arquitectura de Computadoras",
                    "codigo": "SCD-1003",
                    "grupo": "Grupo N1",
                    "salon": "N1",
                    "hora_inicio": "11:00",
                    "hora_fin": "13:00",
                    "tipo": "Teoría",
                    "creditos": 5,
                },
                {
                    "materia": "Taller de Sistemas Operativos",
                    "codigo": "SCA-1026",
                    "grupo": "Grupo N1",
                    "salon": "N1",
                    "hora_inicio": "13:00",
                    "hora_fin": "15:00",
                    "tipo": "Práctica",
                    "creditos": 4,
                }
            ],
            "Jueves": [
                {
                    "materia": "Fundamentos de Base de Datos",
                    "codigo": "AEF-1031",
                    "grupo": "Grupo N1",
                    "salon": "N1",
                    "hora_inicio": "11:00",
                    "hora_fin": "13:00",
                    "tipo": "Teoría",
                    "creditos": 5,
                },
                {
                    "materia": "Tópicos Avanzados de Programación",
                    "codigo": "SCD-1027",
                    "grupo": "Grupo N1",
                    "salon": "N1",
                    "hora_inicio": "14:00",
                    "hora_fin": "16:00",
                    "tipo": "Práctica",
                    "creditos": 5,
                }
            ],
            "Viernes": [
                {
                    "materia": "Taller de Sistemas Operativos",
                    "codigo": "SCA-1026",
                    "grupo": "Grupo N1",
                    "salon": "N1",
                    "hora_inicio": "07:00",
                    "hora_fin": "09:00",
                    "tipo": "Práctica",
                    "creditos": 4,
                },
                {
                    "materia": "Arquitectura de Computadoras",
                    "codigo": "SCD-1003",
                    "grupo": "Grupo N1",
                    "salon": "N1",
                    "hora_inicio": "11:00",
                    "hora_fin": "14:00",
                    "tipo": "Teoría",
                    "creditos": 5,
                }
            ],
            "Sábado": [],
            "Domingo": []
        }
        
        # Calcular estadísticas
        total_classes = 0
        total_hours = 0
        days_with_classes = 0
        
        for dia, clases in schedule_by_day.items():
            if clases:
                days_with_classes += 1
                total_classes += len(clases)
                for clase in clases:
                    # Calcular horas
                    inicio = datetime.strptime(clase["hora_inicio"], "%H:%M")
                    fin = datetime.strptime(clase["hora_fin"], "%H:%M")
                    horas = (fin - inicio).seconds / 3600
                    total_hours += horas
        
        return {
            "success": True,
            "teacher": {
                "id": teacher.id,
                "nombre": teacher.nombre_completo,
                "matricula": teacher.matricula,
                "especialidad": teacher.especialidad or "Docente"
            },
            "schedule_by_day": schedule_by_day,
            "total_classes": total_classes,
            "total_hours_per_week": int(total_hours),
            "days_with_classes": days_with_classes
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo horario del maestro: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/api/teacher/subjects")
async def get_teacher_subjects(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Obtiene las materias asignadas al maestro"""
    try:
        if not credentials:
            return {"success": False, "message": "Token requerido"}
        
        payload = verify_token(credentials.credentials)
        teacher_id = payload.get("sub")
        
        if not teacher_id:
            return {"success": False, "message": "Token inválido"}
        
        # Buscar maestro
        teacher = db.query(Usuario).filter(
            Usuario.id == teacher_id,
            Usuario.rol == "teacher"
        ).first()
        
        if not teacher:
            return {"success": False, "message": "Maestro no encontrado"}
        
        # Materias de ejemplo basadas en el horario real del TESJI
        subjects = [
            {
                "id": 1,
                "nombre": "Tópicos Avanzados de Programación",
                "codigo": "SCD-1027",
                "carrera": "Ingeniería en Sistemas Computacionales",
                "semestre": 4,
                "grupo": "Grupo N1",
                "horario": "Lun 13:00-15:00, Mar 13:00-15:00, Jue 14:00-16:00",
                "aula": "N1",
                "estudiantes_inscritos": 45,
                "creditos": 5,
                "maestro": teacher.nombre_completo,
            },
            {
                "id": 2,
                "nombre": "Fundamentos de Base de Datos",
                "codigo": "AEF-1031",
                "carrera": "Ingeniería en Sistemas Computacionales",
                "semestre": 4,
                "grupo": "Grupo N1",
                "horario": "Lun 15:00-18:00, Jue 11:00-13:00",
                "aula": "N1",
                "estudiantes_inscritos": 45,
                "creditos": 5,
                "maestro": teacher.nombre_completo,
            },
            {
                "id": 3,
                "nombre": "Arquitectura de Computadoras",
                "codigo": "SCD-1003",
                "carrera": "Ingeniería en Sistemas Computacionales",
                "semestre": 4,
                "grupo": "Grupo N1",
                "horario": "Mié 11:00-13:00, Vie 11:00-14:00",
                "aula": "N1",
                "estudiantes_inscritos": 45,
                "creditos": 5,
                "maestro": teacher.nombre_completo,
            },
            {
                "id": 4,
                "nombre": "Taller de Sistemas Operativos",
                "codigo": "SCA-1026",
                "carrera": "Ingeniería en Sistemas Computacionales",
                "semestre": 4,
                "grupo": "Grupo N1",
                "horario": "Mié 13:00-15:00, Vie 07:00-09:00",
                "aula": "N1",
                "estudiantes_inscritos": 45,
                "creditos": 4,
                "maestro": teacher.nombre_completo,
            }
        ]
        
        return {
            "success": True,
            "subjects": subjects,
            "total": len(subjects)
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo materias del maestro: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/api/teacher/profile")
async def get_teacher_profile(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Obtiene el perfil del maestro"""
    try:
        if not credentials:
            return {"success": False, "message": "Token requerido"}
        
        payload = verify_token(credentials.credentials)
        teacher_id = payload.get("sub")
        
        if not teacher_id:
            return {"success": False, "message": "Token inválido"}
        
        # Buscar maestro
        teacher = db.query(Usuario).filter(
            Usuario.id == teacher_id,
            Usuario.rol == "teacher"
        ).first()
        
        if not teacher:
            return {"success": False, "message": "Maestro no encontrado"}
        
        return {
            "success": True,
            "teacher": {
                "id": teacher.id,
                "nombre": teacher.nombre_completo,
                "matricula": teacher.matricula,
                "email": teacher.email,
                "especialidad": teacher.especialidad or "Docente",
                "carrera_id": teacher.carrera_id
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo perfil del maestro: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

# ENDPOINTS PARA ADMINISTRADORES - CORREGIDOS

@app.get("/api/admin/dashboard-stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Obtiene estadísticas para el dashboard del administrador"""
    try:
        total_students = db.query(Usuario).filter(Usuario.rol == "student", Usuario.activo == True).count()
        total_teachers = db.query(Usuario).filter(Usuario.rol == "teacher", Usuario.activo == True).count()
        total_careers = db.query(Carrera).filter(Carrera.activa == True).count()
        
        # Asistencias de hoy
        today = datetime.now().date()
        today_attendance = db.query(Asistencia).filter(
            func.date(Asistencia.fecha) == today
        ).count()
        
        return {
            "success": True,
            "totalStudents": total_students,
            "totalTeachers": total_teachers,
            "totalCareers": total_careers,
            "todayAttendance": today_attendance
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return {"success": False, "message": str(e)}

@app.get("/api/admin/recent-activity")
async def get_recent_activity(db: Session = Depends(get_db)):
    """Obtiene actividad reciente del sistema"""
    try:
        # Últimas asistencias
        recent_attendance = db.query(Asistencia).join(
            Usuario, Asistencia.usuario_id == Usuario.id
        ).filter(
            Usuario.activo == True
        ).order_by(Asistencia.fecha.desc()).limit(10).all()
        
        activity = []
        for attendance in recent_attendance:
            user = db.query(Usuario).filter(Usuario.id == attendance.usuario_id).first()
            if user:
                activity.append({
                    "message": f"{user.nombre_completo} registró asistencia",
                    "timestamp": attendance.fecha.isoformat(),
                    "type": "attendance"
                })
        
        return activity
    except Exception as e:
        logger.error(f"Error obteniendo actividad reciente: {e}")
        return []

@app.get("/api/admin/students-by-career")
async def get_students_by_career(db: Session = Depends(get_db)):
    """Obtiene estudiantes agrupados por carrera"""
    try:
        from sqlalchemy import text
        query = text("""
        SELECT c.nombre as career, COUNT(u.id) as count
        FROM carreras c
        LEFT JOIN usuarios u ON c.id = u.carrera_id AND u.rol = 'student' AND u.activo = 1
        WHERE c.activa = 1
        GROUP BY c.id, c.nombre
        ORDER BY count DESC
        """)
        
        result = db.execute(query)
        data = []
        for row in result:
            data.append({
                "career": row[0],
                "count": row[1]
            })
        
        return data
    except Exception as e:
        logger.error(f"Error obteniendo estudiantes por carrera: {e}")
        return []

@app.get("/api/admin/server-status")
async def get_server_status():
    """Obtiene estado del servidor"""
    try:
        network_info = get_network_info()
        uptime = time_module.time() - server_stats["start_time"] if server_stats["start_time"] else 0
        
        return {
            "status": "online",
            "uptime": f"{uptime:.0f} segundos",
            "network": network_info['network_name'],
            "ip": network_info['primary_ip'],
            "rfid_requests": server_stats["rfid_requests"],
            "successful_recognitions": server_stats["successful_recognitions"]
        }
    except Exception as e:
        logger.error(f"Error obteniendo estado del servidor: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/admin/users")
async def get_admin_users(db: Session = Depends(get_db)):
    """Obtiene todos los usuarios para administración"""
    try:
        users = db.query(Usuario).filter(Usuario.activo == True).all()
        
        users_data = []
        for user in users:
            # Obtener carrera
            carrera = None
            if user.carrera_id:
                carrera = db.query(Carrera).filter(Carrera.id == user.carrera_id).first()
            
            users_data.append({
                "id": user.id,
                "name": user.nombre_completo,
                "matricula": user.matricula,
                "email": user.email,
                "role": user.rol,
                "career": carrera.nombre if carrera else "Sin carrera",
                "status": "Activo" if user.activo else "Inactivo",
                "uid": user.uid,
                "salon": user.salon
            })
        
        return users_data
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        return []

@app.get("/api/admin/careers")
async def get_admin_careers(db: Session = Depends(get_db)):
    """Obtiene todas las carreras para administración"""
    try:
        careers = db.query(Carrera).filter(Carrera.activa == True).all()
        
        careers_data = []
        for career in careers:
            careers_data.append({
                "id": career.id,
                "name": career.nombre,
                "code": career.codigo,
                "semesters": career.semestres,
                "status": "Activa" if career.activa else "Inactiva"
            })
        
        return careers_data
    except Exception as e:
        logger.error(f"Error obteniendo carreras: {e}")
        return []

@app.get("/api/admin/subjects")
async def get_admin_subjects(db: Session = Depends(get_db)):
    """Obtiene todas las materias para administración"""
    try:
        subjects = db.query(Materia).filter(Materia.activa == True).all()
        
        subjects_data = []
        for subject in subjects:
            # Obtener carrera
            carrera = db.query(Carrera).filter(Carrera.id == subject.carrera_id).first()
            
            subjects_data.append({
                "id": subject.id,
                "name": subject.nombre,
                "code": subject.codigo,
                "career": carrera.nombre if carrera else "Sin carrera",
                "semester": subject.semestre,
                "credits": subject.creditos
            })
        
        return subjects_data
    except Exception as e:
        logger.error(f"Error obteniendo materias: {e}")
        return []

@app.get("/api/admin/groups")
async def get_admin_groups(db: Session = Depends(get_db)):
    """Obtiene todos los grupos para administración"""
    try:
        groups = db.query(Grupo).filter(Grupo.activo == True).all()
        
        groups_data = []
        for group in groups:
            # Obtener carrera
            carrera = db.query(Carrera).filter(Carrera.id == group.carrera_id).first()
            
            groups_data.append({
                "id": group.id,
                "name": group.nombre,
                "classroom": group.salon,
                "career": carrera.nombre if carrera else "Sin carrera"
            })
        
        return groups_data
    except Exception as e:
        logger.error(f"Error obteniendo grupos: {e}")
        return []

@app.get("/api/admin/attendance")
async def get_admin_attendance(db: Session = Depends(get_db)):
    """Obtiene registros de asistencia para administración"""
    try:
        attendance = db.query(Asistencia).order_by(Asistencia.fecha.desc()).limit(100).all()
        
        attendance_data = []
        for record in attendance:
            # Obtener usuario
            user = db.query(Usuario).filter(Usuario.id == record.usuario_id).first()
            
            attendance_data.append({
                "id": record.id,
                "date": record.fecha.strftime("%Y-%m-%d %H:%M"),
                "student": user.nombre_completo if user else "Usuario desconocido",
                "subject": "Materia General",
                "status": "Presente" if record.presente else "Ausente"
            })
        
        return attendance_data
    except Exception as e:
        logger.error(f"Error obteniendo asistencias: {e}")
        return []

@app.get("/api/admin/schedules")
async def get_admin_schedules(db: Session = Depends(get_db)):
    """Obtiene horarios para administración"""
    try:
        schedules = db.query(HorarioDetallado).filter(HorarioDetallado.activo == True).all()
        
        schedules_data = []
        for schedule in schedules:
            # Obtener materia y grupo
            materia = db.query(Materia).filter(Materia.id == schedule.materia_id).first()
            grupo = db.query(Grupo).filter(Grupo.id == schedule.grupo_id).first()
            
            schedules_data.append({
                "id": schedule.id,
                "subject": materia.nombre if materia else "Materia desconocida",
                "group": grupo.nombre if grupo else "Grupo desconocido",
                "day": schedule.dia_semana,
                "startTime": schedule.hora_inicio,
                "endTime": schedule.hora_fin
            })
        
        return schedules_data
    except Exception as e:
        logger.error(f"Error obteniendo horarios: {e}")
        return []

# ENDPOINTS PARA CREAR NUEVOS REGISTROS

@app.post("/api/admin/users")
async def create_user(user_data: dict, db: Session = Depends(get_db)):
    """Crea un nuevo usuario desde el panel admin"""
    try:
        # Verificar duplicados
        if db.query(Usuario).filter(Usuario.matricula == user_data['matricula']).first():
            return {"success": False, "message": "Esta matrícula ya está registrada"}
        
        if user_data.get('email') and db.query(Usuario).filter(Usuario.email == user_data['email']).first():
            return {"success": False, "message": "Este email ya está registrado"}
        
        # Crear usuario
        nuevo_usuario = Usuario(
            nombre_completo=user_data['name'],
            matricula=user_data['matricula'],
            email=user_data.get('email'),
            password_hash=hash_password(user_data['password']) if user_data.get('password') else None,
            rol=user_data['role'],
            carrera_id=user_data.get('career') if user_data.get('career') else None,
            activo=True
        )
        
        # Asignar grupo automáticamente si es estudiante
        if user_data['role'] == 'student' and user_data['matricula']:
            grupo_id, salon = assign_group_by_matricula(user_data['matricula'], db)
            if grupo_id:
                nuevo_usuario.grupo_id = grupo_id
                nuevo_usuario.salon = salon
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        return {
            "success": True,
            "message": "Usuario creado exitosamente",
            "user": {
                "id": nuevo_usuario.id,
                "name": nuevo_usuario.nombre_completo,
                "matricula": nuevo_usuario.matricula,
                "role": nuevo_usuario.rol
            }
        }
        
    except Exception as e:
        logger.error(f"Error creando usuario: {e}")
        db.rollback()
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/api/admin/careers")
async def create_career(career_data: dict, db: Session = Depends(get_db)):
    """Crea una nueva carrera"""
    try:
        nueva_carrera = Carrera(
            nombre=career_data['name'],
            codigo=career_data['code'],
            semestres=career_data['semesters']
        )
        
        db.add(nueva_carrera)
        db.commit()
        db.refresh(nueva_carrera)
        
        return {
            "success": True,
            "message": "Carrera creada exitosamente",
            "career": {
                "id": nueva_carrera.id,
                "name": nueva_carrera.nombre,
                "code": nueva_carrera.codigo
            }
        }
        
    except Exception as e:
        logger.error(f"Error creando carrera: {e}")
        db.rollback()
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/api/admin/subjects")
async def create_subject(subject_data: dict, db: Session = Depends(get_db)):
    """Crea una nueva materia"""
    try:
        nueva_materia = Materia(
            nombre=subject_data['name'],
            codigo=subject_data.get('code'),
            carrera_id=subject_data['career'],
            semestre=subject_data['semester'],
            creditos=subject_data['credits']
        )
        
        db.add(nueva_materia)
        db.commit()
        db.refresh(nueva_materia)
        
        return {
            "success": True,
            "message": "Materia creada exitosamente",
            "subject": {
                "id": nueva_materia.id,
                "name": nueva_materia.nombre,
                "code": nueva_materia.codigo
            }
        }
        
    except Exception as e:
        logger.error(f"Error creando materia: {e}")
        db.rollback()
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/api/admin/groups")
async def create_group(group_data: dict, db: Session = Depends(get_db)):
    """Crea un nuevo grupo"""
    try:
        nuevo_grupo = Grupo(
            nombre=group_data['name'],
            salon=group_data['classroom'],
            carrera_id=group_data['career'],
            semestre=4,  # Por defecto
            periodo="2024-1"
        )
        
        db.add(nuevo_grupo)
        db.commit()
        db.refresh(nuevo_grupo)
        
        return {
            "success": True,
            "message": "Grupo creado exitosamente",
            "group": {
                "id": nuevo_grupo.id,
                "name": nuevo_grupo.nombre,
                "classroom": nuevo_grupo.salon
            }
        }
        
    except Exception as e:
        logger.error(f"Error creando grupo: {e}")
        db.rollback()
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/api/admin/schedules")
async def create_schedule(schedule_data: dict, db: Session = Depends(get_db)):
    """Crea un nuevo horario"""
    try:
        nuevo_horario = HorarioDetallado(
            materia_id=schedule_data['subject'],
            grupo_id=schedule_data['group'],
            dia_semana=schedule_data['day'],
            hora_inicio=schedule_data['startTime'],
            hora_fin=schedule_data['endTime']
        )
        
        db.add(nuevo_horario)
        db.commit()
        db.refresh(nuevo_horario)
        
        return {
            "success": True,
            "message": "Horario creado exitosamente",
            "schedule": {
                "id": nuevo_horario.id,
                "day": nuevo_horario.dia_semana,
                "startTime": nuevo_horario.hora_inicio,
                "endTime": nuevo_horario.hora_fin
            }
        }
        
    except Exception as e:
        logger.error(f"Error creando horario: {e}")
        db.rollback()
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/api/admin/attendance")
async def create_manual_attendance(attendance_data: dict, db: Session = Depends(get_db)):
    """Registra asistencia manual"""
    try:
        from datetime import datetime
        
        nueva_asistencia = Asistencia(
            usuario_id=attendance_data['student'],
            materia_id=attendance_data.get('subject'),
            presente=attendance_data['status'] == 'present',
            fecha=datetime.strptime(attendance_data['date'], '%Y-%m-%d')
        )
        
        db.add(nueva_asistencia)
        db.commit()
        db.refresh(nueva_asistencia)
        
        return {
            "success": True,
            "message": "Asistencia registrada exitosamente"
        }
        
    except Exception as e:
        logger.error(f"Error registrando asistencia: {e}")
        db.rollback()
        return {"success": False, "message": f"Error: {str(e)}"}

# ENDPOINTS PARA REPORTES

@app.get("/api/admin/reports/attendance")
async def generate_attendance_report(
    period: str = "today",
    start_date: str = None,
    end_date: str = None,
    format: str = "json",
    db: Session = Depends(get_db)
):
    """Genera reporte de asistencias"""
    try:
        from datetime import datetime, timedelta
        
        # Determinar rango de fechas
        if period == "today":
            start = datetime.now().date()
            end = start
        elif period == "week":
            start = datetime.now().date() - timedelta(days=7)
            end = datetime.now().date()
        elif period == "month":
            start = datetime.now().date() - timedelta(days=30)
            end = datetime.now().date()
        elif period == "custom" and start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            start = datetime.now().date()
            end = start
        
        # Consultar asistencias
        asistencias = db.query(Asistencia).join(
            Usuario, Asistencia.usuario_id == Usuario.id
        ).filter(
            func.date(Asistencia.fecha) >= start,
            func.date(Asistencia.fecha) <= end,
            Usuario.rol == "student"
        ).all()
        
        # Preparar datos
        report_data = []
        for asistencia in asistencias:
            usuario = db.query(Usuario).filter(Usuario.id == asistencia.usuario_id).first()
            if usuario:
                report_data.append({
                    "fecha": asistencia.fecha.strftime("%Y-%m-%d %H:%M"),
                    "estudiante": usuario.nombre_completo,
                    "matricula": usuario.matricula,
                    "estado": "Presente" if asistencia.presente else "Ausente",
                    "salon": usuario.salon or "N/A"
                })
        
        if format == "csv":
            # Generar CSV
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["fecha", "estudiante", "matricula", "estado", "salon"])
            writer.writeheader()
            writer.writerows(report_data)
            
            csv_content = output.getvalue()
            output.close()
            
            return StreamingResponse(
                io.BytesIO(csv_content.encode()),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=reporte_asistencias.csv"}
            )
        
        return {
            "success": True,
            "data": report_data,
            "total": len(report_data),
            "period": period,
            "start_date": start.isoformat(),
            "end_date": end.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generando reporte: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/api/admin/reports/students")
async def generate_students_report(
    career: str = "all",
    semester: str = "all",
    format: str = "json",
    db: Session = Depends(get_db)
):
    """Genera reporte de estudiantes"""
    try:
        query = db.query(Usuario).filter(Usuario.rol == "student", Usuario.activo == True)
        
        if career != "all":
            query = query.filter(Usuario.carrera_id == career)
        
        if semester != "all":
            query = query.filter(Usuario.semestre == semester)
        
        estudiantes = query.all()
        
        report_data = []
        for estudiante in estudiantes:
            carrera = db.query(Carrera).filter(Carrera.id == estudiante.carrera_id).first()
            grupo = db.query(Grupo).filter(Grupo.id == estudiante.grupo_id).first()
            
            report_data.append({
                "matricula": estudiante.matricula,
                "nombre": estudiante.nombre_completo,
                "email": estudiante.email or "N/A",
                "carrera": carrera.nombre if carrera else "N/A",
                "semestre": estudiante.semestre or "N/A",
                "grupo": grupo.nombre if grupo else "N/A",
                "salon": estudiante.salon or "N/A",
                "activo": "Sí" if estudiante.activo else "No"
            })
        
        if format == "csv":
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["matricula", "nombre", "email", "carrera", "semestre", "grupo", "salon", "activo"])
            writer.writeheader()
            writer.writerows(report_data)
            
            csv_content = output.getvalue()
            output.close()
            
            return StreamingResponse(
                io.BytesIO(csv_content.encode()),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=reporte_estudiantes.csv"}
            )
        
        return {
            "success": True,
            "data": report_data,
            "total": len(report_data)
        }
        
    except Exception as e:
        logger.error(f"Error generando reporte de estudiantes: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

# ENDPOINTS PARA ELIMINAR/EDITAR

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Elimina un usuario"""
    try:
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not usuario:
            return {"success": False, "message": "Usuario no encontrado"}
        
        # Marcar como inactivo en lugar de eliminar
        usuario.activo = False
        db.commit()
        
        return {"success": True, "message": "Usuario desactivado exitosamente"}
        
    except Exception as e:
        logger.error(f"Error eliminando usuario: {e}")
        db.rollback()
        return {"success": False, "message": f"Error: {str(e)}"}

@app.put("/api/admin/users/{user_id}")
async def update_user(user_id: int, user_data: dict, db: Session = Depends(get_db)):
    """Actualiza un usuario"""
    try:
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not usuario:
            return {"success": False, "message": "Usuario no encontrado"}
        
        # Actualizar campos
        if 'name' in user_data:
            usuario.nombre_completo = user_data['name']
        if 'email' in user_data:
            usuario.email = user_data['email']
        if 'career' in user_data:
            usuario.carrera_id = user_data['career']
        
        db.commit()
        
        return {"success": True, "message": "Usuario actualizado exitosamente"}
        
    except Exception as e:
        logger.error(f"Error actualizando usuario: {e}")
        db.rollback()
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/api/health")
async def health_check():
    """Estado del sistema con estadísticas"""
    db = SessionLocal()
    try:
        db.execute("SELECT 1")
        total_users = db.query(Usuario).count()
        total_students = db.query(Usuario).filter(Usuario.rol == "student").count()
        total_teachers = db.query(Usuario).filter(Usuario.rol == "teacher").count()
        
        global server_stats
        uptime = time_module.time() - server_stats["start_time"] if server_stats["start_time"] else 0
        
        return {
            "status": "ok",
            "message": "Servidor TESJI funcionando correctamente",
            "version": "1.0.0",
            "timestamp": time_module.time(),
            "uptime_seconds": uptime,
            "database": {
                "status": "ok",
                "total_users": total_users,
                "students": total_students,
                "teachers": total_teachers
            },
            "statistics": {
                "rfid_requests": server_stats["rfid_requests"],
                "successful_recognitions": server_stats["successful_recognitions"],
                "failed_recognitions": server_stats["failed_recognitions"],
                "new_registrations": server_stats["new_registrations"],
            },
            "endpoints": {
                "rfid_main": "/api/rfid",
                "rfid_bridge": "/api/rfid/bridge",
                "rfid_last": "/api/rfid/last",
                "register_student": "/api/register-student",
                "teacher_register": "/api/teacher/register",
                "teacher_login": "/api/teacher/login",
                "admin_login": "/api/admin/login"
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

# PÁGINA PRINCIPAL RESTAURADA
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TESJI - Sistema RFID Completo</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                min-height: 100vh; 
                color: white; 
                display: flex; 
                align-items: center; 
                justify-content: center;
            }
            .container { 
                max-width: 700px; 
                text-align: center; 
                padding: 40px 30px; 
                background: rgba(255,255,255,0.1); 
                border-radius: 20px; 
                backdrop-filter: blur(10px); 
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            h1 { 
                font-size: 3.5em; 
                margin-bottom: 10px; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3); 
            }
            .subtitle { 
                font-size: 1.2em; 
                margin-bottom: 40px; 
                opacity: 0.9; 
            }
            
            .security-warning {
                background: rgba(255, 193, 7, 0.2);
                border: 2px solid #ffc107;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                color: #ffc107;
            }
            .security-warning h3 {
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .rfid-detector {
                background: rgba(255,255,255,0.15);
                padding: 30px;
                border-radius: 15px;
                margin: 30px 0;
                border: 2px solid rgba(76, 175, 80, 0.5);
                position: relative;
            }
            .rfid-status {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
                margin-bottom: 20px;
            }
            .rfid-icon {
                font-size: 2.5em;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { opacity: 0.6; }
                50% { opacity: 1; }
                100% { opacity: 0.6; }
            }
            .status-text {
                font-size: 1.1em;
                font-weight: 600;
            }
            
            .user-detected {
                background: rgba(76, 175, 80, 0.2);
                border: 2px solid #4CAF50;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                display: none;
            }
            .user-info {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 20px;
                margin: 15px 0;
            }
            .user-avatar {
                width: 60px;
                height: 60px;
                background: #4CAF50;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5em;
            }
            
            .manual-access {
                background: rgba(255,255,255,0.1);
                padding: 25px;
                border-radius: 15px;
                margin: 30px 0;
            }
            .access-links {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .access-link {
                display: block;
                padding: 15px 20px;
                background: rgba(255,255,255,0.1);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                transition: all 0.3s ease;
                border: 1px solid rgba(255,255,255,0.2);
            }
            .access-link:hover {
                background: rgba(255,255,255,0.2);
                transform: translateY(-2px);
            }
            .access-icon {
                font-size: 1.8em;
                display: block;
                margin-bottom: 8px;
            }
            .access-title {
                font-weight: 600;
                margin-bottom: 5px;
            }
            .access-desc {
                font-size: 0.9em;
                opacity: 0.8;
            }
            
            .test-section {
                margin-top: 20px;
                padding: 15px;
                background: rgba(0,0,0,0.2);
                border-radius: 10px;
            }
            .test-btn {
                margin: 5px;
                padding: 8px 15px;
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 5px;
                color: white;
                cursor: pointer;
                font-size: 0.9em;
            }
            .test-btn:hover {
                background: rgba(255,255,255,0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 TESJI</h1>
            <p class="subtitle">Sistema de Control de Asistencias con RFID - Versión Final</p>
            
            <div class="security-warning">
                <h3>⚠️ Advertencia de Seguridad</h3>
                <p>Este sistema está ejecutándose en HTTP (no seguro). Para uso en producción, configure HTTPS para proteger las credenciales de usuario.</p>
            </div>
            
            <div class="rfid-detector">
                <div class="rfid-status">
                    <i class="rfid-icon" id="rfidIcon">📡</i>
                    <div class="status-text" id="statusText">Esperando tarjeta RFID...</div>
                </div>
                <p style="opacity: 0.8; margin-bottom: 15px;">
                    Acerca tu tarjeta RFID para pasar lista automáticamente
                </p>
                
                <div id="userDetected" class="user-detected">
                    <div class="user-info">
                        <div class="user-avatar">👨‍🎓</div>
                        <div>
                            <h3 id="userName">Nombre del Usuario</h3>
                            <p id="userDetails">Detalles del usuario</p>
                        </div>
                    </div>
                    <div id="attendanceMessage" style="margin-top: 15px; font-weight: 600;"></div>
                </div>
                
                <div class="test-section">
                    <p style="margin-bottom: 10px; font-size: 0.9em;">🧪 Pruebas (Solo para testing):</p>
                    <button class="test-btn" onclick="simulateRFID('TEST001')">Estudiante Grupo 3402</button>
                    <button class="test-btn" onclick="simulateRFID('TEST002')">Estudiante Grupo 3401</button>
                    <button class="test-btn" onclick="simulateRFID('PROF001')">Maestro</button>
                </div>
            </div>
            
            <div class="manual-access">
                <h3>🔗 Acceso Manual</h3>
                <p style="opacity: 0.8; margin-bottom: 15px;">Acceso directo a las diferentes secciones del sistema</p>
                
                <div class="access-links">
                    <a href="/welcome.html" class="access-link">
                        <span class="access-icon">🎫</span>
                        <div class="access-title">Lector RFID</div>
                        <div class="access-desc">Página completa de RFID</div>
                    </a>
                    
                    <a href="/login-teacher.html" class="access-link">
                        <span class="access-icon">👨‍🏫</span>
                        <div class="access-title">Acceso Maestros</div>
                        <div class="access-desc">Panel para maestros</div>
                    </a>
                    
                    <a href="/admin.html" class="access-link">
                        <span class="access-icon">👨‍💼</span>
                        <div class="access-title">Acceso Admin</div>
                        <div class="access-desc">Panel de administración</div>
                    </a>
                </div>
            </div>
        </div>
        
        <script>
            let lastProcessedUID = null;
            let pollInterval = null;
            
            const statusText = document.getElementById('statusText');
            const rfidIcon = document.getElementById('rfidIcon');
            const userDetected = document.getElementById('userDetected');
            const userName = document.getElementById('userName');
            const userDetails = document.getElementById('userDetails');
            const attendanceMessage = document.getElementById('attendanceMessage');
            
            function startPolling() {
                if (pollInterval) clearInterval(pollInterval);
                pollInterval = setInterval(checkRFIDStatus, 1000);
                console.log('🔄 Polling RFID iniciado');
            }
            
            async function checkRFIDStatus() {
                try {
                    const response = await fetch('/api/rfid/last', {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                            'Cache-Control': 'no-cache'
                        }
                    });
                    
                    if (!response.ok) return;
                    
                    const data = await response.json();
                    
                    if (data && data.uid && data.uid !== lastProcessedUID) {
                        console.log('🆕 Nuevo UID detectado:', data.uid);
                        lastProcessedUID = data.uid;
                        handleRFIDDetected(data);
                    }
                } catch (error) {
                    console.error('❌ Error consultando RFID:', error);
                }
            }
            
            function handleRFIDDetected(data) {
                console.log('🎫 RFID procesado:', data);
                
                if (data.exists === true && data.user) {
                    updateStatus('success', '✅ Usuario Detectado');
                    
                    userName.textContent = data.user.nombre;
                    userDetails.textContent = data.user.matricula + ' - ' + data.user.rol + ' - Salón: ' + (data.user.salon || 'N/A');
                    
                    if (data.user.rol === 'student') {
                        if (data.attendance_registered) {
                            attendanceMessage.textContent = '✅ Asistencia registrada exitosamente';
                            attendanceMessage.style.color = '#4CAF50';
                        } else {
                            attendanceMessage.textContent = 'ℹ️ Asistencia ya registrada hoy';
                            attendanceMessage.style.color = '#FF9800';
                        }
                        
                        setTimeout(() => {
                          const studentUrl = '/student.html?uid=' + encodeURIComponent(data.uid) + '&name=' + encodeURIComponent(data.user.nombre) + '&matricula=' + encodeURIComponent(data.user.matricula) + '&salon=' + encodeURIComponent(data.user.salon || 'N1');
                          console.log('🔗 Redirigiendo a:', studentUrl);
                          window.location.href = studentUrl;
                        }, 3000);
                    } else {
                        attendanceMessage.textContent = '👋 Bienvenido ' + data.user.rol;
                        attendanceMessage.style.color = '#2196F3';
                        
                        setTimeout(() => {
                            if (data.user.rol === 'teacher') {
                                window.location.href = '/teacher.html';
                            }
                        }, 2000);
                    }
                    
                    userDetected.style.display = 'block';
                    
                    if (data.user.rol !== 'student') {
                        setTimeout(() => {
                            userDetected.style.display = 'none';
                            resetStatus();
                        }, 5000);
                    }
                    
                } else if (data.exists === false) {
                    updateStatus('warning', '🆕 Usuario Nuevo Detectado');
                    setTimeout(() => {
                        window.location.href = '/welcome.html';
                    }, 1500);
                }
            }
            
            async function simulateRFID(uid) {
                console.log('🧪 Simulando RFID:', uid);
                updateStatus('info', '🔄 Procesando...');
                
                try {
                    const response = await fetch('/api/rfid', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ tag: uid })
                    });
                    
                    const data = await response.json();
                    console.log('✅ Respuesta simulación:', data);
                    
                    handleRFIDDetected(data);
                    
                } catch (error) {
                    console.error('❌ Error simulando RFID:', error);
                    updateStatus('error', '❌ Error de conexión');
                }
            }
            
            function updateStatus(type, message) {
                statusText.textContent = message;
                
                const icons = {
                    waiting: '📡',
                    success: '✅',
                    error: '❌',
                    warning: '⚠️',
                    info: '🔄'
                };
                
                rfidIcon.textContent = icons[type] || '📡';
            }
            
            function resetStatus() {
                updateStatus('waiting', 'Esperando tarjeta RFID...');
                userDetected.style.display = 'none';
            }
            
            document.addEventListener('DOMContentLoaded', function() {
                console.log('🚀 Sistema TESJI iniciado');
                startPolling();
                resetStatus();
            });
            
            window.addEventListener('beforeunload', function() {
                if (pollInterval) {
                    clearInterval(pollInterval);
                }
            });
        </script>
    </body>
    </html>
    """)

# Función principal para iniciar el servidor
def main():
    """Función principal para iniciar el servidor"""
    global server_stats
    server_stats["start_time"] = time_module.time()
    
    # Obtener puerto de la variable de entorno (Render lo asigna automáticamente)
    port = int(os.environ.get("PORT", 8001))
    
    # Obtener información de red
    network_info = get_network_info()
    
    # Iniciar monitor de red solo en desarrollo local
    if os.environ.get("RENDER") != "true":
        network_monitor.start_monitoring()
    
    # Mostrar información de inicio
    logger.info("=" * 80)
    logger.info("🎓 SISTEMA TESJI - SERVIDOR UNIFICADO INICIANDO")
    logger.info("=" * 80)
    logger.info(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🌐 Red: {network_info['network_name']}")
    logger.info(f"🔗 IP Principal: {network_info['primary_ip']}")
    logger.info(f"🚀 Puerto: {port}")
    logger.info("")
    logger.info("🔗 URLs de acceso:")
    logger.info(f"   - Local:    http://127.0.0.1:{port}")
    logger.info(f"   - Red:      http://{network_info['primary_ip']}:{port}")
    logger.info("")
    logger.info("📱 Páginas disponibles:")
    logger.info("   - Principal:     /")
    logger.info("   - RFID:          /welcome.html")
    logger.info("   - Estudiantes:   /student.html")
    logger.info("   - Maestros:      /login-teacher.html")
    logger.info("   - Admin:         /admin.html")
    logger.info("")
    logger.info("🔌 Endpoints principales:")
    logger.info("   - RFID:          POST /api/rfid")
    logger.info("   - Registro:      POST /api/register-student")
    logger.info("   - Login Admin:   POST /api/admin/login")
    logger.info("   - Login Maestro: POST /api/teacher/login")
    logger.info("   - Salud:         GET /api/health")
    logger.info("=" * 80)
    
    try:
        # Configurar uvicorn para producción
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            reload=False
        )
        
        server = uvicorn.Server(config)
        server.run()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error iniciando servidor: {e}")
    finally:
        # Limpiar recursos
        if os.environ.get("RENDER") != "true":
            network_monitor.stop_monitoring()
        logger.info("🧹 Recursos liberados")
        logger.info("👋 ¡Hasta luego!")

if __name__ == "__main__":
    main()
