// Variables globales

let currentUID = null

let lastProcessedUID = null

let pollInterval = null



// Elementos DOM - VERIFICACIÓN ROBUSTA

const elements = {}



// Función para inicializar elementos DOM

function initializeElements() {

  const elementIds = [

    "statusCard",

    "statusIcon",

    "statusTitle",

    "statusMessage",

    "userDetected",

    "registrationForm",

    "studentForm",

    "userName",

    "userDetails",

    "uid",

    "cancelBtn",

  ]



  console.log("🔍 Inicializando elementos DOM...")



  elementIds.forEach((id) => {

    elements[id] = document.getElementById(id)

    if (elements[id]) {

      console.log(`✅ ${id}: encontrado`)

    } else {

      console.error(`❌ ${id}: NO encontrado`)

    }

  })



  return elementIds.every((id) => elements[id] !== null)

}



// Función para consultar el estado RFID (polling)

async function checkRFIDStatus() {

  try {

    const response = await fetch("/api/rfid/last", {

      method: "GET",

      headers: {

        "Content-Type": "application/json",

        "Cache-Control": "no-cache",

      },

    })



    if (!response.ok) {

      throw new Error(`HTTP ${response.status}: ${response.statusText}`)

    }



    const data = await response.json()



    // Solo procesar si hay datos válidos y diferentes

    if (data && data.uid && data.uid !== lastProcessedUID) {

      console.log(`🆕 Nuevo UID detectado: ${data.uid}`)

      console.log(`📊 Datos completos:`, data)



      lastProcessedUID = data.uid

      handleRFIDDetected(data)

    }

  } catch (error) {

    console.error("❌ Error consultando estado RFID:", error)

  }

}



// Función MEJORADA para manejar RFID detectado

function handleRFIDDetected(data) {

  console.log("=" * 50)

  console.log("🎫 PROCESANDO RFID DETECTADO")

  console.log("=" * 50)

  console.log("📋 Datos recibidos:", data)

  console.log("🔍 UID:", data.uid)

  console.log("🔍 Existe:", data.exists)

  console.log("🔍 Éxito:", data.success)

  console.log("🔍 Mensaje:", data.message)



  if (data.user) {

    console.log("👤 Datos del usuario:", data.user)

  }



  currentUID = data.uid



  // Ocultar todas las secciones primero

  hideAllSections()



  // DECISIÓN: Usuario existente vs nuevo

  if (data.exists === true) {

    console.log("✅ USUARIO EXISTENTE - Procesando...")



    if (data.user && data.user.rol === "student") {

      console.log("🎓 Es estudiante - Redirigiendo a panel...")

      showUserDetectedAndRedirect(data)

    } else {

      console.log("👨‍🏫 Es docente/admin - Mostrando información...")

      showUserDetected(data)

    }

  } else if (data.exists === false) {

    console.log("🆕 USUARIO NUEVO - Mostrando formulario...")

    showRegistrationForm(data.uid)

  } else {

    console.error("❓ Estado desconocido - exists:", data.exists)

  }



  console.log("=" * 50)

}



// Función para mostrar usuario detectado Y redirigir

function showUserDetectedAndRedirect(data) {

  console.log("🎓 Mostrando usuario y preparando redirección...")



  // Actualizar interfaz

  let statusMessage = `Hola ${data.user.nombre}`

  if (data.attendance_registered) {

    statusMessage += ` - Asistencia registrada`

    if (data.subject) {

      statusMessage += ` para ${data.subject}`

    }

  }



  updateStatus("success", "¡Bienvenido Estudiante!", statusMessage)



  if (elements.userName) {

    elements.userName.textContent = data.user.nombre

  }

  if (elements.userDetails) {

    let details = `${data.user.matricula} - ${data.user.grupo || "Grupo 4302"}`

    if (data.attendance_registered && data.subject) {

      details += `\n✅ Asistencia: ${data.subject}`

    }

    elements.userDetails.textContent = details

  }



  // Mostrar sección de usuario detectado

  if (elements.userDetected) {

    elements.userDetected.style.display = "flex"

    console.log("✅ Sección de usuario mostrada")

  }



  // Redirigir después de 4 segundos (más tiempo para ver la confirmación)

  console.log("⏰ Redirigiendo a panel de estudiante en 4 segundos...")



  let countdown = 4

  const countdownInterval = setInterval(() => {

    let countdownMessage = `Redirigiendo en ${countdown} segundos...`

    if (data.attendance_registered) {

      countdownMessage = `✅ Asistencia registrada - ${countdownMessage}`

    }

    updateStatus("success", "¡Bienvenido!", countdownMessage)

    countdown--



    if (countdown < 0) {

      clearInterval(countdownInterval)

      console.log("🚀 Redirigiendo a student.html...")

      window.location.href = `/student.html?uid=${data.uid}&name=${encodeURIComponent(data.user.nombre)}`

    }

  }, 1000)

}



// Función para mostrar usuario detectado (sin redirecci��n)

function showUserDetected(data) {

  console.log("👤 Mostrando información de usuario (sin redirección)...")



  if (data.user) {

    if (elements.userName) {

      elements.userName.textContent = data.user.nombre

    }

    if (elements.userDetails) {

      elements.userDetails.textContent = `${data.user.matricula} - Rol: ${data.user.rol}`

    }



    if (data.success) {

      updateStatus("success", "Usuario Detectado", data.message)

    } else {

      updateStatus("warning", "Acceso Limitado", data.message)

    }

  }



  // Mostrar sección de usuario detectado

  if (elements.userDetected) {

    elements.userDetected.style.display = "flex"

  }



  // Auto-ocultar después de 8 segundos

  setTimeout(() => {

    hideAllSections()

    resetStatus()

    currentUID = null

    lastProcessedUID = null

  }, 8000)

}



// Función MEJORADA para mostrar formulario de registro

function showRegistrationForm(uid) {

  console.log("📝 MOSTRANDO FORMULARIO DE REGISTRO")

  console.log("📝 UID a registrar:", uid)



  // Verificar que tenemos los elementos necesarios

  if (!elements.registrationForm) {

    console.error("❌ ERROR: No se encontró el elemento registrationForm")

    return

  }



  if (!elements.uid) {

    console.error("❌ ERROR: No se encontró el elemento uid (input)")

    return

  }



  // Actualizar estado

  updateStatus("waiting", "Usuario Nuevo Detectado", "Complete el formulario para registrarse")



  // LLENAR EL CAMPO UID - MÉTODO ROBUSTO

  try {

    elements.uid.value = uid

    elements.uid.setAttribute("value", uid)



    console.log("✅ UID asignado al campo:")

    console.log("   - elements.uid.value:", elements.uid.value)

    console.log("   - elements.uid.getAttribute('value'):", elements.uid.getAttribute("value"))



    // Verificación adicional

    setTimeout(() => {

      console.log("🔍 Verificación después de 100ms:")

      console.log("   - Valor actual:", elements.uid.value)

    }, 100)

  } catch (error) {

    console.error("❌ Error llenando campo UID:", error)

  }



  // MOSTRAR FORMULARIO - MÉTODO ROBUSTO

  try {

    elements.registrationForm.style.display = "block"

    elements.registrationForm.style.visibility = "visible"

    elements.registrationForm.style.opacity = "1"



    console.log("✅ Formulario mostrado:")

    console.log("   - display:", elements.registrationForm.style.display)

    console.log("   - visibility:", elements.registrationForm.style.visibility)



    // Verificación visual

    setTimeout(() => {

      const computedStyle = window.getComputedStyle(elements.registrationForm)

      console.log("🔍 Estilo computado del formulario:")

      console.log("   - display:", computedStyle.display)

      console.log("   - visibility:", computedStyle.visibility)

      console.log("   - opacity:", computedStyle.opacity)

    }, 100)

  } catch (error) {

    console.error("❌ Error mostrando formulario:", error)

  }



  // Enfocar el primer campo editable

  setTimeout(() => {

    const nombreField = document.getElementById("nombre")

    if (nombreField) {

      nombreField.focus()

      console.log("✅ Campo nombre enfocado")

    }

  }, 200)

}



// Función para simular RFID - MEJORADA

function simulateRFID(uid) {

  console.log("🧪 SIMULANDO RFID:", uid)

  console.log("🔄 Reseteando estado anterior...")



  // Resetear estado anterior

  lastProcessedUID = null

  currentUID = null

  hideAllSections()

  resetStatus()



  // Enviar al backend

  fetch("/api/rfid", {

    method: "POST",

    headers: {

      "Content-Type": "application/json",

    },

    body: JSON.stringify({ tag: uid }),

  })

    .then((response) => {

      console.log("📡 Respuesta HTTP:", response.status)

      return response.json()

    })

    .then((data) => {

      console.log("✅ Respuesta del servidor:", data)



      // Procesar inmediatamente (sin esperar polling)

      handleRFIDDetected(data)

    })

    .catch((error) => {

      console.error("❌ Error simulando RFID:", error)

      updateStatus("error", "Error", "No se pudo simular RFID")

    })

}



// Función para manejar registro de estudiante

async function handleStudentRegistration(event) {

  event.preventDefault()



  console.log("📤 ENVIANDO REGISTRO DE ESTUDIANTE")



  const formData = new FormData(event.target)

  const studentData = {

    uid: formData.get("uid"),

    nombre_completo: formData.get("nombre"),

    matricula: formData.get("matricula"),

    email: formData.get("email"),

  }



  console.log("📋 Datos del estudiante:", studentData)



  // Validación básica

  if (!studentData.uid || !studentData.nombre_completo || !studentData.matricula) {

    console.error("❌ Datos incompletos")

    updateStatus("error", "Error", "Complete todos los campos obligatorios")

    return

  }



  try {

    const response = await fetch("/api/register-student", {

      method: "POST",

      headers: {

        "Content-Type": "application/json",

      },

      body: JSON.stringify(studentData),

    })



    const result = await response.json()

    console.log("✅ Respuesta del registro:", result)



    if (result.success) {

      updateStatus("success", "¡Registro Exitoso!", result.message)



      // Ocultar formulario y redirigir después de 2 segundos

      setTimeout(() => {

        console.log("🚀 Redirigiendo a panel de estudiante...")

        window.location.href = `/student.html?uid=${studentData.uid}&name=${encodeURIComponent(studentData.nombre_completo)}`

      }, 2000)

    } else {

      updateStatus("error", "Error en Registro", result.message)

    }

  } catch (error) {

    console.error("❌ Error registrando estudiante:", error)

    updateStatus("error", "Error de Conexión", "No se pudo conectar con el servidor")

  }

}



// Funciones de utilidad

function updateStatus(type, title, message) {

  if (elements.statusCard) {

    elements.statusCard.className = `status-card ${type}`

  }

  if (elements.statusTitle) {

    elements.statusTitle.textContent = title

  }

  if (elements.statusMessage) {

    elements.statusMessage.textContent = message

  }



  const icons = {

    waiting: "fas fa-wifi",

    success: "fas fa-check-circle",

    error: "fas fa-exclamation-triangle",

    warning: "fas fa-exclamation-circle",

  }



  if (elements.statusIcon) {

    elements.statusIcon.className = icons[type] || "fas fa-wifi"

  }

}



function resetStatus() {

  updateStatus("waiting", "Esperando Tarjeta RFID...", "Acerca tu tarjeta al lector para registrarte")

}



function hideAllSections() {

  console.log("🙈 Ocultando todas las secciones")



  if (elements.userDetected) {

    elements.userDetected.style.display = "none"

  }

  if (elements.registrationForm) {

    elements.registrationForm.style.display = "none"

  }

}



function cancelRegistration() {

  console.log("❌ Cancelando registro")

  hideAllSections()

  resetStatus()

  currentUID = null

  lastProcessedUID = null

}



function confirmAttendance() {

  console.log("✅ Confirmando asistencia para:", currentUID)

  // Aquí podrías agregar lógica adicional si es necesario

}



function viewProfile() {

  if (currentUID) {

    window.location.href = `/student.html?uid=${currentUID}`

  }

}



// Verificar conexión del servidor

async function checkServerConnection() {

  try {

    const response = await fetch("/api/health")

    if (response.ok) {

      const data = await response.json()

      console.log("✅ Servidor conectado:", data.message)

      return true

    }

    return false

  } catch (error) {

    console.error("❌ Error verificando conexión al servidor:", error)

    return false

  }

}



// INICIALIZACIÓN MEJORADA

document.addEventListener("DOMContentLoaded", async () => {

  console.log("🚀 INICIALIZANDO SISTEMA RFID...")

  console.log("🌐 URL actual:", window.location.href)



  // 1. Inicializar elementos DOM

  const elementsOk = initializeElements()

  if (!elementsOk) {

    console.error("❌ ERROR CRÍTICO: No se pudieron inicializar todos los elementos DOM")

    return

  }



  // 2. Verificar servidor

  console.log("🔍 Verificando conexión al servidor...")

  const serverOk = await checkServerConnection()

  if (!serverOk) {

    console.error("❌ Servidor no disponible")

    updateStatus("error", "Error", "Servidor no disponible")

    return

  }



  // 3. Configurar eventos

  if (elements.studentForm) {

    elements.studentForm.addEventListener("submit", handleStudentRegistration)

    console.log("📝 Formulario de registro configurado")

  }



  if (elements.cancelBtn) {

    elements.cancelBtn.addEventListener("click", cancelRegistration)

    console.log("❌ Botón cancelar configurado")

  }



  // 4. Iniciar polling (menos frecuente para evitar spam)

  pollInterval = setInterval(checkRFIDStatus, 2000)

  console.log("🔄 Polling iniciado (cada 2 segundos)")



  // 5. Estado inicial

  resetStatus()

  console.log("✅ SISTEMA RFID COMPLETAMENTE LISTO")

  console.log("💡 Usa los botones de prueba para simular tarjetas RFID")

})



// Limpiar al cerrar la página

window.addEventListener("beforeunload", () => {

  if (pollInterval) {

    clearInterval(pollInterval)

  }

})



// Hacer funciones globales

window.simulateRFID = simulateRFID

window.confirmAttendance = confirmAttendance

window.cancelRegistration = cancelRegistration

window.viewProfile = viewProfile
