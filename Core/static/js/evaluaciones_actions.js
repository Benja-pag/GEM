// Funciones para manejar el flujo completo de evaluaciones
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const btnGenerarEvaluacionBase = document.getElementById('btn-generar-evaluacion-base');
    const listaEvaluacionesBase = document.getElementById('lista-evaluaciones-base');
    const listaEvaluacionesCreadas = document.getElementById('lista-evaluaciones-creadas');
    const tablaNotas = document.getElementById('tabla-notas');
    
    // Modales
    const modalEvaluacionBase = document.getElementById('modalEvaluacionBase');
    const modalEvaluacionEspecifica = document.getElementById('modalEvaluacionEspecifica');
    const modalEvaluacionesEstudiantes = document.getElementById('modalEvaluacionesEstudiantes');
    
    // Botones de modales
    const btnGuardarEvaluacionBase = document.getElementById('btnGuardarEvaluacionBase');
    const btnGuardarEvaluacionEspecifica = document.getElementById('btnGuardarEvaluacionEspecifica');
    const btnCrearEvaluacionesEstudiantes = document.getElementById('btnCrearEvaluacionesEstudiantes');
    
    // Formularios
    const formEvaluacionBase = document.getElementById('formEvaluacionBase');
    const formEvaluacionEspecifica = document.getElementById('formEvaluacionEspecifica');
    
    // Campos de formularios
    const nombreEvaluacion = document.getElementById('nombreEvaluacion');
    const descripcionEvaluacion = document.getElementById('descripcionEvaluacion');
    const ponderacionEvaluacion = document.getElementById('ponderacionEvaluacion');
    const evaluacionBaseSelect = document.getElementById('evaluacionBaseSelect');
    const claseSelect = document.getElementById('claseSelect');
    const fechaEvaluacion = document.getElementById('fechaEvaluacion');
    const observacionesEvaluacion = document.getElementById('observacionesEvaluacion');
    
    // Configuración para las peticiones fetch
    const fetchConfig = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    };
    
    // Variables globales
    let asignaturaId = null;
    let evaluacionSeleccionada = null;
    let evaluacionesBaseData = [];
    let clasesData = [];
    let asignaturaInfo = null;
    
    // Inicialización
    function inicializar() {
        // Verificar que estamos en la página correcta
        if (!document.getElementById('notas-tab')) {
            console.log('No estamos en la página de notas, saliendo...');
            return;
        }
        
        // Obtener el ID de la asignatura desde la URL
        const urlParts = window.location.pathname.split('/');
        asignaturaId = urlParts[urlParts.length - 2];
        
        // Cargar datos iniciales
        cargarEvaluaciones();
        cargarInfoAsignatura();
        
        // Configurar event listeners
        configurarEventListeners();
        configurarSubpestanasNotas();
    }
    
    // Configurar event listeners
    function configurarEventListeners() {
        // Botón para generar evaluación base
        if (btnGenerarEvaluacionBase) {
            btnGenerarEvaluacionBase.addEventListener('click', abrirModalEvaluacionBase);
        }
        
        // Botón para guardar evaluación base
        if (btnGuardarEvaluacionBase) {
            btnGuardarEvaluacionBase.addEventListener('click', guardarEvaluacionBase);
        }
        
        // Botón para guardar evaluación específica
        if (btnGuardarEvaluacionEspecifica) {
            btnGuardarEvaluacionEspecifica.addEventListener('click', guardarEvaluacionEspecifica);
        }
        
        // Botón para crear evaluaciones de estudiantes
        if (btnCrearEvaluacionesEstudiantes) {
            btnCrearEvaluacionesEstudiantes.addEventListener('click', crearEvaluacionesEstudiantes);
        }
        
        // Event listeners para modales
        if (modalEvaluacionEspecifica) {
            modalEvaluacionEspecifica.addEventListener('show.bs.modal', cargarDatosEvaluacionEspecifica);
            modalEvaluacionEspecifica.addEventListener('hidden.bs.modal', limpiarModalEvaluacionEspecifica);
        }
        
        if (modalEvaluacionesEstudiantes) {
            modalEvaluacionesEstudiantes.addEventListener('show.bs.modal', cargarInfoEvaluacionEstudiantes);
        }
    }
    
    // Configurar event listeners para las subpestañas de notas
    function configurarSubpestanasNotas() {
        // Event listener para la pestaña de evaluaciones base
        const evaluacionesBaseTab = document.getElementById('evaluaciones-base-tab');
        if (evaluacionesBaseTab) {
            evaluacionesBaseTab.addEventListener('shown.bs.tab', function() {
                console.log('Pestaña Evaluaciones Base activada');
            });
        }
        
        // Event listener para la pestaña de evaluaciones creadas
        const evaluacionesCreadasTab = document.getElementById('evaluaciones-creadas-tab');
        if (evaluacionesCreadasTab) {
            evaluacionesCreadasTab.addEventListener('shown.bs.tab', function() {
                console.log('Pestaña Evaluaciones Creadas activada');
            });
        }
        
        // Event listener para la pestaña de notas de alumnos
        const notasAlumnosTab = document.getElementById('notas-alumnos-tab');
        if (notasAlumnosTab) {
            notasAlumnosTab.addEventListener('shown.bs.tab', function() {
                console.log('Pestaña Notas de Alumnos activada');
            });
        }
    }
    
    // Cargar información de la asignatura
    function cargarInfoAsignatura() {
        // Obtener información de la asignatura desde el DOM
        const asignaturaNombre = document.getElementById('asignatura-nombre');
        const asignaturaCodigo = document.getElementById('asignatura-codigo');
        const docenteNombre = document.getElementById('asignatura-docente');
        
        if (asignaturaNombre && asignaturaCodigo && docenteNombre) {
            asignaturaInfo = {
                nombre: asignaturaNombre.textContent.trim(),
                codigo: asignaturaCodigo.textContent.trim(),
                docente: docenteNombre.textContent.replace('Prof.', '').replace('Prof', '').trim()
            };
            console.log('Información de asignatura cargada:', asignaturaInfo);
        } else {
            console.error('No se pudieron obtener todos los elementos de información de la asignatura');
            console.log('Elementos encontrados:', {
                nombre: asignaturaNombre,
                codigo: asignaturaCodigo,
                docente: docenteNombre
            });
        }
    }
    
    // Abrir modal de evaluación base
    function abrirModalEvaluacionBase() {
        if (!modalEvaluacionBase || !formEvaluacionBase) {
            console.error('Modal o formulario no encontrado');
            return;
        }
        
        // Limpiar formulario
        formEvaluacionBase.reset();
        
        // Mostrar modal
        const modal = new bootstrap.Modal(modalEvaluacionBase);
        modal.show();
    }
    
    // Guardar evaluación base
    function guardarEvaluacionBase() {
        const nombre = nombreEvaluacion.value.trim();
        const descripcion = descripcionEvaluacion.value.trim();
        const ponderacion = ponderacionEvaluacion.value;
        
        // Validaciones
        if (!nombre) {
            mostrarMensaje('El nombre de la evaluación es obligatorio', 'error');
            return;
        }
        
        if (!ponderacion || ponderacion <= 0 || ponderacion > 100) {
            mostrarMensaje('La ponderación debe estar entre 1 y 100', 'error');
            return;
        }
        
        // Enviar petición
        fetch(`/api/evaluacion-base/${asignaturaId}/generar/`, {
            ...fetchConfig,
            method: 'POST',
            body: JSON.stringify({
                nombre: nombre,
                descripcion: descripcion,
                ponderacion: ponderacion
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarMensaje('Evaluación base creada correctamente', 'success');
                
                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(modalEvaluacionBase);
                modal.hide();
                
                // Recargar evaluaciones
                cargarEvaluaciones();
            } else {
                mostrarMensaje(data.error || 'Error al crear la evaluación base', 'error');
            }
        })
        .catch(error => {
            mostrarMensaje('Error al crear la evaluación base', 'error');
            console.error('Error:', error);
        });
    }
    
    // Cargar evaluaciones de la asignatura
    function cargarEvaluaciones() {
        try {
            fetch(`/api/asignatura/${asignaturaId}/evaluaciones/`, {
                ...fetchConfig,
                method: 'GET'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    evaluacionesBaseData = data.evaluaciones_base || [];
                    const evaluaciones = data.evaluaciones || [];
                    
                    // Renderizar evaluaciones base
                    renderizarEvaluacionesBase(evaluacionesBaseData);
                    
                    // Renderizar evaluaciones creadas
                    renderizarEvaluacionesCreadas(evaluaciones);
                } else {
                    console.error('Error al cargar evaluaciones:', data.error);
                    mostrarMensaje('Error al cargar las evaluaciones', 'error');
                }
            })
            .catch(error => {
                console.error('Error en la petición:', error);
                mostrarMensaje('Error al cargar las evaluaciones', 'error');
            });
        } catch (error) {
            console.error('Error en cargarEvaluaciones:', error);
            mostrarMensaje('Error al cargar las evaluaciones', 'error');
        }
    }
    
    // Renderizar evaluaciones base
    function renderizarEvaluacionesBase(evaluacionesBase) {
        if (!listaEvaluacionesBase) return;
        
        if (evaluacionesBase.length === 0) {
            listaEvaluacionesBase.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No hay evaluaciones base disponibles</p>
                    <button class="btn btn-primary btn-sm" onclick="document.getElementById('btn-generar-evaluacion-base').click()">
                        <i class="fas fa-plus me-2"></i>Crear Primera Evaluación Base
                    </button>
                </div>
            `;
            return;
        }
        
        let html = '';
        evaluacionesBase.forEach(evaluacion => {
            html += `
                <div class="card mb-3 border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h6 class="card-title mb-1">${evaluacion.nombre}</h6>
                                <p class="card-text text-muted mb-2">${evaluacion.descripcion || 'Sin descripción'}</p>
                                <div class="d-flex align-items-center gap-3">
                                    <span class="badge bg-primary">${evaluacion.ponderacion}%</span>
                                    <small class="text-muted">
                                        <i class="fas fa-calendar me-1"></i>
                                        Creada: ${new Date(evaluacion.fecha_creacion).toLocaleDateString()}
                                    </small>
                                </div>
                            </div>
                            <div class="d-flex flex-column gap-2">
                                <button class="btn btn-success btn-sm" 
                                        onclick="crearEvaluacionEspecifica(${evaluacion.id})"
                                        title="Crear evaluación específica">
                                    <i class="fas fa-plus me-1"></i>Crear Evaluación
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        listaEvaluacionesBase.innerHTML = html;
    }
    
    // Renderizar evaluaciones creadas
    function renderizarEvaluacionesCreadas(evaluaciones) {
        if (!listaEvaluacionesCreadas) return;
        
        if (evaluaciones.length === 0) {
            listaEvaluacionesCreadas.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-calendar-check fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No hay evaluaciones específicas creadas</p>
                    <small class="text-muted">Crea evaluaciones desde las evaluaciones base</small>
                </div>
            `;
            return;
        }
        
        let html = '';
        evaluaciones.forEach(evaluacion => {
            const fecha = new Date(evaluacion.fecha).toLocaleDateString();
            const cursoStr = evaluacion.clase__curso__nivel && evaluacion.clase__curso__letra 
                ? `${evaluacion.clase__curso__nivel}°${evaluacion.clase__curso__letra}` 
                : 'Electivo';
            
            html += `
                <div class="card mb-3 border-0 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h6 class="card-title mb-1">${evaluacion.evaluacion_base__nombre}</h6>
                                <p class="card-text text-muted mb-2">Sin descripción</p>
                                <div class="d-flex align-items-center gap-3 mb-2">
                                    <span class="badge bg-primary">${evaluacion.evaluacion_base__ponderacion}%</span>
                                    <span class="badge bg-info">${cursoStr}</span>
                                    <small class="text-muted">
                                        <i class="fas fa-calendar me-1"></i>${fecha}
                                    </small>
                                </div>
                                <div class="d-flex align-items-center gap-3">
                                    <small class="text-muted">
                                        <i class="fas fa-sticky-note me-1"></i>${evaluacion.observaciones || 'Sin observaciones'}
                                    </small>
                                </div>
                            </div>
                            <div class="d-flex flex-column gap-2">
                                <button class="btn btn-warning btn-sm" 
                                        onclick="colocarNota(${evaluacion.id})"
                                        title="Colocar notas">
                                    <i class="fas fa-edit me-1"></i>Colocar Nota
                                </button>
                                <button class="btn btn-info btn-sm" 
                                        onclick="verNotas(${evaluacion.id})"
                                        title="Ver notas">
                                    <i class="fas fa-eye me-1"></i>Ver Notas
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        listaEvaluacionesCreadas.innerHTML = html;
    }
    
    // Función global para crear evaluación específica
    window.crearEvaluacionEspecifica = function(evaluacionBaseId) {
        const evaluacionBase = evaluacionesBaseData.find(eb => eb.id === evaluacionBaseId);
        if (!evaluacionBase) {
            mostrarMensaje('Evaluación base no encontrada', 'error');
            return;
        }
        
        // Mostrar modal de evaluación específica
        if (modalEvaluacionEspecifica) {
            // Establecer la evaluación base seleccionada
            evaluacionSeleccionada = evaluacionBase;
            
            // Mostrar modal
            const modal = new bootstrap.Modal(modalEvaluacionEspecifica);
            modal.show();
        }
    };
    
    // Función global para colocar nota
    window.colocarNota = function(evaluacionId) {
        // Cambiar a la pestaña de notas de alumnos
        const notasAlumnosTab = document.getElementById('notas-alumnos-tab');
        if (notasAlumnosTab) {
            const tab = new bootstrap.Tab(notasAlumnosTab);
            tab.show();
        }
        
        // Cargar las notas de la evaluación
        cargarNotas(evaluacionId);
    };
    
    // Función global para ver notas
    window.verNotas = function(evaluacionId) {
        // Cambiar a la pestaña de notas de alumnos
        const notasAlumnosTab = document.getElementById('notas-alumnos-tab');
        if (notasAlumnosTab) {
            const tab = new bootstrap.Tab(notasAlumnosTab);
            tab.show();
        }
        
        // Cargar las notas de la evaluación
        cargarNotas(evaluacionId);
    };
    
    // Cargar datos para evaluación específica
    function cargarDatosEvaluacionEspecifica() {
        if (!evaluacionSeleccionada) return;
        
        // Mostrar información de la evaluación base
        const evaluacionBaseInfo = document.getElementById('evaluacionBaseInfo');
        if (evaluacionBaseInfo) {
            evaluacionBaseInfo.innerHTML = `
                <div class="alert alert-info">
                    <h6 class="alert-heading">${evaluacionSeleccionada.nombre}</h6>
                    <p class="mb-1">${evaluacionSeleccionada.descripcion || 'Sin descripción'}</p>
                    <small>Ponderación: ${evaluacionSeleccionada.ponderacion}%</small>
                </div>
            `;
        }
        
        // Mostrar información de la asignatura
        const asignaturaInfoElement = document.getElementById('asignaturaInfo');
        if (asignaturaInfoElement && asignaturaInfo) {
            asignaturaInfoElement.innerHTML = `
                <div class="alert alert-success">
                    <h6 class="alert-heading">${asignaturaInfo.nombre}</h6>
                    <p class="mb-1">Código: ${asignaturaInfo.codigo}</p>
                    <small>Docente: ${asignaturaInfo.docente}</small>
                </div>
            `;
        }
        
        // Cargar clases disponibles
        cargarClases();
    }
    
    // Limpiar modal de evaluación específica
    function limpiarModalEvaluacionEspecifica() {
        evaluacionSeleccionada = null;
        
        if (formEvaluacionEspecifica) {
            formEvaluacionEspecifica.reset();
        }
        
        if (claseSelect) {
            claseSelect.innerHTML = '<option value="">Selecciona una clase...</option>';
        }
        
        if (fechaEvaluacion) {
            fechaEvaluacion.value = '';
        }
        
        if (observacionesEvaluacion) {
            observacionesEvaluacion.value = '';
        }
    }
    
    // Cargar clases disponibles con lógica de bloques pares/impares
    function cargarClases() {
        if (!asignaturaId) return;
        
        fetch(`/api/asignatura/${asignaturaId}/clases/`, {
            ...fetchConfig,
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                clasesData = data.clases || [];
                
                // Agrupar clases por bloques pares/impares
                const clasesAgrupadas = agruparClasesPorBloques(clasesData);
                
                // Renderizar opciones en el select
                renderizarOpcionesClases(clasesAgrupadas);
            } else {
                console.error('Error al cargar clases:', data.error);
                mostrarMensaje('Error al cargar las clases disponibles', 'error');
            }
        })
        .catch(error => {
            console.error('Error en la petición:', error);
            mostrarMensaje('Error al cargar las clases disponibles', 'error');
        });
    }
    
    // Agrupar clases por bloques pares/impares
    function agruparClasesPorBloques(clases) {
        const grupos = {};
        
        clases.forEach(clase => {
            // Extraer el número del horario (ej: "1-2" -> 1, "3-4" -> 3)
            const horarioMatch = clase.horario.match(/^(\d+)/);
            if (horarioMatch) {
                const numeroBloque = parseInt(horarioMatch[1]);
                const esPar = numeroBloque % 2 === 0;
                const grupo = esPar ? 'pares' : 'impares';
                
                if (!grupos[grupo]) {
                    grupos[grupo] = [];
                }
                grupos[grupo].push(clase);
            }
        });
        
        return grupos;
    }
    
    // Renderizar opciones de clases agrupadas
    function renderizarOpcionesClases(clasesAgrupadas) {
        if (!claseSelect) return;
        
        let html = '<option value="">Selecciona una clase...</option>';
        
        // Agregar opciones para bloques pares
        if (clasesAgrupadas.pares && clasesAgrupadas.pares.length > 0) {
            html += '<optgroup label="Bloques Pares (2-4, 6-8, etc.)">';
            clasesAgrupadas.pares.forEach(clase => {
                html += `<option value="${clase.id}" data-fecha="${clase.dia}">${clase.descripcion}</option>`;
            });
            html += '</optgroup>';
        }
        
        // Agregar opciones para bloques impares
        if (clasesAgrupadas.impares && clasesAgrupadas.impares.length > 0) {
            html += '<optgroup label="Bloques Impares (1-2, 3-4, etc.)">';
            clasesAgrupadas.impares.forEach(clase => {
                html += `<option value="${clase.id}" data-fecha="${clase.dia}">${clase.descripcion}</option>`;
            });
            html += '</optgroup>';
        }
        
        claseSelect.innerHTML = html;
    }
    
    // Guardar evaluación específica
    function guardarEvaluacionEspecifica() {
        if (!evaluacionSeleccionada) {
            mostrarMensaje('No hay evaluación base seleccionada', 'error');
            return;
        }
        
        const claseId = claseSelect.value;
        const fecha = fechaEvaluacion.value;
        const observaciones = observacionesEvaluacion.value.trim();
        
        // Validaciones
        if (!claseId) {
            mostrarMensaje('Debes seleccionar una clase', 'error');
            return;
        }
        
        if (!fecha) {
            mostrarMensaje('La fecha es obligatoria', 'error');
            return;
        }
        
        // Enviar petición
        fetch('/api/evaluacion-especifica/crear/', {
            ...fetchConfig,
            method: 'POST',
            body: JSON.stringify({
                evaluacion_base_id: evaluacionSeleccionada.id,
                clase_id: claseId,
                fecha: fecha,
                observaciones: observaciones
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarMensaje('Evaluación específica creada correctamente', 'success');
                
                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(modalEvaluacionEspecifica);
                modal.hide();
                
                // Recargar evaluaciones
                cargarEvaluaciones();
            } else {
                mostrarMensaje(data.error || 'Error al crear la evaluación específica', 'error');
            }
        })
        .catch(error => {
            mostrarMensaje('Error al crear la evaluación específica', 'error');
            console.error('Error:', error);
        });
    }
    
    // Cargar información de evaluación para estudiantes
    function cargarInfoEvaluacionEstudiantes() {
        // Esta función se puede implementar si es necesario
        console.log('Cargando información de evaluación para estudiantes');
    }
    
    // Crear evaluaciones de estudiantes
    function crearEvaluacionesEstudiantes() {
        // Esta función se puede implementar si es necesario
        console.log('Creando evaluaciones de estudiantes');
    }
    
    // Cargar notas de una evaluación
    function cargarNotas(evaluacionId) {
        if (!evaluacionId) return;
        
        fetch(`/api/evaluacion/${evaluacionId}/notas/`, {
            ...fetchConfig,
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderizarTablaNotas(data.notas, evaluacionId);
            } else {
                console.error('Error al cargar notas:', data.error);
                mostrarMensaje('Error al cargar las notas', 'error');
            }
        })
        .catch(error => {
            console.error('Error en la petición:', error);
            mostrarMensaje('Error al cargar las notas', 'error');
        });
    }
    
    // Renderizar tabla de notas
    function renderizarTablaNotas(notas, evaluacionId) {
        if (!tablaNotas) return;
        
        if (!notas || notas.length === 0) {
            tablaNotas.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No hay notas registradas para esta evaluación</p>
                    <button class="btn btn-primary btn-sm" onclick="crearNotasEstudiantes(${evaluacionId})">
                        <i class="fas fa-plus me-2"></i>Crear Notas
                    </button>
                </div>
            `;
            return;
        }
        
        let html = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th>Estudiante</th>
                            <th>Nota</th>
                            <th>Observaciones</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        notas.forEach(nota => {
            html += `
                <tr data-nota-id="${nota.id}">
                    <td>
                        <div class="d-flex align-items-center">
                            <div class="student-avatar me-2">
                                ${nota.estudiante_nombre.charAt(0).toUpperCase()}
                            </div>
                            <span>${nota.estudiante_nombre}</span>
                        </div>
                    </td>
                    <td>
                        <span class="nota-display">${nota.nota}</span>
                        <input type="number" 
                               class="form-control nota-input d-none" 
                               value="${nota.nota}" 
                               min="1.0" 
                               max="7.0" 
                               step="0.1">
                    </td>
                    <td>
                        <span class="observaciones-display">${nota.observaciones || ''}</span>
                        <textarea class="form-control observaciones-input d-none" 
                                  rows="2">${nota.observaciones || ''}</textarea>
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary btn-edit" 
                                    onclick="iniciarEdicion(this)">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-success btn-save d-none" 
                                    onclick="guardarNota(this)">
                                <i class="fas fa-save"></i>
                            </button>
                            <button class="btn btn-outline-danger btn-delete" 
                                    onclick="eliminarNota(this)">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        tablaNotas.innerHTML = html;
    }
    
    // Función global para iniciar edición
    window.iniciarEdicion = function(btn) {
        const row = btn.closest('tr');
        const notaDisplay = row.querySelector('.nota-display');
        const notaInput = row.querySelector('.nota-input');
        const observacionesDisplay = row.querySelector('.observaciones-display');
        const observacionesInput = row.querySelector('.observaciones-input');
        const btnEdit = row.querySelector('.btn-edit');
        const btnSave = row.querySelector('.btn-save');
        
        // Mostrar campos de edición
        notaDisplay.classList.add('d-none');
        notaInput.classList.remove('d-none');
        observacionesDisplay.classList.add('d-none');
        observacionesInput.classList.remove('d-none');
        
        // Cambiar botones
        btnEdit.classList.add('d-none');
        btnSave.classList.remove('d-none');
        
        // Enfocar en el campo de nota
        notaInput.focus();
    };
    
    // Función global para guardar nota
    window.guardarNota = function(btn) {
        const row = btn.closest('tr');
        const notaId = row.dataset.notaId;
        const notaInput = row.querySelector('.nota-input');
        const observacionesInput = row.querySelector('.observaciones-input');
        const notaDisplay = row.querySelector('.nota-display');
        const observacionesDisplay = row.querySelector('.observaciones-display');
        const btnEdit = row.querySelector('.btn-edit');
        const btnSave = row.querySelector('.btn-save');
        
        const nuevaNota = parseFloat(notaInput.value);
        const observaciones = observacionesInput.value.trim();
        
        // Validaciones
        if (isNaN(nuevaNota) || nuevaNota < 1.0 || nuevaNota > 7.0) {
            mostrarMensaje('La nota debe estar entre 1.0 y 7.0', 'error');
            return;
        }
        
        // Enviar petición
        fetch(`/api/nota/${notaId}/actualizar/`, {
            ...fetchConfig,
            method: 'PUT',
            body: JSON.stringify({
                nota: nuevaNota,
                observaciones: observaciones
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Actualizar display
                notaDisplay.textContent = nuevaNota;
                observacionesDisplay.textContent = observaciones;
                
                // Ocultar campos de edición
                notaDisplay.classList.remove('d-none');
                notaInput.classList.add('d-none');
                observacionesDisplay.classList.remove('d-none');
                observacionesInput.classList.add('d-none');
                
                // Cambiar botones
                btnEdit.classList.remove('d-none');
                btnSave.classList.add('d-none');
                
                mostrarMensaje('Nota actualizada correctamente', 'success');
            } else {
                mostrarMensaje(data.error || 'Error al actualizar la nota', 'error');
            }
        })
        .catch(error => {
            mostrarMensaje('Error al actualizar la nota', 'error');
            console.error('Error:', error);
        });
    };
    
    // Función global para eliminar nota
    window.eliminarNota = function(btn) {
        if (!confirm('¿Estás seguro de que quieres eliminar esta nota?')) {
            return;
        }
        
        const row = btn.closest('tr');
        const notaId = row.dataset.notaId;
        
        fetch(`/api/nota/${notaId}/eliminar/`, {
            ...fetchConfig,
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                row.remove();
                mostrarMensaje('Nota eliminada correctamente', 'success');
            } else {
                mostrarMensaje(data.error || 'Error al eliminar la nota', 'error');
            }
        })
        .catch(error => {
            mostrarMensaje('Error al eliminar la nota', 'error');
            console.error('Error:', error);
        });
    };
    
    // Función global para crear notas de estudiantes
    window.crearNotasEstudiantes = function(evaluacionId) {
        fetch(`/api/evaluacion/${evaluacionId}/estudiantes/crear/`, {
            ...fetchConfig,
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarMensaje(`Se crearon ${data.nuevas_evaluaciones} notas de estudiantes`, 'success');
                cargarNotas(evaluacionId);
            } else {
                mostrarMensaje(data.error || 'Error al crear las notas', 'error');
            }
        })
        .catch(error => {
            mostrarMensaje('Error al crear las notas', 'error');
            console.error('Error:', error);
        });
    };
    
    // Mostrar mensajes usando el sistema GEM
    function mostrarMensaje(mensaje, tipo) {
        if (typeof GEMSystemMessage !== 'undefined') {
            switch (tipo) {
                case 'success':
                    GEMSystemMessage.success(mensaje);
                    break;
                case 'error':
                    GEMSystemMessage.error(mensaje);
                    break;
                case 'info':
                    GEMSystemMessage.info(mensaje);
                    break;
                default:
                    GEMSystemMessage.show(mensaje);
            }
        } else {
            // Fallback si no está disponible el sistema GEM
            alert(mensaje);
        }
    }
    
    // Inicializar cuando el DOM esté listo
    inicializar();
}); 