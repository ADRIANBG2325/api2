#!/usr/bin/env python3
"""
Servidor TESJI Optimizado para Múltiples Dispositivos
"""

import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import time
from network_config import network_manager

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.device_info: Dict[str, dict] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.device_info[client_id] = {
            'websocket': websocket,
            'connected_at': time.time(),
            'last_activity': time.time()
        }
        print(f"📱 Dispositivo conectado: {client_id}")
        
    def disconnect(self, websocket: WebSocket, client_id: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if client_id in self.device_info:
            del self.device_info[client_id]
        print(f"📱 Dispositivo desconectado: {client_id}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            pass
            
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Limpiar conexiones muertas
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)
    
    async def broadcast_rfid_event(self, rfid_data: dict):
        """Envía eventos RFID a todos los dispositivos conectados"""
        message = json.dumps({
            'type': 'rfid_event',
            'data': rfid_data,
            'timestamp': time.time()
        })
        await self.broadcast(message)
    
    async def broadcast_attendance_update(self, attendance_data: dict):
        """Envía actualizaciones de asistencia a todos los dispositivos"""
        message = json.dumps({
            'type': 'attendance_update',
            'data': attendance_data,
            'timestamp': time.time()
        })
        await self.broadcast(message)
    
    def get_connected_devices(self):
        """Obtiene información de dispositivos conectados"""
        devices = []
        current_time = time.time()
        
        for client_id, info in self.device_info.items():
            devices.append({
                'client_id': client_id,
                'connected_at': info['connected_at'],
                'last_activity': info['last_activity'],
                'duration': current_time - info['connected_at']
            })
        
        return devices

# Instancia global del manager de conexiones
connection_manager = ConnectionManager()

# Función para integrar con el servidor principal
def setup_websocket_routes(app: FastAPI):
    """Configura las rutas WebSocket en el servidor principal"""
    
    @app.websocket("/ws/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: str):
        await connection_manager.connect(websocket, client_id)
        try:
            while True:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Actualizar última actividad
                if client_id in connection_manager.device_info:
                    connection_manager.device_info[client_id]['last_activity'] = time.time()
                
                # Procesar diferentes tipos de mensajes
                if message_data.get('type') == 'ping':
                    await connection_manager.send_personal_message(
                        json.dumps({'type': 'pong', 'timestamp': time.time()}),
                        websocket
                    )
                elif message_data.get('type') == 'rfid_scan':
                    # Reenviar evento RFID a todos los dispositivos
                    await connection_manager.broadcast_rfid_event(message_data.get('data', {}))
                
        except WebSocketDisconnect:
            connection_manager.disconnect(websocket, client_id)
    
    @app.get("/api/connected-devices")
    async def get_connected_devices():
        """Obtiene lista de dispositivos conectados"""
        devices = connection_manager.get_connected_devices()
        return {
            'success': True,
            'total_devices': len(devices),
            'devices': devices,
            'network_info': network_manager.get_network_info()
        }

# Función para enviar eventos desde el servidor principal
async def notify_rfid_event(rfid_data: dict):
    """Notifica evento RFID a todos los dispositivos conectados"""
    await connection_manager.broadcast_rfid_event(rfid_data)

async def notify_attendance_update(attendance_data: dict):
    """Notifica actualización de asistencia a todos los dispositivos"""
    await connection_manager.broadcast_attendance_update(attendance_data)
