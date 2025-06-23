// Variables globales
let currentUID = null
let lastProcessedUID = null
let pollInterval = null
let availableCareers = []
let selectedCareer = null
let selectedSemester = null

// Elementos DOM
const elements = {}

// Carreras con iconos
const CAREER_ICONS = {
  ISC: "fas fa-laptop-code",
  II: "fas fa-industry",
  IM: "fas fa-robot",
  IC: "fas fa-building",
  LA: "fas fa-briefcase",
  IQ: "fas fa-flask",
  IL: "fas fa-truck",
  ITIC: "fas fa-network-wired",
}

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
    "careerGrid",
    "semesterSelector",
    "semesterGrid",
    "carrera_id",
    "semestre",
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

// Cargar carreras disponibles
async function loadCareers() {
  try {
    const response = await fetch("/api/careers")
    const data = await response.json()

    if (data.success) {
      availableCareers = data.careers
      renderCareerOptions()
    } else {
      console.error("Error cargando carreras:", data.message)
      // Usar carreras por defecto si no se pueden cargar
      loadDefaultCareers()
    }
  } catch (error) {
    console.error("Error de conexión cargando carreras:", error)
    loadDefaultCareers()
  }
}

// Carreras por defecto si no se pueden cargar de la BD
function loadDefaultCareers() {
  availableCareers = [
    { id: 1, nombre: "Ingeniería en Sistemas Computacionales", codigo: "ISC", semestres: 9 },
    { id: 2, nombre: "Ingeniería Industrial", codigo: "II", semestres: 9 },
    { id: 3, nombre: "Ingeniería Mecatrónica", codigo: "IM", semestres: 9 },
    { id: 4, nombre: "Ingeniería Civil", codigo: "IC", semestres: 9 },
    { id: 5, nombre: "Licenciatura en Administración", codigo: "LA", semestres: 9 },
    { id: 6, nombre: "Ingeniería Química", codigo: "IQ", semestres: 9 },
    { id: 7, nombre: "Ingeniería en Logística", codigo: "IL", semestres: 9 },
    { id: 8, nombre: "Ingeniería en Tecnologías de la Información y Comunicaciones", codigo: "ITIC", semestres: 9 },
  ]
  renderCareerOptions()
}

// Renderizar opciones de carrera
function renderCareerOptions() {
  if (!elements.careerGrid) return

  elements.careerGrid.innerHTML = availableCareers
    .map(
      (career) => `
        <div class="career-option" data-career-id="${career.id}" onclick="selectCareer(${career.id})">
            <i class="${CAREER_ICONS[career.codigo] || "fas fa-graduation-cap"} career-icon"></i>
            <div class="career-name">${career.nombre}</div>
            <div class="career-code">${career.codigo} - ${career.semestres} semestres</div>
        </div>
    `,
    )
    .join("")
}

// Seleccionar carrera
function selectCareer(careerId) {
  selectedCareer = availableCareers.find((c) => c.id === careerId)

  if (!selectedCareer) return

  // Actualizar UI
  document.querySelectorAll(".career-option").forEach((el) => {
    el.classList.remove("selected")
  })
  document.querySelector(`[data-career-id="${careerId}"]`).classList.add("selected")

  // Llenar campo oculto
  if (elements.carrera_id) {
    elements.carrera_id.value = careerId
  }

  // Mostrar selector de semestre
  renderSemesterOptions()
  if (elements.semesterSelector) {
    elements.semesterSelector.style.display = "block"
  }

  console.log(`✅ Carrera seleccionada: ${selectedCareer.nombre}`)
}

// Renderizar opciones de semestre
function renderSemesterOptions() {
  if (!selectedCareer || !elements.semesterGrid) return

  elements.semesterGrid.innerHTML = ""

  for (let i = 1; i <= selectedCareer.semestres; i++) {
    const semesterDiv = document.createElement("div")
    semesterDiv.className = "semester-option"
    semesterDiv.textContent = `${i}°`
    semesterDiv.onclick = () => selectSemester(i)
    elements.semesterGrid.appendChild(semesterDiv)
  }
}

// Seleccionar semestre
function selectSemester(semester) {
  selectedSemester = semester

  // Actualizar UI
  document.querySelectorAll(".semester-option").forEach((el) => {
    el.classList.remove("selected")
  })
  event.target.classList.add("selected")

  // Llenar campo oculto
  if (elements.semestre) {
    elements.semestre.value = semester
  }

  console.log(`�� Semestre seleccionado: ${semester}°`)
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
      lastProcessedUID = data.uid
      handleRFIDDetected(data)
    }
  } catch (error) {
    console.error("❌ Error consultando estado RFID:", error)
  }
}

// Función para manejar RFID detectado
function handleRFIDDetected(data) {
  console.log("🎫 PROCESANDO RFID DETECTADO:", data)

  currentUID = data.uid
  hideAllSections()

  if (data.exists === true) {
    if (data.user && data.user.rol === "student") {
      showUserDetectedAndRedirect(data)
    } else {
      showUserDetected(data)
    }
  } else if (data.exists === false) {
    showRegistrationForm(data.uid)
  }
}

// Mostrar usuario detectado y redirigir
function showUserDetectedAndRedirect(data) {
  console.log("🎓 Mostrando usuario y preparando redirección...")

  let statusMessage = `Hola ${data.user.nombre}`
  if (data.attendance_registered) {
    statusMessage += ` - Asistencia registrada`
  }

  updateStatus("success", "¡Bienvenido Estudiante!", statusMessage)

  if (elements.userName) {
    elements.userName.textContent = data.user.nombre
  }
  if (elements.userDetails) {
    let details = `${data.user.matricula}`
    if (data.user.carrera) {
      details += ` - ${data.user.carrera}`
    }
    if (data.user.semestre) {
      details += ` - ${data.user.semestre}° Semestre`
    }
    elements.userDetails.textContent = details
  }

  if (elements.userDetected) {
    elements.userDetected.style.display = "flex"
  }

  // Redirigir después de 4 segundos
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
      window.location.href = `/student.html?uid=${data.uid}&name=${encodeURIComponent(data.user.nombre)}`
    }
  }, 1000)
}

// Mostrar usuario detectado (sin redirección)
function showUserDetected(data) {
  console.log("👤 Mostrando información de usuario...")

  if (data.user) {
    if (elements.userName) {
      elements.userName.textContent = data.user.nombre
    }
    if (elements.userDetails) {
      elements.userDetails.textContent = `${data.user.matricula} - Rol: ${data.user.rol}`
    }

    updateStatus("success", "Usuario Detectado", data.message)
  }

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

// Mostrar formulario de registro
function showRegistrationForm(uid) {
  console.log("📝 MOSTRANDO FORMULARIO DE REGISTRO:", uid)

  if (!elements.registrationForm || !elements.uid) {
    console.error("❌ ERROR: Elementos del formulario no encontrados")
    return
  }

  updateStatus("waiting", "Usuario Nuevo Detectado", "Complete el formulario para registrarse")

  // Llenar UID
  elements.uid.value = uid

  // Mostrar formulario
  elements.registrationForm.style.display = "block"

  // Enfocar primer campo
  setTimeout(() => {
    const nombreField = document.getElementById("nombre")
    if (nombreField) {
      nombreField.focus()
    }
  }, 200)
}

// Manejar registro de estudiante
async function handleStudentRegistration(event) {
  event.preventDefault()

  console.log("📤 ENVIANDO REGISTRO DE ESTUDIANTE")

  const formData = new FormData(event.target)
  const studentData = {
    uid: formData.get("uid"),
    nombre_completo: formData.get("nombre"),
    matricula: formData.get("matricula"),
    email: formData.get("email"),
    carrera_id: formData.get("carrera_id"),
    semestre: formData.get("semestre"),
  }

  console.log("📋 Datos del estudiante:", studentData)

  // Validación
  if (
    !studentData.uid ||
    !studentData.nombre_completo ||
    !studentData.matricula ||
    !studentData.carrera_id ||
    !studentData.semestre
  ) {
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

      setTimeout(() => {
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

// Simular RFID
function simulateRFID(uid) {
  console.log("🧪 SIMULANDO RFID:", uid)

  lastProcessedUID = null
  currentUID = null
  hideAllSections()
  resetStatus()

  fetch("/api/rfid", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tag: uid }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("✅ Respuesta del servidor:", data)
      handleRFIDDetected(data)
    })
    .catch((error) => {
      console.error("❌ Error simulando RFID:", error)
      updateStatus("error", "Error", "No se pudo simular RFID")
    })
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
  if (elements.userDetected) {
    elements.userDetected.style.display = "none"
  }
  if (elements.registrationForm) {
    elements.registrationForm.style.display = "none"
  }
}

function cancelRegistration() {
  hideAllSections()
  resetStatus()
  currentUID = null
  lastProcessedUID = null
  selectedCareer = null
  selectedSemester = null
}

function confirmAttendance() {
  console.log("✅ Confirmando asistencia para:", currentUID)
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
      console.log("✅ Servidor conectado")
      return true
    }
    return false
  } catch (error) {
    console.error("❌ Error verificando servidor:", error)
    return false
  }
}

// INICIALIZACIÓN
document.addEventListener("DOMContentLoaded", async () => {
  console.log("🚀 INICIALIZANDO SISTEMA RFID PROFESIONAL...")

  // 1. Inicializar elementos DOM
  const elementsOk = initializeElements()
  if (!elementsOk) {
    console.error("❌ ERROR: No se pudieron inicializar elementos DOM")
    return
  }

  // 2. Verificar servidor
  const serverOk = await checkServerConnection()
  if (!serverOk) {
    updateStatus("error", "Error", "Servidor no disponible")
    return
  }

  // 3. Cargar carreras
  await loadCareers()

  // 4. Configurar eventos
  if (elements.studentForm) {
    elements.studentForm.addEventListener("submit", handleStudentRegistration)
  }

  if (elements.cancelBtn) {
    elements.cancelBtn.addEventListener("click", cancelRegistration)
  }

  // 5. Iniciar polling
  pollInterval = setInterval(checkRFIDStatus, 2000)

  // 6. Estado inicial
  resetStatus()
  console.log("✅ SISTEMA RFID PROFESIONAL LISTO")
})

// Limpiar al cerrar
window.addEventListener("beforeunload", () => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})

// Hacer funciones globales
window.simulateRFID = simulateRFID
window.selectCareer = selectCareer
window.selectSemester = selectSemester
window.confirmAttendance = confirmAttendance
window.cancelRegistration = cancelRegistration
window.viewProfile = viewProfile
