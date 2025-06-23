#!/usr/bin/env python3
"""
Servidor Unificado TESJI - Sistema Completo CORREGIDO
Versión Final - FastAPI configurado correctamente
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
import threading
import subprocess
import platform

# Configurar logging profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
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

# Horario temporal para Salón N2
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

# Función simplificada para obtener IP
def get_best_ip():
    """Obtiene la mejor IP disponible para el servidor"""
    try:
        import netifaces
        interfaces = []
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if ip != '127.0.0.1' and not ip.startswith('169.254'):
                        return ip
    except ImportError:
        pass
    
    return "0.0.0.0"

def get_network_info():
    """Obtiene información básica de la red"""
    return {
        'primary_ip': get_best_ip(),
        'interfaces': [],
        'network_name': "Render Cloud",
        'total_interfaces': 1
    }

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

def assign_group_by_matricula(matricula: str, db: Session) -> tuple:
    """Asigna grupo y salón automáticamente"""
    try:
        logger.info(f"🔍 Verificando matrícula: {matricula}")
        
        if matricula in GRUPO_3402_MATRICULAS:
            grupo = db.query(Grupo).filter(Grupo.nombre.like("%3402%")).first()
            if not grupo:
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
            grupo = db.query(Grupo).filter(Grupo.nombre.like("%3401%")).first()
            if not grupo:
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
        
        # Fallback
        grupo = db.query(Grupo).filter(Grupo.activo == True).first()
        if grupo:
            salon = grupo.salon or "N1"
            logger.info(f"⚠️ Matrícula {matricula} asignada al primer grupo disponible")
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

# ==================== SERVIR ARCHIVOS ESTÁTICOS CORRECTAMENTE ====================

# Montar archivos estáticos ANTES de las rutas
try:
    # Verificar que los directorios existen
    static_dir = "static"
    templates_dir = "templates"
    
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        logger.info(f"✅ Archivos estáticos montados desde /{static_dir}")
    else:
        logger.warning(f"⚠️ Directorio /{static_dir} no encontrado")
        
    # NO montar templates como estáticos, solo servir archivos específicos
    
except Exception as e:
    logger.error(f"❌ Error montando archivos estáticos: {e}")

# ==================== FUNCIONES PARA SERVIR HTML ====================

# ==================== RUTAS PARA PÁGINAS HTML ====================

def get_file_path(filename: str) -> str:
    """Obtiene la ruta completa del archivo"""
    # Intentar en templates/ primero
    template_path = os.path.join(os.getcwd(), "templates", filename)
    if os.path.exists(template_path):
        logger.info(f"✅ Archivo encontrado: {template_path}")
        return template_path
    
    # Intentar en la raíz
    root_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(root_path):
        logger.info(f"✅ Archivo encontrado: {root_path}")
        return root_path
    
    logger.error(f"❌ Archivo no encontrado: {filename}")
    return None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Página principal del sistema"""
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
            .status-info {
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                font-size: 0.9em;
            }
            .debug-info {
                background: rgba(0,0,0,0.2);
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
                font-size: 0.8em;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 TESJI</h1>
            <p class="subtitle">Sistema de Control de Asistencias con RFID</p>
            
            <div class="status-info">
                <p>✅ Sistema desplegado en Render</p>
                <p>🌐 Acceso desde cualquier dispositivo</p>
                <p>🔒 HTTPS habilitado automáticamente</p>
            </div>
            
            <div class="debug-info">
                <p><strong>Debug Info:</strong></p>
                <p>📁 Directorio actual: """ + os.getcwd() + """</p>
                <p>📂 Templates existe: """ + str(os.path.exists("templates")) + """</p>
                <p>📂 Static existe: """ + str(os.path.exists("static")) + """</p>
                <p>📄 welcome.html: """ + str(os.path.exists("templates/welcome.html")) + """</p>
                <p>📄 admin.html: """ + str(os.path.exists("templates/admin.html")) + """</p>
            </div>
            
            <div class="access-links">
                <a href="/welcome.html" class="access-link">
                    <span class="access-icon">🎫</span>
                    <div class="access-title">Lector RFID</div>
                    <div class="access-desc">Registro de asistencias</div>
                </a>
                
                <a href="/login-teacher.html" class="access-link">
                    <span class="access-icon">👨‍🏫</span>
                    <div class="access-title">Maestros</div>
                    <div class="access-desc">Panel de profesores</div>
                </a>
                
                <a href="/admin.html" class="access-link">
                    <span class="access-icon">👨‍💼</span>
                    <div class="access-title">Administración</div>
                    <div class="access-desc">Panel administrativo</div>
                </a>
                
                <a href="/student.html" class="access-link">
                    <span class="access-icon">👨‍🎓</span>
                    <div class="access-title">Estudiantes</div>
                    <div class="access-desc">Panel de estudiantes</div>
                </a>
                
                <a href="/api/health" class="access-link">
                    <span class="access-icon">🔧</span>
                    <div class="access-title">Estado del Sistema</div>
                    <div class="access-desc">Diagnósticos y salud</div>
                </a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/welcome.html")
async def serve_welcome():
    """Página de bienvenida con lector RFID"""
    logger.info("🔍 Solicitando welcome.html")
    file_path = get_file_path("welcome.html")
    if file_path:
        return FileResponse(file_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <h1>Error: welcome.html no encontrado</h1>
        <p>Directorio actual: """ + os.getcwd() + """</p>
        <p>Archivos en templates/: """ + str(os.listdir("templates") if os.path.exists("templates") else "No existe") + """</p>
        <a href="/">← Volver</a>
        """, status_code=404)

@app.get("/admin.html")
async def serve_admin():
    """Panel de administración"""
    logger.info("🔍 Solicitando admin.html")
    file_path = get_file_path("admin.html")
    if file_path:
        return FileResponse(file_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <h1>Error: admin.html no encontrado</h1>
        <p>Directorio actual: """ + os.getcwd() + """</p>
        <p>Archivos en templates/: """ + str(os.listdir("templates") if os.path.exists("templates") else "No existe") + """</p>
        <a href="/">← Volver</a>
        """, status_code=404)

@app.get("/teacher.html")
async def serve_teacher():
    """Panel de maestros"""
    logger.info("🔍 Solicitando teacher.html")
    file_path = get_file_path("enhanced-teacher.html")
    if file_path:
        return FileResponse(file_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <h1>Error: enhanced-teacher.html no encontrado</h1>
        <p>Directorio actual: """ + os.getcwd() + """</p>
        <p>Archivos en templates/: """ + str(os.listdir("templates") if os.path.exists("templates") else "No existe") + """</p>
        <a href="/">← Volver</a>
        """, status_code=404)

@app.get("/student.html")
async def serve_student():
    """Panel de estudiantes"""
    logger.info("🔍 Solicitando student.html")
    file_path = get_file_path("student.html")
    if file_path:
        return FileResponse(file_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <h1>Error: student.html no encontrado</h1>
        <p>Directorio actual: """ + os.getcwd() + """</p>
        <p>Archivos en templates/: """ + str(os.listdir("templates") if os.path.exists("templates") else "No existe") + """</p>
        <a href="/">← Volver</a>
        """, status_code=404)

@app.get("/login-teacher.html")
async def serve_teacher_login():
    """Página de login para maestros"""
    logger.info("🔍 Solicitando login-teacher.html")
    file_path = get_file_path("login-teacher.html")
    if file_path:
        return FileResponse(file_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <h1>Error: login-teacher.html no encontrado</h1>
        <p>Directorio actual: """ + os.getcwd() + """</p>
        <p>Archivos en templates/: """ + str(os.listdir("templates") if os.path.exists("templates") else "No existe") + """</p>
        <a href="/">← Volver</a>
        """, status_code=404)

@app.get("/enhanced-teacher.html")
async def serve_enhanced_teacher():
    """Panel de maestros mejorado"""
    logger.info("🔍 Solicitando enhanced-teacher.html")
    file_path = get_file_path("enhanced-teacher.html")
    if file_path:
        return FileResponse(file_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <h1>Error: enhanced-teacher.html no encontrado</h1>
        <p>Directorio actual: """ + os.getcwd() + """</p>
        <p>Archivos en templates/: """ + str(os.listdir("templates") if os.path.exists("templates") else "No existe") + """</p>
        <a href="/">← Volver</a>
        """, status_code=404)

@app.get("/enhanced-welcome.html")
async def serve_enhanced_welcome():
    """Página de bienvenida mejorada"""
    logger.info("🔍 Solicitando enhanced-welcome.html")
    file_path = get_file_path("enhanced-welcome.html")
    if file_path:
        return FileResponse(file_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <h1>Error: enhanced-welcome.html no encontrado</h1>
        <p>Directorio actual: """ + os.getcwd() + """</p>
        <p>Archivos en templates/: """ + str(os.listdir("templates") if os.path.exists("templates") else "No existe") + """</p>
        <a href="/">← Volver</a>
        """, status_code=404)

@app.get("/device-selector.html")
async def serve_device_selector():
    """Selector de dispositivos"""
    logger.info("🔍 Solicitando device-selector.html")
    file_path = get_file_path("device-selector.html")
    if file_path:
        return FileResponse(file_path, media_type="text/html")
    else:
        return HTMLResponse("""
        <h1>Error: device-selector.html no encontrado</h1>
        <p>Directorio actual: """ + os.getcwd() + """</p>
        <p>Archivos en templates/: """ + str(os.listdir("templates") if os.path.exists("templates") else "No existe") + """</p>
        <a href="/">← Volver</a>
        """, status_code=404)

# ==================== MIDDLEWARE ====================

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
        
        # Buscar usuario en base de datos
        usuario = db.query(Usuario).filter(Usuario.uid == tag_data.tag).first()
        
        if usuario:
            logger.info(f"✅ Usuario encontrado: {usuario.nombre_completo} ({usuario.matricula}) - {usuario.rol}")
            
            if usuario.rol == "student":
                # Registrar asistencia para estudiante
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
                    mensaje = f"Bienvenido {usuario.nombre_completo}. Asistencia registrada."
                else:
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
        active_rfid_sessions[tag_data.tag] = {
            "uid": tag_data.tag,
            "timestamp": time_module.time(),
            "data": response_data
        }

        # Limpiar sesiones expiradas
        current_time = time_module.time()
        expired_sessions = [uid for uid, session in active_rfid_sessions.items() 
                           if current_time - session["timestamp"] > 300]
        for uid in expired_sessions:
            del active_rfid_sessions[uid]
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ ERROR procesando RFID: {e}")
        
        return {
            "type": "error",
            "success": False,
            "message": f"Error interno del servidor: {str(e)}",
            "uid": tag_data.tag,
            "timestamp": time_module.time()
        }

@app.get("/api/rfid/last")
async def get_last_rfid():
    """Obtiene el último UID RFID procesado"""
    global active_rfid_sessions
    
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
            return latest_session["data"]
    
    return {"uid": None, "timestamp": None, "message": "No hay datos RFID recientes"}

@app.post("/api/register-student")
async def register_student(student_data: StudentRegistration, request: Request, db: Session = Depends(get_db)):
    """Registra un nuevo estudiante"""
    global server_stats
    
    try:
        logger.info(f"📝 REGISTRO DE ESTUDIANTE: {student_data.matricula}")
        
        # Verificar duplicados
        if db.query(Usuario).filter(Usuario.uid == student_data.uid).first():
            raise HTTPException(status_code=400, detail="Este UID ya está registrado")
        
        if db.query(Usuario).filter(Usuario.matricula == student_data.matricula).first():
            raise HTTPException(status_code=400, detail="Esta matrícula ya está registrada")
        
        if db.query(Usuario).filter(Usuario.email == student_data.email).first():
            raise HTTPException(status_code=400, detail="Este email ya está registrado")
        
        # Asignar grupo y salón automáticamente
        grupo_id, salon = assign_group_by_matricula(student_data.matricula, db)
        
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
                "salon": nuevo_usuario.salon
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error registrando estudiante: {e}")
        db.rollback()
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/api/student/schedule")
async def get_student_schedule(uid: str = None, db: Session = Depends(get_db)):
    """Obtiene el horario del estudiante por UID"""
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
            return {"success": False, "message": "Estudiante no encontrado"}
        
        # Obtener horario según el salón asignado
        salon = student.salon or "N1"
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
        
        return {
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
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo horario del estudiante: {e}")
        return {"success": False, "message": f"Error interno: {str(e)}"}

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
            "files": {
                "static_exists": os.path.exists("static"),
                "templates_exists": os.path.exists("templates"),
                "welcome_html": os.path.exists("templates/welcome.html"),
                "admin_html": os.path.exists("templates/admin.html"),
                "student_html": os.path.exists("templates/student.html"),
                "teacher_html": os.path.exists("templates/enhanced-teacher.html"),
                "login_teacher_html": os.path.exists("templates/login-teacher.html"),
            },
            "endpoints": {
                "rfid_main": "/api/rfid",
                "rfid_last": "/api/rfid/last",
                "register_student": "/api/register-student",
                "student_schedule": "/api/student/schedule",
                "health": "/api/health"
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal para iniciar el servidor"""
    global server_stats
    server_stats["start_time"] = time_module.time()
    
    # Obtener puerto de la variable de entorno (Render lo asigna automáticamente)
    port = int(os.environ.get("PORT", 8001))
    
    # Mostrar información de inicio
    logger.info("=" * 80)
    logger.info("🎓 SISTEMA TESJI - SERVIDOR UNIFICADO INICIANDO")
    logger.info("=" * 80)
    logger.info(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🚀 Puerto: {port}")
    logger.info(f"🌐 Entorno: {'Render Cloud' if os.environ.get('RENDER') else 'Local'}")
    logger.info("")
    logger.info("📁 Verificando archivos:")
    logger.info(f"   - static/: {'✅' if os.path.exists('static') else '❌'}")
    logger.info(f"   - templates/: {'✅' if os.path.exists('templates') else '❌'}")
    logger.info("")
    logger.info("📱 Páginas disponibles:")
    logger.info("   - Principal:     /")
    logger.info("   - RFID:          /welcome.html")
    logger.info("   - Estudiantes:   /student.html")
    logger.info("   - Maestros:      /login-teacher.html")
    logger.info("   - Admin:         /admin.html")
    logger.info("   - Salud:         /api/health")
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
        logger.info("🧹 Recursos liberados")
        logger.info("👋 ¡Hasta luego!")

if __name__ == "__main__":
    main()

