// Variables globales
let currentTeacher = null
let selectedSubject = null
let teacherSubjects = []
let currentAttendance = []
let attendanceActive = false

// Elementos DOM
const elements = {
  teacherName: document.getElementById("teacherName"),
  teacherDetails: document.getElementById("teacherDetails"),
  subjectGrid: document.getElementById("subjectGrid"),
  startAttendanceBtn: document.getElementById("startAttendanceBtn"),
  attendanceStatus: document.getElementById("attendanceStatus"),
  attendanceList: document.getElementById("attendanceList"),
  totalStudents: document.getElementById("totalStudents"),
  presentStudents: document.getElementById("presentStudents"),
  absentStudents: document.getElementById("absentStudents"),
  attendancePercentage: document.getElementById("attendancePercentage"),
}

// Función para mostrar errores
function showError(message) {
  alert("Error: " + message)
}

// Inicialización
document.addEventListener("DOMContentLoaded", async () => {
  console.log("🚀 Iniciando panel del maestro...")

  try {
    // Cargar información del maestro
    const teacherLoaded = await loadTeacherInfo()
    if (!teacherLoaded) {
      console.error("❌ No se pudo cargar información del maestro")
      return
    }

    // Cargar materias
    await loadTeacherSubjects()

    // Cargar horario completo
    await loadTeacherSchedule()

    console.log("✅ Panel del maestro cargado completamente")
  } catch (error) {
    console.error("❌ Error durante la inicialización:", error)
    showError("Error al cargar el panel. Usando datos de ejemplo.")

    // Cargar datos de ejemplo como fallback
    loadSampleTeacherData()
    loadSampleSubjects()
    renderSubjects()
    loadSampleSchedule()
  }
})

// Cargar información del maestro
async function loadTeacherInfo() {
  try {
    // Obtener token del localStorage
    const token = localStorage.getItem("teacher_token")
    if (!token) {
      window.location.href = "/login-teacher.html"
      return
    }

    const response = await fetch("/api/teacher/profile", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (response.ok) {
      const data = await response.json()
      currentTeacher = data.teacher

      elements.teacherName.textContent = currentTeacher.nombre
      elements.teacherDetails.textContent = `${currentTeacher.matricula} - ${currentTeacher.email}`
    } else {
      // Token inválido, redirigir al login
      localStorage.removeItem("teacher_token")
      window.location.href = "/login-teacher.html"
    }
  } catch (error) {
    console.error("Error cargando información del maestro:", error)
    // Usar datos de ejemplo si no se puede conectar
    loadSampleTeacherData()
  }
}

// Datos de ejemplo del maestro
function loadSampleTeacherData() {
  currentTeacher = {
    id: 1,
    nombre: "Dr. Juan Carlos Pérez",
    matricula: "PROF001",
    email: "juan.perez@tesji.edu.mx",
  }

  elements.teacherName.textContent = currentTeacher.nombre
  elements.teacherDetails.textContent = `${currentTeacher.matricula} - ${currentTeacher.email}`
}

// Cargar horario completo del maestro - MEJORADO
async function loadTeacherSchedule() {
  try {
    const token = localStorage.getItem("teacher_token")
    const response = await fetch("/api/teacher/schedule", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        renderTeacherSchedule(data)
        return
      }
    }

    // Fallback a horario de ejemplo mejorado
    loadSampleSchedule()
  } catch (error) {
    console.error("Error cargando horario del maestro:", error)
    loadSampleSchedule()
  }
}

// Renderizar horario completo del maestro - MEJORADO
function renderTeacherSchedule(scheduleData) {
  console.log("📅 Renderizando horario del maestro:", scheduleData)

  // Actualizar información del maestro
  if (scheduleData.teacher) {
    elements.teacherName.textContent = scheduleData.teacher.nombre
    elements.teacherDetails.textContent = `${scheduleData.teacher.matricula} - ${scheduleData.teacher.especialidad}`
  }

  // Crear sección de horario si no existe
  let scheduleSection = document.getElementById("teacher-schedule-section")
  if (!scheduleSection) {
    scheduleSection = document.createElement("div")
    scheduleSection.id = "teacher-schedule-section"
    scheduleSection.className = "card schedule-card"
    scheduleSection.innerHTML = `
            <div class="card-header">
                <div class="header-icon">
                    <i class="fas fa-calendar-week"></i>
                </div>
                <div class="header-content">
                    <h3>Mi Horario Semanal</h3>
                    <div class="schedule-stats">
                        <span id="total-classes-week" class="stat-badge primary">0 clases</span>
                        <span id="total-hours-week" class="stat-badge success">0 horas</span>
                    </div>
                </div>
            </div>
            <div id="weekly-schedule-container"></div>
        `

    // Insertar después del grid de materias
    const subjectGrid = document.getElementById("subjectGrid")
    if (subjectGrid && subjectGrid.parentNode) {
      subjectGrid.parentNode.insertBefore(scheduleSection, subjectGrid.nextSibling)
    }
  }

  // Actualizar estadísticas
  document.getElementById("total-classes-week").textContent = `${scheduleData.total_classes} clases`
  document.getElementById("total-hours-week").textContent = `${scheduleData.total_hours_per_week} horas`

  // Renderizar horario por días
  const container = document.getElementById("weekly-schedule-container")
  const diasOrden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

  let scheduleHTML = '<div class="weekly-schedule-teacher">'

  diasOrden.forEach((dia) => {
    const clasesDelDia = scheduleData.schedule_by_day[dia] || []

    scheduleHTML += `
            <div class="day-schedule-teacher ${clasesDelDia.length > 0 ? "has-classes" : "no-classes"}">
                <div class="day-header-teacher">
                    <h4>${dia}</h4>
                    <span class="day-count-teacher">${clasesDelDia.length} clases</span>
                </div>
                <div class="day-classes-teacher">
        `

    if (clasesDelDia.length > 0) {
      clasesDelDia.forEach((clase) => {
        scheduleHTML += `
                    <div class="class-item-teacher" onclick="selectSubjectByName('${clase.materia}')">
                        <div class="class-time-teacher">
                            <i class="fas fa-clock"></i>
                            <span>${clase.hora_inicio} - ${clase.hora_fin}</span>
                        </div>
                        <div class="class-info-teacher">
                            <div class="class-subject-teacher">${clase.materia}</div>
                            <div class="class-details-teacher">
                                <span class="class-code-teacher">${clase.codigo}</span>
                                <span class="class-group-teacher">${clase.grupo}</span>
                                <span class="class-room-teacher">
                                    <i class="fas fa-map-marker-alt"></i> ${clase.salon}
                                </span>
                            </div>
                            <div class="class-meta-teacher">
                                <span class="class-type-teacher">${clase.tipo}</span>
                                <span class="class-credits-teacher">${clase.creditos} créditos</span>
                            </div>
                        </div>
                    </div>
                `
      })
    } else {
      scheduleHTML += '<div class="no-classes-message-teacher">Sin clases programadas</div>'
    }

    scheduleHTML += `
                </div>
            </div>
        `
  })

  scheduleHTML += "</div>"
  container.innerHTML = scheduleHTML

  // Agregar estilos CSS para el horario
  addScheduleStyles()
}

// Cargar horario de ejemplo mejorado
function loadSampleSchedule() {
  const sampleScheduleData = {
    teacher: {
      nombre: "Dr. Juan Carlos Pérez",
      matricula: "PROF001",
      especialidad: "Programación y Base de Datos",
    },
    schedule_by_day: {
      Lunes: [
        {
          materia: "Tópicos Avanzados de Programación",
          codigo: "SCD-1027",
          grupo: "Grupo N2",
          salon: "N2",
          hora_inicio: "12:00",
          hora_fin: "15:00",
          tipo: "Práctica",
          creditos: 5,
        },
        {
          materia: "Fundamentos de Base de Datos",
          codigo: "AEF-1031",
          grupo: "Grupo N1",
          salon: "N1",
          hora_inicio: "15:00",
          hora_fin: "18:00",
          tipo: "Teoría",
          creditos: 5,
        },
      ],
      Martes: [
        {
          materia: "Tópicos Avanzados de Programación",
          codigo: "SCD-1027",
          grupo: "Grupo N2",
          salon: "N2",
          hora_inicio: "13:00",
          hora_fin: "15:00",
          tipo: "Práctica",
          creditos: 5,
        },
      ],
      Miércoles: [
        {
          materia: "Tópicos Avanzados de Programación",
          codigo: "SCD-1027",
          grupo: "Grupo N2",
          salon: "N2",
          hora_inicio: "09:00",
          hora_fin: "11:00",
          tipo: "Teoría",
          creditos: 5,
        },
      ],
      Jueves: [
        {
          materia: "Fundamentos de Base de Datos",
          codigo: "AEF-1031",
          grupo: "Grupo N1",
          salon: "N1",
          hora_inicio: "11:00",
          hora_fin: "13:00",
          tipo: "Teoría",
          creditos: 5,
        },
        {
          materia: "Tópicos Avanzados de Programación",
          codigo: "SCD-1027",
          grupo: "Grupo N2",
          salon: "N2",
          hora_inicio: "14:00",
          hora_fin: "16:00",
          tipo: "Práctica",
          creditos: 5,
        },
      ],
      Viernes: [],
      Sábado: [],
    },
    total_classes: 6,
    total_hours_per_week: 15,
    days_with_classes: 4,
  }

  renderTeacherSchedule(sampleScheduleData)
}

// Seleccionar materia por nombre (para integración con horario)
function selectSubjectByName(subjectName) {
  const subject = teacherSubjects.find((s) => s.nombre === subjectName)
  if (subject) {
    selectSubject(subject.id)
  }
}

// Agregar estilos CSS para el horario del maestro - MEJORADOS
function addScheduleStyles() {
  if (document.getElementById("teacher-schedule-styles")) return

  const style = document.createElement("style")
  style.id = "teacher-schedule-styles"
  style.textContent = `
    .schedule-card {
      background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(16, 185, 129, 0.05));
      border: 2px solid rgba(34, 197, 94, 0.2);
      margin-bottom: 30px;
      position: relative;
      overflow: hidden;
    }
    
    .schedule-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, #22c55e, #10b981, #059669);
    }
    
    .card-header {
      display: flex;
      align-items: center;
      gap: 20px;
      margin-bottom: 25px;
      padding-bottom: 20px;
      border-bottom: 2px solid rgba(34, 197, 94, 0.2);
    }
    
    .header-icon {
      width: 60px;
      height: 60px;
      background: linear-gradient(135deg, #22c55e, #10b981);
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 1.5em;
      box-shadow: 0 8px 25px rgba(34, 197, 94, 0.3);
    }
    
    .header-content {
      flex: 1;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .header-content h3 {
      font-size: 1.5em;
      font-weight: 700;
      background: linear-gradient(135deg, #22c55e, #10b981);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin: 0;
    }
    
    .schedule-stats {
      display: flex;
      gap: 15px;
    }
    
    .stat-badge {
      padding: 8px 16px;
      border-radius: 12px;
      font-weight: 700;
      font-size: 0.9em;
      color: white;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stat-badge.primary {
      background: linear-gradient(135deg, #3b82f6, #2563eb);
    }
    
    .stat-badge.success {
      background: linear-gradient(135deg, #22c55e, #10b981);
    }
    
    .weekly-schedule-teacher {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 25px;
      margin-top: 20px;
    }
    
    .day-schedule-teacher {
      background: rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 20px;
      border: 2px solid transparent;
      transition: all 0.4s ease;
      position: relative;
      overflow: hidden;
    }
    
    .day-schedule-teacher::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, #22c55e, #10b981);
      opacity: 0;
      transition: opacity 0.3s ease;
    }
    
    .day-schedule-teacher.has-classes {
      border-color: rgba(34, 197, 94, 0.3);
      background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(16, 185, 129, 0.05));
    }
    
    .day-schedule-teacher.has-classes::before {
      opacity: 1;
    }
    
    .day-schedule-teacher.no-classes {
      opacity: 0.6;
      border-color: rgba(255, 255, 255, 0.1);
    }
    
    .day-schedule-teacher:hover {
      transform: translateY(-5px);
      box-shadow: 0 15px 40px rgba(34, 197, 94, 0.2);
    }
    
    .day-header-teacher {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
      padding-bottom: 12px;
      border-bottom: 1px solid rgba(34, 197, 94, 0.2);
    }
    
    .day-header-teacher h4 {
      background: linear-gradient(135deg, #22c55e, #10b981);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin: 0;
      font-size: 1.3em;
      font-weight: 700;
    }
    
    .day-count-teacher {
      background: linear-gradient(135deg, #22c55e, #10b981);
      color: white;
      padding: 6px 12px;
      border-radius: 12px;
      font-size: 0.85em;
      font-weight: 700;
      box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
    }
    
    .day-classes-teacher {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    
    .class-item-teacher {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 16px;
      border-left: 4px solid #22c55e;
      cursor: pointer;
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
    }
    
    .class-item-teacher::before {
      content: '';
      position: absolute;
      top: 0;
      right: 0;
      width: 3px;
      height: 100%;
      background: linear-gradient(180deg, #10b981, #059669);
      opacity: 0;
      transition: opacity 0.3s ease;
    }
    
    .class-item-teacher:hover {
      background: rgba(255, 255, 255, 0.15);
      transform: translateX(8px);
      box-shadow: 0 8px 25px rgba(34, 197, 94, 0.25);
      border-left-color: #10b981;
    }
    
    .class-item-teacher:hover::before {
      opacity: 1;
    }
    
    .class-time-teacher {
      display: flex;
      align-items: center;
      gap: 8px;
      background: linear-gradient(135deg, #22c55e, #10b981);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      font-weight: 700;
      font-size: 1em;
      margin-bottom: 10px;
    }
    
    .class-subject-teacher {
      font-weight: 700;
      color: white;
      margin-bottom: 8px;
      font-size: 1.1em;
      line-height: 1.3;
    }
    
    .class-details-teacher {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 8px;
    }
    
    .class-details-teacher span {
      padding: 4px 8px;
      border-radius: 8px;
      font-size: 0.85em;
      font-weight: 600;
      color: white;
    }
    
    .class-code-teacher {
      background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
      box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .class-group-teacher {
      background: linear-gradient(135deg, #f59e0b, #d97706) !important;
      box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
    }
    
    .class-room-teacher {
      background: linear-gradient(135deg, #22c55e, #10b981) !important;
      box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
      display: flex;
      align-items: center;
      gap: 4px;
    }
    
    .class-meta-teacher {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .class-type-teacher {
      background: linear-gradient(135deg, #8b5cf6, #7c3aed);
      color: white;
      padding: 4px 8px;
      border-radius: 8px;
      font-size: 0.8em;
      font-weight: 700;
      box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
    }
    
    .class-credits-teacher {
      color: rgba(255, 255, 255, 0.8);
      font-size: 0.85em;
      font-weight: 600;
      background: rgba(255, 255, 255, 0.1);
      padding: 4px 8px;
      border-radius: 6px;
    }
    
    .no-classes-message-teacher {
      text-align: center;
      color: rgba(255, 255, 255, 0.6);
      font-style: italic;
      padding: 30px;
      font-size: 1em;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 10px;
      border: 1px dashed rgba(255, 255, 255, 0.2);
    }
    
    @media (max-width: 768px) {
      .weekly-schedule-teacher {
        grid-template-columns: 1fr;
      }
      
      .header-content {
        flex-direction: column;
        gap: 15px;
        align-items: flex-start;
      }
      
      .schedule-stats {
        flex-direction: column;
        gap: 8px;
      }
    }
  `
  document.head.appendChild(style)
}

// Cargar materias del maestro
async function loadTeacherSubjects() {
  try {
    const token = localStorage.getItem("teacher_token")
    const response = await fetch("/api/teacher/subjects", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (response.ok) {
      const data = await response.json()
      teacherSubjects = data.subjects
    } else {
      // Usar materias de ejemplo
      loadSampleSubjects()
    }
  } catch (error) {
    console.error("Error cargando materias:", error)
    loadSampleSubjects()
  }

  renderSubjects()
}

// Materias de ejemplo con horarios REALES del TESJI corregidos
function loadSampleSubjects() {
  teacherSubjects = [
    {
      id: 1,
      nombre: "Tópicos Avanzados de Programación",
      codigo: "SCD-1027",
      carrera: "Ingeniería en Sistemas Computacionales",
      semestre: 4,
      grupo: "Grupo N2",
      horario: "Lun 12:00-15:00, Mar 13:00-15:00, Mié 09:00-11:00, Jue 14:00-16:00",
      aula: "N2",
      estudiantes_inscritos: 45,
      creditos: 5,
      maestro: "Víctor David Maya Arce",
    },
    {
      id: 2,
      nombre: "Fundamentos de Base de Datos",
      codigo: "AEF-1031",
      carrera: "Ingeniería en Sistemas Computacionales",
      semestre: 4,
      grupo: "Grupo N1",
      horario: "Lun 15:00-18:00, Jue 11:00-13:00",
      aula: "N1",
      estudiantes_inscritos: 42,
      creditos: 5,
      maestro: "Mtra. Yadira Esther Jiménez Pérez",
    },
  ]
}

// Renderizar materias
function renderSubjects() {
  if (!elements.subjectGrid) return

  elements.subjectGrid.innerHTML = teacherSubjects
    .map(
      (subject) => `
        <div class="subject-card" data-subject-id="${subject.id}" onclick="selectSubject(${subject.id})">
            <div class="subject-name">${subject.nombre}</div>
            <div class="subject-details">
                <strong>${subject.codigo}</strong><br>
                ${subject.grupo} - ${subject.aula}<br>
                <span style="color: #22c55e; font-weight: 600;">${subject.horario}</span><br>
                ${subject.estudiantes_inscritos} estudiantes - ${subject.creditos} créditos<br>
                <small><strong>Maestro:</strong> ${subject.maestro}</small>
            </div>
        </div>
    `,
    )
    .join("")
}

// Seleccionar materia
function selectSubject(subjectId) {
  selectedSubject = teacherSubjects.find((s) => s.id === subjectId)

  if (!selectedSubject) return

  // Actualizar UI
  document.querySelectorAll(".subject-card").forEach((el) => {
    el.classList.remove("selected")
  })
  document.querySelector(`[data-subject-id="${subjectId}"]`).classList.add("selected")

  // Habilitar botón de asistencia
  elements.startAttendanceBtn.disabled = false

  // Cargar asistencias de la materia
  loadSubjectAttendance()

  console.log(`✅ Materia seleccionada: ${selectedSubject.nombre}`)
}

// Cargar asistencias de la materia
async function loadSubjectAttendance() {
  if (!selectedSubject) return

  try {
    const token = localStorage.getItem("teacher_token")
    const response = await fetch(`/api/teacher/attendance/${selectedSubject.id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (response.ok) {
      const data = await response.json()
      currentAttendance = data.attendance
    } else {
      // Usar datos de ejemplo
      loadSampleAttendance()
    }
  } catch (error) {
    console.error("Error cargando asistencias:", error)
    loadSampleAttendance()
  }

  renderAttendance()
  updateStats()
}

// Estudiantes de ejemplo del TESJI (Grupo N2)
function loadSampleAttendance() {
  const sampleStudents = [
    { id: 1, nombre: "Adrian Estudiante Ejemplo", matricula: "202323652", presente: true, hora: "08:05" },
    { id: 2, nombre: "Carlos Hernández Ruiz", matricula: "202323734", presente: true, hora: "08:03" },
    { id: 3, nombre: "Ana Martínez Silva", matricula: "202323768", presente: false, hora: null },
    { id: 4, nombre: "Luis García Pérez", matricula: "202323367", presente: true, hora: "08:07" },
    { id: 5, nombre: "Sofia Rodríguez López", matricula: "202323728", presente: false, hora: null },
    { id: 6, nombre: "Diego Morales Castro", matricula: "202323883", presente: true, hora: "08:02" },
    { id: 7, nombre: "Isabella Torres Vega", matricula: "202323830", presente: true, hora: "08:06" },
    { id: 8, nombre: "Alejandro Jiménez Ramos", matricula: "202323377", presente: false, hora: null },
    { id: 9, nombre: "María González López", matricula: "202323352", presente: true, hora: "08:04" },
    { id: 10, nombre: "José Luis Martínez", matricula: "202323737", presente: true, hora: "08:08" },
    { id: 11, nombre: "Carmen Flores Vega", matricula: "202323458", presente: false, hora: null },
    { id: 12, nombre: "Roberto Silva Castro", matricula: "202323762", presente: true, hora: "08:01" },
    { id: 13, nombre: "Fernanda López Ruiz", matricula: "202323355", presente: true, hora: "08:09" },
    { id: 14, nombre: "Miguel Ángel Torres", matricula: "202323750", presente: false, hora: null },
    { id: 15, nombre: "Paola Hernández Silva", matricula: "202323315", presente: true, hora: "08:03" },
  ]

  currentAttendance = sampleStudents
}

// Renderizar asistencias
function renderAttendance() {
  if (!currentAttendance.length) {
    elements.attendanceStatus.style.display = "block"
    elements.attendanceStatus.textContent = "No hay asistencias registradas para esta materia"
    elements.attendanceList.style.display = "none"
    return
  }

  elements.attendanceStatus.style.display = "none"
  elements.attendanceList.style.display = "block"

  elements.attendanceList.innerHTML = currentAttendance
    .map(
      (student) => `
        <div class="attendance-item">
            <div class="student-info">
                <div class="student-name">${student.nombre}</div>
                <div class="student-details">
                    ${student.matricula} ${student.hora ? `- Llegó: ${student.hora}` : ""}
                </div>
            </div>
            <div class="attendance-status ${student.presente ? "status-present" : "status-absent"}">
                ${student.presente ? "Presente" : "Ausente"}
            </div>
        </div>
    `,
    )
    .join("")
}

// Actualizar estadísticas
function updateStats() {
  const total = currentAttendance.length
  const present = currentAttendance.filter((s) => s.presente).length
  const absent = total - present
  const percentage = total > 0 ? Math.round((present / total) * 100) : 0

  elements.totalStudents.textContent = total
  elements.presentStudents.textContent = present
  elements.absentStudents.textContent = absent
  elements.attendancePercentage.textContent = `${percentage}%`
}

// Verificar nuevas asistencias - MEJORADO
async function checkForNewAttendance() {
  if (!attendanceActive || !selectedSubject) return

  try {
    const response = await fetch("/api/rfid/last")
    const data = await response.json()

    if (data && data.uid && data.exists && data.user && data.user.rol === "student") {
      // Verificar si el estudiante ya está en la lista
      const existingStudent = currentAttendance.find((s) => s.matricula === data.user.matricula)

      if (existingStudent && !existingStudent.presente) {
        // Marcar como presente
        existingStudent.presente = true
        existingStudent.hora = new Date().toLocaleTimeString("es-ES", {
          hour: "2-digit",
          minute: "2-digit",
        })

        renderAttendance()
        updateStats()

        console.log(`✅ Asistencia registrada: ${data.user.nombre}`)

        // Mostrar notificación visual
        showAttendanceNotification(data.user.nombre, "success")

        // Reproducir sonido de confirmación (opcional)
        playNotificationSound()
      }
    }
  } catch (error) {
    console.error("Error verificando asistencias:", error)
  }
}

// Reproducir sonido de notificación
function playNotificationSound() {
  try {
    // Crear un sonido simple usando Web Audio API
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)

    oscillator.frequency.setValueAtTime(800, audioContext.currentTime)
    oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1)

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3)

    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + 0.3)
  } catch (error) {
    console.log("No se pudo reproducir sonido:", error)
  }
}

// Iniciar polling para asistencias en tiempo real - MEJORADO
function startAttendancePolling() {
  if (attendanceActive && selectedSubject) {
    // Verificar cada 2 segundos cuando está activo
    setInterval(checkForNewAttendance, 2000)
    console.log("📡 Polling de asistencias iniciado")
  }
}

// Función mejorada para iniciar asistencia
async function startAttendance() {
  if (!selectedSubject) {
    showError("Selecciona una materia primero")
    return
  }

  attendanceActive = !attendanceActive

  if (attendanceActive) {
    try {
      // Llamar al API para iniciar sesión
      const token = localStorage.getItem("teacher_token")
      const response = await fetch("/api/teacher/attendance/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          subject_id: selectedSubject.id,
          subject_name: selectedSubject.nombre,
        }),
      })

      const result = await response.json()

      if (result.success) {
        elements.startAttendanceBtn.innerHTML = '<i class="fas fa-stop"></i> Detener Pase de Lista'
        elements.startAttendanceBtn.className = "btn btn-danger"

        showSuccessMessage(
          `✅ Pase de lista iniciado para ${selectedSubject.nombre}\n\nLos estudiantes pueden pasar su tarjeta RFID para registrar asistencia.`,
        )

        // Iniciar monitoreo de asistencias en tiempo real
        startAttendancePolling()
        console.log("📝 Pase de lista activo para:", selectedSubject.nombre)
      } else {
        throw new Error(result.message || "Error iniciando pase de lista")
      }
    } catch (error) {
      console.error("Error iniciando pase de lista:", error)
      attendanceActive = false
      showError("Error al iniciar el pase de lista: " + error.message)
    }
  } else {
    try {
      // Llamar al API para detener sesión
      const token = localStorage.getItem("teacher_token")
      const response = await fetch("/api/teacher/attendance/stop", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          subject_id: selectedSubject.id,
        }),
      })

      const result = await response.json()

      if (result.success) {
        elements.startAttendanceBtn.innerHTML = '<i class="fas fa-play"></i> Iniciar Pase de Lista'
        elements.startAttendanceBtn.className = "btn btn-primary"

        showSuccessMessage("⏹️ Pase de lista detenido")
        console.log("⏹️ Pase de lista detenido")
      }
    } catch (error) {
      console.error("Error deteniendo pase de lista:", error)
      showError("Error al detener el pase de lista")
    }
  }
}

// Función para mostrar mensajes de éxito
function showSuccessMessage(message) {
  // Crear modal o usar alert mejorado
  const notification = document.createElement("div")
  notification.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: linear-gradient(135deg, #22c55e, #10b981);
    color: white;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 15px 50px rgba(34, 197, 94, 0.4);
    z-index: 2000;
    max-width: 400px;
    text-align: center;
    font-weight: 600;
    animation: modalSlideIn 0.3s ease;
  `

  notification.innerHTML = `
    <i class="fas fa-check-circle" style="font-size: 2em; margin-bottom: 15px;"></i>
    <div style="white-space: pre-line;">${message}</div>
    <button onclick="this.parentElement.remove()" style="
      margin-top: 20px;
      background: rgba(255,255,255,0.2);
      border: none;
      color: white;
      padding: 10px 20px;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
    ">Cerrar</button>
  `

  document.body.appendChild(notification)

  // Auto-cerrar después de 5 segundos
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove()
    }
  }, 5000)
}

// Función mejorada para exportar asistencias
async function exportAttendance() {
  if (!selectedSubject || !currentAttendance.length) {
    showError("No hay datos de asistencia para exportar")
    return
  }

  try {
    // Preparar datos más detallados
    const exportData = currentAttendance.map((student) => ({
      "Nombre Completo": student.nombre,
      Matrícula: student.matricula,
      Estado: student.presente ? "Presente" : "Ausente",
      "Hora de Llegada": student.hora || "N/A",
      Materia: selectedSubject.nombre,
      Código: selectedSubject.codigo,
      Grupo: selectedSubject.grupo,
      Fecha: new Date().toLocaleDateString("es-ES"),
      "Hora de Clase": new Date().toLocaleTimeString("es-ES"),
      Maestro: currentTeacher.nombre,
    }))

    // Crear CSV con BOM para caracteres especiales
    const BOM = "\uFEFF"
    const headers = Object.keys(exportData[0])
    const csvContent =
      BOM +
      [headers.join(","), ...exportData.map((row) => headers.map((header) => `"${row[header]}"`).join(","))].join("\n")

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
    const link = document.createElement("a")

    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob)
      link.setAttribute("href", url)
      link.setAttribute(
        "download",
        `asistencia_${selectedSubject.nombre.replace(/\s+/g, "_")}_${new Date().toISOString().split("T")[0]}.csv`,
      )
      link.style.visibility = "hidden"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      showSuccessMessage("📄 Archivo de asistencia exportado exitosamente")
    }
  } catch (error) {
    console.error("Error exportando asistencia:", error)
    showError("Error al exportar el archivo: " + error.message)
  }
}

// Función para generar reporte detallado
async function generateDetailedReport() {
  if (!selectedSubject) {
    showError("Selecciona una materia primero")
    return
  }

  try {
    const reportData = {
      materia: selectedSubject.nombre,
      codigo: selectedSubject.codigo,
      grupo: selectedSubject.grupo,
      maestro: currentTeacher.nombre,
      fecha: new Date().toLocaleDateString("es-ES"),
      hora: new Date().toLocaleTimeString("es-ES"),
      estadisticas: {
        total_estudiantes: currentAttendance.length,
        presentes: currentAttendance.filter((s) => s.presente).length,
        ausentes: currentAttendance.filter((s) => s.presente === false).length,
        porcentaje_asistencia: Math.round(
          (currentAttendance.filter((s) => s.presente).length / currentAttendance.length) * 100,
        ),
      },
      estudiantes: currentAttendance,
    }

    // Crear reporte HTML para imprimir
    const reportWindow = window.open("", "_blank")
    reportWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Reporte de Asistencia - ${selectedSubject.nombre}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .header { text-align: center; margin-bottom: 30px; }
          .stats { display: flex; justify-content: space-around; margin: 20px 0; }
          .stat-box { text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
          table { width: 100%; border-collapse: collapse; margin-top: 20px; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background-color: #f2f2f2; }
          .presente { color: green; font-weight: bold; }
          .ausente { color: red; font-weight: bold; }
          @media print { .no-print { display: none; } }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>TECNOLÓGICO DE ESTUDIOS SUPERIORES DE JILOTEPEC</h1>
          <h2>Reporte de Asistencia</h2>
          <p><strong>Materia:</strong> ${reportData.materia} (${reportData.codigo})</p>
          <p><strong>Grupo:</strong> ${reportData.grupo} | <strong>Maestro:</strong> ${reportData.maestro}</p>
          <p><strong>Fecha:</strong> ${reportData.fecha} | <strong>Hora:</strong> ${reportData.hora}</p>
        </div>
        
        <div class="stats">
          <div class="stat-box">
            <h3>${reportData.estadisticas.total_estudiantes}</h3>
            <p>Total Estudiantes</p>
          </div>
          <div class="stat-box">
            <h3>${reportData.estadisticas.presentes}</h3>
            <p>Presentes</p>
          </div>
          <div class="stat-box">
            <h3>${reportData.estadisticas.ausentes}</h3>
            <p>Ausentes</p>
          </div>
          <div class="stat-box">
            <h3>${reportData.estadisticas.porcentaje_asistencia}%</h3>
            <p>Asistencia</p>
          </div>
        </div>
        
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Nombre</th>
              <th>Matrícula</th>
              <th>Estado</th>
              <th>Hora de Llegada</th>
            </tr>
          </thead>
          <tbody>
            ${reportData.estudiantes
              .map(
                (student, index) => `
              <tr>
                <td>${index + 1}</td>
                <td>${student.nombre}</td>
                <td>${student.matricula}</td>
                <td class="${student.presente ? "presente" : "ausente"}">
                  ${student.presente ? "PRESENTE" : "AUSENTE"}
                </td>
                <td>${student.hora || "N/A"}</td>
              </tr>
            `,
              )
              .join("")}
          </tbody>
        </table>
        
        <div class="no-print" style="margin-top: 30px; text-align: center;">
          <button onclick="window.print()" style="padding: 10px 20px; font-size: 16px; margin-right: 10px;">
            Imprimir Reporte
          </button>
          <button onclick="window.close()" style="padding: 10px 20px; font-size: 16px;">
            Cerrar
          </button>
        </div>
      </body>
      </html>
    `)
    reportWindow.document.close()

    console.log("📊 Reporte detallado generado")
  } catch (error) {
    console.error("Error generando reporte:", error)
    showError("Error al generar el reporte: " + error.message)
  }
}

// Función para mostrar notificaciones visuales
function showAttendanceNotification(studentName, type = "success") {
  const notification = document.createElement("div")
  notification.classList.add("attendance-notification", type)
  notification.textContent = `¡Asistencia registrada para ${studentName}!`

  document.body.appendChild(notification)

  // Eliminar la notificación después de unos segundos
  setTimeout(() => {
    notification.remove()
  }, 3000)
}

// Función para ver reportes (placeholder)
function viewReports() {
  alert("Función para ver reportes en desarrollo...")
}

// Agregar funciones globales
window.startAttendance = startAttendance
window.exportAttendance = exportAttendance
window.generateDetailedReport = generateDetailedReport
window.viewReports = viewReports

// Agregar estilos para animaciones de modal
const modalStyles = document.createElement("style")
modalStyles.textContent = `
  @keyframes modalSlideIn {
    from {
      transform: translate(-50%, -50%) scale(0.8);
      opacity: 0;
    }
    to {
      transform: translate(-50%, -50%) scale(1);
      opacity: 1;
    }
  }
`
document.head.appendChild(modalStyles)

console.log("✅ Panel del maestro cargado completamente")
