// Cliente WebSocket para múltiples dispositivos
class MultiDeviceClient {
  constructor() {
    this.ws = null
    this.clientId = this.generateClientId()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.isConnected = false
    this.eventHandlers = {}

    this.connect()
    this.setupHeartbeat()
  }

  generateClientId() {
    const timestamp = Date.now()
    const random = Math.random().toString(36).substr(2, 9)
    const deviceInfo = this.getDeviceInfo()
    return `${deviceInfo.type}_${timestamp}_${random}`
  }

  getDeviceInfo() {
    const userAgent = navigator.userAgent
    let deviceType = "desktop"

    if (/Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent)) {
      deviceType = "mobile"
    } else if (/iPad/i.test(userAgent)) {
      deviceType = "tablet"
    }

    return {
      type: deviceType,
      userAgent: userAgent,
      screen: {
        width: screen.width,
        height: screen.height,
      },
      timestamp: new Date().toISOString(),
    }
  }

  connect() {
    try {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:"
      const host = window.location.host
      const wsUrl = `${protocol}//${host}/ws/${this.clientId}`

      console.log(`🔌 Conectando WebSocket: ${wsUrl}`)

      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log("✅ WebSocket conectado")
        this.isConnected = true
        this.reconnectAttempts = 0
        this.onConnect()
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleMessage(data)
        } catch (error) {
          console.error("Error procesando mensaje:", error)
        }
      }

      this.ws.onclose = () => {
        console.log("🔌 WebSocket desconectado")
        this.isConnected = false
        this.onDisconnect()
        this.attemptReconnect()
      }

      this.ws.onerror = (error) => {
        console.error("❌ Error WebSocket:", error)
      }
    } catch (error) {
      console.error("Error creando WebSocket:", error)
      this.attemptReconnect()
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)

      console.log(`🔄 Reintentando conexión en ${delay}ms (intento ${this.reconnectAttempts})`)

      setTimeout(() => {
        this.connect()
      }, delay)
    } else {
      console.error("❌ Máximo número de reintentos alcanzado")
      this.showConnectionError()
    }
  }

  handleMessage(data) {
    console.log("📨 Mensaje recibido:", data)

    switch (data.type) {
      case "pong":
        // Respuesta al ping
        break

      case "rfid_event":
        this.emit("rfid_detected", data.data)
        break

      case "attendance_update":
        this.emit("attendance_updated", data.data)
        break

      default:
        console.log("Mensaje no reconocido:", data)
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
      return true
    } else {
      console.warn("WebSocket no está conectado")
      return false
    }
  }

  setupHeartbeat() {
    setInterval(() => {
      if (this.isConnected) {
        this.send({
          type: "ping",
          timestamp: Date.now(),
        })
      }
    }, 30000) // Ping cada 30 segundos
  }

  // Sistema de eventos
  on(event, handler) {
    if (!this.eventHandlers[event]) {
      this.eventHandlers[event] = []
    }
    this.eventHandlers[event].push(handler)
  }

  emit(event, data) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].forEach((handler) => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error en handler de evento ${event}:`, error)
        }
      })
    }
  }

  onConnect() {
    this.showConnectionStatus("Conectado", "success")
    this.emit("connected")
  }

  onDisconnect() {
    this.showConnectionStatus("Desconectado", "error")
    this.emit("disconnected")
  }

  showConnectionStatus(message, type) {
    // Crear o actualizar indicador de estado
    let indicator = document.getElementById("connection-indicator")
    if (!indicator) {
      indicator = document.createElement("div")
      indicator.id = "connection-indicator"
      indicator.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                padding: 8px 12px;
                border-radius: 4px;
                color: white;
                font-size: 12px;
                z-index: 10000;
                transition: all 0.3s ease;
            `
      document.body.appendChild(indicator)
    }

    indicator.textContent = `🌐 ${message}`
    indicator.className = `connection-${type}`

    if (type === "success") {
      indicator.style.backgroundColor = "#4CAF50"
    } else if (type === "error") {
      indicator.style.backgroundColor = "#f44336"
    } else {
      indicator.style.backgroundColor = "#FF9800"
    }

    // Auto-ocultar después de 3 segundos si es éxito
    if (type === "success") {
      setTimeout(() => {
        if (indicator) {
          indicator.style.opacity = "0.3"
        }
      }, 3000)
    }
  }

  showConnectionError() {
    const errorDiv = document.createElement("div")
    errorDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #f44336;
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            z-index: 10001;
        `
    errorDiv.innerHTML = `
            <h3>❌ Error de Conexión</h3>
            <p>No se pudo conectar al servidor</p>
            <button onclick="location.reload()" style="
                background: white;
                color: #f44336;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 10px;
            ">Recargar Página</button>
        `
    document.body.appendChild(errorDiv)
  }
}

// Instancia global
let multiDeviceClient

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", () => {
  multiDeviceClient = new MultiDeviceClient()

  // Configurar eventos RFID
  multiDeviceClient.on("rfid_detected", (data) => {
    console.log("🎫 RFID detectado desde otro dispositivo:", data)
    // Actualizar UI si es necesario
    const handleRFIDDetected = window.handleRFIDDetected // Declare or import handleRFIDDetected here
    if (typeof handleRFIDDetected === "function") {
      handleRFIDDetected(data)
    }
  })

  // Configurar eventos de asistencia
  multiDeviceClient.on("attendance_updated", (data) => {
    console.log("📝 Asistencia actualizada:", data)
    // Actualizar UI si es necesario
    const updateAttendanceUI = window.updateAttendanceUI // Declare or import updateAttendanceUI here
    if (typeof updateAttendanceUI === "function") {
      updateAttendanceUI(data)
    }
  })
})

// Función para enviar eventos RFID
function broadcastRFIDEvent(rfidData) {
  if (multiDeviceClient) {
    multiDeviceClient.send({
      type: "rfid_scan",
      data: rfidData,
      timestamp: Date.now(),
    })
  }
}

// Hacer disponible globalmente
window.multiDeviceClient = multiDeviceClient
window.broadcastRFIDEvent = broadcastRFIDEvent
