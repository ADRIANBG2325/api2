console.log("🚀 student.js cargado - Versión 3.0 Optimizada con horarios reales")

// HORARIOS REALES DEL SALÓN N1 (Grupo 3402)
const HORARIOS_SALON_N1 = {
  Lunes: [
    {
      materia: "Métodos Numéricos",
      codigo: "SCC-1017",
      salon: "N1",
      hora_inicio: "07:00",
      hora_fin: "09:00",
      tipo: "Teoría",
      creditos: 4,
      maestro: "Lic. Juan Alberto Martínez Zamora",
    },
    {
      materia: "Ecuaciones Diferenciales",
      codigo: "ACF-0905",
      salon: "N1",
      hora_inicio: "09:00",
      hora_fin: "12:00",
      tipo: "Teoría",
      creditos: 5,
      maestro: "Ing. Rodolfo Guadalupe Alcántara Rosales",
    },
    {
      materia: "Tutorías",
      codigo: "TUT-001",
      salon: "N1",
      hora_inicio: "12:00",
      hora_fin: "14:00",
      tipo: "Tutoría",
      creditos: 0,
      maestro: "Tutor Asignado",
    },
    {
      materia: "Fundamentos de Base de Datos",
      codigo: "AEF-1031",
      salon: "N1",
      hora_inicio: "15:00",
      hora_fin: "18:00",
      tipo: "Teoría",
      creditos: 5,
      maestro: "Mtra. Yadira Esther Jiménez Pérez",
    },
  ],
  Martes: [
    {
      materia: "Inglés",
      codigo: "ING-001",
      salon: "N1",
      hora_inicio: "09:00",
      hora_fin: "11:00",
      tipo: "Idioma",
      creditos: 2,
      maestro: "L.L. Isodoro Cruz Huitrón",
    },
    {
      materia: "Arquitectura de Computadoras",
      codigo: "SCD-1003",
      salon: "N1",
      hora_inicio: "11:00",
      hora_fin: "13:00",
      tipo: "Teoría",
      creditos: 5,
      maestro: "Ing. Alfredo Aguilar López",
    },
    {
      materia: "Tópicos Avanzados de Programación",
      codigo: "SCD-1027",
      salon: "N1",
      hora_inicio: "13:00",
      hora_fin: "15:00",
      tipo: "Práctica",
      creditos: 5,
      maestro: "Víctor David Maya Arce",
    },
  ],
  Miércoles: [
    {
      materia: "Métodos Numéricos",
      codigo: "SCC-1017",
      salon: "N1",
      hora_inicio: "07:00",
      hora_fin: "09:00",
      tipo: "Teoría",
      creditos: 4,
      maestro: "Lic. Juan Alberto Martínez Zamora",
    },
    {
      materia: "Inglés",
      codigo: "ING-001",
      salon: "N1",
      hora_inicio: "09:00",
      hora_fin: "11:00",
      tipo: "Idioma",
      creditos: 2,
      maestro: "L.L. Isodoro Cruz Huitrón",
    },
    {
      materia: "Ecuaciones Diferenciales",
      codigo: "ACF-0905",
      salon: "N1",
      hora_inicio: "11:00",
      hora_fin: "13:00",
      tipo: "Teoría",
      creditos: 5,
      maestro: "Ing. Rodolfo Guadalupe Alcántara Rosales",
    },
    {
      materia: "Taller de Sistemas Operativos",
      codigo: "SCA-1026",
      salon: "N1",
      hora_inicio: "13:00",
      hora_fin: "15:00",
      tipo: "Práctica",
      creditos: 4,
      maestro: "Mtro. Anselmo Martínez Montalvo",
    },
  ],
  Jueves: [
    {
      materia: "Inglés",
      codigo: "ING-001",
      salon: "N1",
      hora_inicio: "07:00",
      hora_fin: "09:00",
      tipo: "Idioma",
      creditos: 2,
      maestro: "L.L. Isodoro Cruz Huitrón",
    },
    {
      materia: "Taller de Ética",
      codigo: "ACA-0907",
      salon: "N1",
      hora_inicio: "09:00",
      hora_fin: "11:00",
      tipo: "Práctica",
      creditos: 4,
      maestro: "C.P. Sonia Vázquez Alcántara",
    },
    {
      materia: "Fundamentos de Base de Datos",
      codigo: "AEF-1031",
      salon: "N1",
      hora_inicio: "11:00",
      hora_fin: "13:00",
      tipo: "Teoría",
      creditos: 5,
      maestro: "Mtra. Yadira Esther Jiménez Pérez",
    },
    {
      materia: "Tópicos Avanzados de Programación",
      codigo: "SCD-1027",
      salon: "N1",
      hora_inicio: "14:00",
      hora_fin: "16:00",
      tipo: "Práctica",
      creditos: 5,
      maestro: "Víctor David Maya Arce",
    },
  ],
  Viernes: [
    {
      materia: "Taller de Sistemas Operativos",
      codigo: "SCA-1026",
      salon: "N1",
      hora_inicio: "07:00",
      hora_fin: "09:00",
      tipo: "Práctica",
      creditos: 4,
      maestro: "Mtro. Anselmo Martínez Montalvo",
    },
    {
      materia: "Taller de Ética",
      codigo: "ACA-0907",
      salon: "N1",
      hora_inicio: "09:00",
      hora_fin: "11:00",
      tipo: "Práctica",
      creditos: 4,
      maestro: "C.P. Sonia Vázquez Alcántara",
    },
    {
      materia: "Arquitectura de Computadoras",
      codigo: "SCD-1003",
      salon: "N1",
      hora_inicio: "11:00",
      hora_fin: "14:00",
      tipo: "Teoría",
      creditos: 5,
      maestro: "Ing. Alfredo Aguilar López",
    },
  ],
  Sábado: [],
  Domingo: [],
}

// HORARIOS TEMPORALES PARA SALÓN N2 (Grupo 3401) - Hasta que se proporcione el real
const HORARIOS_SALON_N2 = {
  Lunes: [
    {
      materia: "Programación Avanzada",
      codigo: "PRG-002",
      salon: "N2",
      hora_inicio: "08:00",
      hora_fin: "10:00",
      tipo: "Práctica",
      creditos: 5,
      maestro: "Ing. Ejemplo N2",
    },
  ],
  Martes: [],
  Miércoles: [
    {
      materia: "Base de Datos Avanzada",
      codigo: "BDA-002",
      salon: "N2",
      hora_inicio: "10:00",
      hora_fin: "12:00",
      tipo: "Teoría",
      creditos: 5,
      maestro: "Mtra. Ejemplo N2",
    },
  ],
  Jueves: [],
  Viernes: [],
  Sábado: [],
  Domingo: [],
}

// Información de los grupos
const GRUPOS_INFO = {
  N1: {
    id: 1,
    nombre: "Grupo 3402",
    salon: "N1",
    turno: "Matutino",
    semestre: 4,
    carrera: "Ingeniería en Sistemas Computacionales",
  },
  N2: {
    id: 2,
    nombre: "Grupo 3401",
    salon: "N2",
    turno: "Matutino",
    semestre: 4,
    carrera: "Ingeniería en Sistemas Computacionales",
  },
}

// Variables globales
let currentStudentData = null
let fullScheduleData = null

// Función para obtener parámetros de URL
function getURLParams() {
  const params = new URLSearchParams(window.location.search)
  return {
    uid: params.get("uid"),
    name: params.get("name"),
    matricula: params.get("matricula"),
    salon: params.get("salon"),
  }
}

// Obtener información del estudiante
function getStudentInfo() {
  const urlParams = getURLParams()

  if (urlParams.uid && urlParams.name) {
    const studentData = {
      nombre: decodeURIComponent(urlParams.name),
      matricula: urlParams.matricula || urlParams.uid,
      uid: urlParams.uid,
      salon: urlParams.salon || "N1",
    }
    localStorage.setItem("currentStudent", JSON.stringify(studentData))
    return studentData
  }

  const savedStudent = localStorage.getItem("currentStudent")
  if (savedStudent) {
    try {
      return JSON.parse(savedStudent)
    } catch (e) {
      console.error("Error parseando localStorage:", e)
    }
  }

  return {
    nombre: "Estudiante Demo",
    matricula: "EST123456",
    uid: "EST123456",
    salon: "N1",
  }
}

// Obtener horario según el salón
function getScheduleBySalon(salon) {
  console.log(`📅 Obteniendo horario para salón: ${salon}`)

  if (salon === "N1") {
    return HORARIOS_SALON_N1
  } else if (salon === "N2") {
    return HORARIOS_SALON_N2
  } else {
    // Por defecto usar N1
    return HORARIOS_SALON_N1
  }
}

// Actualizar interfaz básica
function updateStudentUI(student) {
  console.log("🔄 Actualizando UI para:", student)

  const nameElement = document.getElementById("student-name")
  const matriculaElement = document.getElementById("student-matricula")
  const grupoElement = document.getElementById("student-grupo")

  if (nameElement) nameElement.textContent = student.nombre
  if (matriculaElement) matriculaElement.textContent = `Matrícula: ${student.matricula}`

  // Obtener información del grupo según el salón
  const grupoInfo = GRUPOS_INFO[student.salon] || GRUPOS_INFO["N1"]
  if (grupoElement) {
    grupoElement.textContent = `${grupoInfo.nombre} - Salón ${grupoInfo.salon} - ${grupoInfo.turno}`
  }

  document.title = `TESJI - ${student.nombre}`

  const todayElement = document.getElementById("today-date")
  if (todayElement) {
    const today = new Date().toLocaleDateString("es-ES", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    })
    todayElement.textContent = today
  }
}

// Cargar horario desde API (con fallback a horarios locales)
async function loadStudentScheduleFromAPI() {
  const student = getStudentInfo()
  console.log("📅 Cargando horario desde API para UID:", student.uid)

  try {
    const response = await fetch(`/api/student/schedule?uid=${encodeURIComponent(student.uid)}`)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()
    console.log("📊 Respuesta del servidor:", data)

    if (data.success && data.schedule_by_day) {
      console.log("✅ Horario cargado desde API exitosamente")
      fullScheduleData = data
      renderFullSchedule(data)
      updateScheduleInfo(data)
      return true
    } else {
      console.warn("⚠️ API no devolvió horarios válidos:", data.message)
      return false
    }
  } catch (error) {
    console.error("❌ Error cargando horario desde API:", error)
    return false
  }
}

// Cargar horario local según el salón
function loadLocalSchedule(student) {
  console.log(`📅 Cargando horario local para salón: ${student.salon}`)

  const schedule_by_day = getScheduleBySalon(student.salon)
  const grupoInfo = GRUPOS_INFO[student.salon] || GRUPOS_INFO["N1"]

  // Calcular estadísticas
  const total_subjects = new Set()
  let total_classes = 0
  let days_with_classes = 0

  Object.entries(schedule_by_day).forEach(([dia, clases]) => {
    if (clases.length > 0) {
      days_with_classes++
      total_classes += clases.length
      clases.forEach((clase) => total_subjects.add(clase.materia))
    }
  })

  const scheduleData = {
    student: student,
    group: grupoInfo,
    schedule_by_day: schedule_by_day,
    total_subjects: total_subjects.size,
    total_classes: total_classes,
    days_with_classes: days_with_classes,
  }

  fullScheduleData = scheduleData
  renderFullSchedule(scheduleData)
  updateScheduleInfo(scheduleData)

  console.log(`✅ Horario local cargado para salón ${student.salon}`)
}

// Función principal para cargar información del estudiante
async function loadStudentInfo() {
  console.log("📚 Iniciando carga de información del estudiante")

  const student = getStudentInfo()
  currentStudentData = student
  updateStudentUI(student)

  console.log(`🎓 Estudiante: ${student.nombre} - Salón: ${student.salon}`)

  // Intentar cargar desde API primero
  console.log("🔄 Intentando cargar horario desde API...")
  const apiSuccess = await loadStudentScheduleFromAPI()

  if (!apiSuccess) {
    console.log("⚠️ API falló, usando horarios locales...")
    loadLocalSchedule(student)
  }

  // Cargar horario de hoy
  await loadTodaySchedule()

  return student
}

// Renderizar horario completo
function renderFullSchedule(scheduleData) {
  console.log("🎨 Renderizando horario completo:", scheduleData)

  const container = document.getElementById("student-weekly-schedule")
  if (!container) return

  const diasOrden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

  let scheduleHTML = '<div class="weekly-schedule-grid">'

  diasOrden.forEach((dia) => {
    const clasesDelDia = scheduleData.schedule_by_day[dia] || []
    console.log(`📅 ${dia}: ${clasesDelDia.length} clases`)

    scheduleHTML += `
      <div class="day-column ${clasesDelDia.length > 0 ? "has-classes" : "no-classes"}">
        <div class="day-header">
          <h4>${dia}</h4>
          <span class="class-count">${clasesDelDia.length} clases</span>
        </div>
        <div class="day-classes">
    `

    if (clasesDelDia.length > 0) {
      clasesDelDia.forEach((clase) => {
        scheduleHTML += `
          <div class="class-block">
            <div class="class-time">
              <i class="fas fa-clock"></i>
              ${clase.hora_inicio} - ${clase.hora_fin}
            </div>
            <div class="class-subject">${clase.materia}</div>
            <div class="class-details">
              <div class="class-code">${clase.codigo}</div>
              <div class="class-room"><i class="fas fa-map-marker-alt"></i> ${clase.salon}</div>
              <div class="class-teacher"><i class="fas fa-user"></i> ${clase.maestro}</div>
            </div>
            <div class="class-meta">
              <span class="class-type">${clase.tipo}</span>
              <span class="class-credits">${clase.creditos} créditos</span>
            </div>
          </div>
        `
      })
    } else {
      scheduleHTML += '<div class="no-classes-day">Sin clases</div>'
    }

    scheduleHTML += `
        </div>
      </div>
    `
  })

  scheduleHTML += "</div>"
  container.innerHTML = scheduleHTML
}

// Actualizar información del horario
function updateScheduleInfo(scheduleData) {
  console.log("ℹ️ Actualizando información del horario")

  const grupoElement = document.getElementById("schedule-group")
  const statsElement = document.getElementById("schedule-stats")

  if (scheduleData.group) {
    if (grupoElement) {
      grupoElement.textContent = `${scheduleData.group.nombre} - Salón ${scheduleData.group.salon} - ${scheduleData.group.turno}`
    }
  }

  if (statsElement) {
    statsElement.textContent = `${scheduleData.total_subjects} materias • ${scheduleData.total_classes} clases • ${scheduleData.days_with_classes} días`
  }

  // Actualizar estadísticas
  const totalSubjectsElement = document.getElementById("total-subjects")
  if (totalSubjectsElement) {
    totalSubjectsElement.textContent = scheduleData.total_subjects || 0
  }
}

// Cargar horario de hoy
async function loadTodaySchedule() {
  const student = getStudentInfo()
  console.log("📅 Cargando horario de hoy para:", student.uid)

  try {
    const response = await fetch(`/api/schedule/today?uid=${encodeURIComponent(student.uid)}&role=student`)
    const data = await response.json()

    console.log("📊 Horario de hoy desde API:", data)

    if (data.success && data.classes) {
      renderTodaySchedule(data.classes)
      return
    }
  } catch (error) {
    console.error("❌ Error cargando horario de hoy desde API:", error)
  }

  // Fallback: usar horario local
  const today = new Date().getDay() // 0 = Domingo, 1 = Lunes, etc.
  const diasSemana = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
  const hoy = diasSemana[today]

  console.log("📅 Hoy es:", hoy)

  const schedule_by_day = getScheduleBySalon(student.salon)
  const clasesHoy = schedule_by_day[hoy] || []
  renderTodaySchedule(clasesHoy)
}

// Renderizar horario de hoy
function renderTodaySchedule(classes) {
  console.log("🎨 Renderizando horario de hoy:", classes)

  const container = document.getElementById("today-schedule")
  if (!container) return

  if (classes.length === 0) {
    container.innerHTML = `
      <div class="no-classes-today">
        <i class="fas fa-calendar-times"></i>
        <h4>Sin clases hoy</h4>
        <p>¡Disfruta tu día libre!</p>
      </div>
    `
    return
  }

  const now = new Date()

  container.innerHTML = classes
    .map((clase, index) => {
      // Determinar estado de la clase
      const horaInicio = new Date()
      const [hora, minuto] = clase.hora_inicio.split(":")
      horaInicio.setHours(Number.parseInt(hora), Number.parseInt(minuto), 0, 0)

      const horaFin = new Date()
      const [horaF, minutoF] = clase.hora_fin.split(":")
      horaFin.setHours(Number.parseInt(horaF), Number.parseInt(minutoF), 0, 0)

      let statusClass = "pending"
      let statusIcon = "fas fa-clock"
      let statusText = "Pendiente"

      if (now > horaFin) {
        statusClass = "completed"
        statusIcon = "fas fa-check-circle"
        statusText = "Completada"
      } else if (now >= horaInicio && now <= horaFin) {
        statusClass = "current"
        statusIcon = "fas fa-play-circle"
        statusText = "En curso"
      }

      return `
      <div class="today-class-item ${statusClass}">
        <div class="class-status-indicator">
          <i class="${statusIcon}"></i>
          <span class="status-text">${statusText}</span>
        </div>
        <div class="class-time-today">
          <i class="fas fa-clock"></i>
          ${clase.hora_inicio} - ${clase.hora_fin}
        </div>
        <div class="class-info-today">
          <div class="class-subject-today">${clase.materia}</div>
          <div class="class-details-today">
            <span class="class-code-today">${clase.codigo}</span>
            <span class="class-room-today"><i class="fas fa-map-marker-alt"></i> ${clase.salon}</span>
            <span class="class-teacher-today"><i class="fas fa-user"></i> ${clase.maestro}</span>
          </div>
        </div>
      </div>
    `
    })
    .join("")
}

// Funciones de acciones
function registerAttendance() {
  const student = getStudentInfo()
  alert(`✅ Asistencia registrada correctamente para ${student.nombre}`)
}

function refreshSchedule() {
  console.log("🔄 Refrescando horario...")
  loadStudentInfo()
}

function viewGrades() {
  const student = getStudentInfo()
  alert(`📊 Consultando calificaciones de ${student.nombre}...`)
}

function downloadReport() {
  const student = getStudentInfo()
  alert(`📄 Generando reporte PDF para ${student.nombre}...`)
}

function logout() {
  localStorage.removeItem("currentStudent")
  window.location.href = "/"
}

// Hacer funciones globales
window.registerAttendance = registerAttendance
window.refreshSchedule = refreshSchedule
window.viewGrades = viewGrades
window.downloadReport = downloadReport
window.logout = logout
window.loadStudentInfo = loadStudentInfo

// Ejecutar cuando el DOM esté listo
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", loadStudentInfo)
} else {
  setTimeout(loadStudentInfo, 100)
}

console.log("✅ student.js v3.0 completamente cargado con horarios reales optimizados")
