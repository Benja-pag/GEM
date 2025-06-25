// Calendario del Administrador
let calendarAdmin;
let eventosDataAdmin = [];

// Inicializar calendario del administrador
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado para calendario admin');
    
    // Esperar un poco para que se carguen todos los elementos
    setTimeout(() => {
        const tabCalendario = document.querySelector('#calendario-tab');
        console.log('Tab calendario encontrado:', tabCalendario);
        
        if (tabCalendario) {
            tabCalendario.addEventListener('click', function() {
                console.log('Click en tab calendario');
                setTimeout(() => {
                    if (!calendarAdmin) {
                        console.log('Inicializando calendario después del click');
                        initCalendarAdmin();
                    }
                    // Inicializar listeners de collapse después de cargar el calendario
                    initCollapseListeners();
                }, 200);
            });
        }
        
        // También intentar inicializar si ya estamos en la pestaña
        const calendarioActivo = document.querySelector('#calendario.show');
        if (calendarioActivo) {
            console.log('Calendario ya activo, inicializando');
            initCalendarAdmin();
            initCollapseListeners();
        }
    }, 500);
});

// Función para inicializar los listeners de collapse
function initCollapseListeners() {
    const collapseElements = ['#collapseEventosGenerales', '#collapseEventosCursos', '#collapseEventosElectivos'];
    
    collapseElements.forEach(elementId => {
        const collapseElement = document.querySelector(elementId);
        
        if (collapseElement) {
            collapseElement.addEventListener('show.bs.collapse', function() {
                const header = document.querySelector(`[data-bs-target="${elementId}"]`);
                const icon = header.querySelector('.collapse-icon');
                if (icon) {
                    icon.style.transform = 'rotate(0deg)';
                }
            });
            
            collapseElement.addEventListener('hide.bs.collapse', function() {
                const header = document.querySelector(`[data-bs-target="${elementId}"]`);
                const icon = header.querySelector('.collapse-icon');
                if (icon) {
                    icon.style.transform = 'rotate(-90deg)';
                }
            });
        }
    });
}

function initCalendarAdmin() {
    console.log('Iniciando initCalendarAdmin');
    const calendarEl = document.getElementById('calendarAdmin');
    console.log('Elemento calendario encontrado:', calendarEl);
    
    if (!calendarEl) {
        console.error('No se encontró el elemento del calendario');
        return;
    }

    try {
        // Verificar si hay datos de eventos disponibles globalmente
        if (typeof window.eventosCalendarioAdmin !== 'undefined') {
            eventosDataAdmin = window.eventosCalendarioAdmin;
            console.log('Eventos cargados desde window:', eventosDataAdmin.length);
        } else {
            console.warn('No se encontraron datos de eventos');
            eventosDataAdmin = [];
        }
        
        calendarAdmin = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'es',
            height: 600,
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            buttonText: {
                today: 'Hoy',
                month: 'Mes',
                week: 'Semana',
                day: 'Día'
            },
            dayMaxEvents: 3,
            moreLinkText: 'más',
            eventDisplay: 'block',
            eventTextColor: '#fff',
            eventBorderWidth: 0,
            events: eventosDataAdmin,
            eventDidMount: function(info) {
                // Agregar clases CSS según el tipo de evento
                const event = info.event;
                const tipo = event.extendedProps.type;
                
                if (tipo === 'Colegio') {
                    info.el.classList.add('evento-colegio');
                } else if (tipo === 'Asignatura') {
                    info.el.classList.add('evento-asignatura');
                } else if (event.title.toLowerCase().includes('evaluación') || event.title.toLowerCase().includes('examen')) {
                    info.el.classList.add('evento-evaluacion');
                }
                
                // Agregar tooltip con información adicional
                const tooltip = `
                    <strong>${event.title}</strong><br/>
                    Fecha: ${event.start.toLocaleDateString('es-ES')}<br/>
                    Tipo: ${tipo}<br/>
                    ${event.extendedProps.description ? `Descripción: ${event.extendedProps.description}<br/>` : ''}
                    ${event.extendedProps.ubicacion ? `Ubicación: ${event.extendedProps.ubicacion}<br/>` : ''}
                    ${event.extendedProps.encargado ? `Encargado: ${event.extendedProps.encargado}` : ''}
                    ${event.extendedProps.curso ? `Curso: ${event.extendedProps.curso}` : ''}
                `;
                
                info.el.setAttribute('title', tooltip);
                info.el.setAttribute('data-bs-toggle', 'tooltip');
                info.el.setAttribute('data-bs-html', 'true');
            },
            eventClick: function(info) {
                const event = info.event;
                mostrarDetalleEvento(event);
            },
            dateClick: function(info) {
                // Pre-llenar la fecha en el modal de crear evento
                const fechaInput = document.getElementById('fechaEventoAdmin');
                if (fechaInput) {
                    fechaInput.value = info.dateStr;
                }
                const modal = new bootstrap.Modal(document.getElementById('modalCrearEventoAdmin'));
                modal.show();
            }
        });

        calendarAdmin.render();
        console.log('Calendario renderizado exitosamente');
        
        // Inicializar tooltips de Bootstrap
        setTimeout(() => {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('#calendarAdmin [data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function(tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl, {
                    html: true,
                    placement: 'top'
                });
            });
        }, 100);
        
        // Actualizar paneles laterales
        updateProximosEventosAdmin();
        updateEventosPorCursos();
        updateEventosPorElectivos();
        
    } catch (error) {
        console.error('Error al inicializar el calendario del administrador:', error);
        calendarEl.innerHTML = `
            <div class="alert alert-danger text-center" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error al cargar el calendario. Revisa la consola para más detalles.
            </div>
        `;
    }
}

// Actualizar próximos eventos (solo eventos del colegio)
function updateProximosEventosAdmin() {
    console.log('Actualizando próximos eventos admin...');
    
    const proximosEventosDiv = document.getElementById('proximosEventosAdmin');
    if (!proximosEventosDiv || !eventosDataAdmin) {
        console.log('No se encontró el contenedor o no hay datos');
        return;
    }
    
    const today = new Date();
    
    // Filtrar solo eventos del colegio (tipo "Colegio")
    const eventosGenerales = eventosDataAdmin.filter(evento => 
        evento.extendedProps && evento.extendedProps.type === 'Colegio'
    );
    
    // Ordenar por fecha
    eventosGenerales.sort((a, b) => new Date(a.start) - new Date(b.start));
    
    console.log(`Eventos generales encontrados: ${eventosGenerales.length}`);
    
    if (eventosGenerales.length === 0) {
        proximosEventosDiv.innerHTML = `
            <div class="estado-vacio">
                <i class="fas fa-calendar-times"></i>
                <p>No hay eventos generales</p>
            </div>
        `;
        return;
    }
    
    let eventosHtml = '';
    eventosGenerales.slice(0, 5).forEach(evento => {
        const fechaEvento = new Date(evento.start);
        const fechaFormateada = fechaEvento.toLocaleDateString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
        
        const horaFormateada = fechaEvento.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        eventosHtml += `
            <div class="evento-item evento-colegio">
                <div class="evento-content">
                    <div class="evento-info">
                        <h6>${evento.title}</h6>
                        <div class="text-muted">
                            <span><i class="fas fa-calendar-alt me-1"></i>${fechaFormateada}</span>
                            <span><i class="fas fa-clock me-1"></i>${horaFormateada}</span>
                            ${evento.extendedProps.ubicacion ? `<span><i class="fas fa-map-marker-alt me-1"></i>${evento.extendedProps.ubicacion}</span>` : ''}
                        </div>
                    </div>
                    <div class="evento-actions">
                        <button class="btn btn-evento btn-editar" onclick="editarEvento('${evento.id}')" title="Editar evento">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-evento btn-eliminar" onclick="eliminarEvento('${evento.id}', '${evento.title}')" title="Eliminar evento">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    proximosEventosDiv.innerHTML = eventosHtml;
}

// Actualizar eventos por cursos
function updateEventosPorCursos() {
    console.log('Actualizando eventos por cursos...');
    
    const eventosDiv = document.getElementById('eventosPorCursos');
    if (!eventosDiv || !eventosDataAdmin) {
        return;
    }
    
    // Filtrar eventos de asignaturas que tengan curso
    const eventosAsignaturas = eventosDataAdmin.filter(evento => 
        evento.extendedProps && 
        evento.extendedProps.type === 'Asignatura' && 
        evento.extendedProps.curso
    );
    
    console.log(`Eventos de asignaturas encontrados: ${eventosAsignaturas.length}`);
    
    if (eventosAsignaturas.length === 0) {
        eventosDiv.innerHTML = `
            <div class="estado-vacio">
                <i class="fas fa-chalkboard-teacher"></i>
                <p>No hay eventos de cursos</p>
            </div>
        `;
        return;
    }
    
    // Agrupar por curso
    const eventosPorCurso = {};
    eventosAsignaturas.forEach(evento => {
        const curso = evento.extendedProps.curso;
        if (!eventosPorCurso[curso]) {
            eventosPorCurso[curso] = [];
        }
        eventosPorCurso[curso].push(evento);
    });
    
    // Ordenar cursos alfabéticamente
    const cursosOrdenados = Object.keys(eventosPorCurso).sort();
    
    let cursosHtml = '';
    cursosOrdenados.forEach(curso => {
        const eventos = eventosPorCurso[curso];
        
        cursosHtml += `
            <div class="mb-3">
                <div class="d-flex align-items-center mb-2">
                    <span class="curso-badge me-2">${curso}</span>
                    <small class="text-muted">${eventos.length} evento${eventos.length !== 1 ? 's' : ''}</small>
                </div>
        `;
        
        // Mostrar máximo 3 eventos por curso
        eventos.slice(0, 3).forEach(evento => {
            const fechaEvento = new Date(evento.start);
            const fechaFormateada = fechaEvento.toLocaleDateString('es-ES', {
                day: '2-digit',
                month: '2-digit'
            });
            
            const horaFormateada = fechaEvento.toLocaleTimeString('es-ES', {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            cursosHtml += `
                <div class="evento-item evento-asignatura">
                    <div class="evento-content">
                        <div class="evento-info">
                            <h6>${evento.title}</h6>
                            <div class="text-muted">
                                <span><i class="fas fa-calendar-alt me-1"></i>${fechaFormateada}</span>
                                <span><i class="fas fa-clock me-1"></i>${horaFormateada}</span>
                                ${evento.extendedProps.ubicacion ? `<span><i class="fas fa-map-marker-alt me-1"></i>${evento.extendedProps.ubicacion}</span>` : ''}
                            </div>
                        </div>
                        <div class="evento-actions">
                            <button class="btn btn-evento btn-editar" onclick="editarEvento('${evento.id}')" title="Editar evento">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-evento btn-eliminar" onclick="eliminarEvento('${evento.id}', '${evento.title}')" title="Eliminar evento">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        if (eventos.length > 3) {
            cursosHtml += `
                <div class="text-center">
                    <small class="text-muted">... y ${eventos.length - 3} más</small>
                </div>
            `;
        }
        
        cursosHtml += '</div>';
    });
    
    eventosDiv.innerHTML = cursosHtml;
}

// Actualizar eventos por electivos
function updateEventosPorElectivos() {
    console.log('Actualizando eventos por electivos...');
    
    const eventosDiv = document.getElementById('eventosPorElectivos');
    if (!eventosDiv || !eventosDataAdmin) {
        return;
    }
    
    // Palabras clave para identificar electivos
    const palabrasElectivos = ['electivo', 'taller', 'optativo', 'extracurricular'];
    
    const eventosElectivos = eventosDataAdmin.filter(evento => {
        const titulo = evento.title.toLowerCase();
        return palabrasElectivos.some(palabra => titulo.includes(palabra));
    });
    
    console.log(`Eventos de electivos encontrados: ${eventosElectivos.length}`);
    
    if (eventosElectivos.length === 0) {
        eventosDiv.innerHTML = `
            <div class="estado-vacio">
                <i class="fas fa-graduation-cap"></i>
                <p>No hay eventos de electivos</p>
            </div>
        `;
        return;
    }
    
    let electivosHtml = '';
    eventosElectivos.slice(0, 8).forEach(evento => {
        const fechaEvento = new Date(evento.start);
        const fechaFormateada = fechaEvento.toLocaleDateString('es-ES', {
            day: '2-digit',
            month: '2-digit'
        });
        
        const horaFormateada = fechaEvento.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        electivosHtml += `
            <div class="evento-item evento-evaluacion">
                <div class="evento-content">
                    <div class="evento-info">
                        <h6>${evento.title}</h6>
                        <div class="text-muted">
                            <span><i class="fas fa-calendar-alt me-1"></i>${fechaFormateada}</span>
                            <span><i class="fas fa-clock me-1"></i>${horaFormateada}</span>
                            ${evento.extendedProps.curso ? `<span class="curso-badge">${evento.extendedProps.curso}</span>` : ''}
                        </div>
                    </div>
                    <div class="evento-actions">
                        <button class="btn btn-evento btn-editar" onclick="editarEvento('${evento.id}')" title="Editar evento">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-evento btn-eliminar" onclick="eliminarEvento('${evento.id}', '${evento.title}')" title="Eliminar evento">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    eventosDiv.innerHTML = electivosHtml;
}

// Mostrar detalle de evento en modal
function mostrarDetalleEvento(event) {
    // Crear y mostrar modal de detalle con botones de acción
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-calendar-alt me-2"></i>
                        Detalle del Evento
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-8">
                            <h6 class="fw-bold text-primary">${event.title}</h6>
                            <p class="mb-2">
                                <i class="fas fa-calendar me-2 text-info"></i>
                                <strong>Fecha:</strong> ${event.start.toLocaleDateString('es-ES')}
                            </p>
                            <p class="mb-2">
                                <i class="fas fa-clock me-2 text-info"></i>
                                <strong>Hora:</strong> ${event.start.toLocaleTimeString('es-ES', {hour: '2-digit', minute: '2-digit'})}
                            </p>
                            ${event.extendedProps.type ? `
                                <p class="mb-2">
                                    <i class="fas fa-tag me-2 text-info"></i>
                                    <strong>Tipo:</strong> ${event.extendedProps.type}
                                </p>
                            ` : ''}
                            ${event.extendedProps.ubicacion ? `
                                <p class="mb-2">
                                    <i class="fas fa-map-marker-alt me-2 text-info"></i>
                                    <strong>Ubicación:</strong> ${event.extendedProps.ubicacion}
                                </p>
                            ` : ''}
                            ${event.extendedProps.curso ? `
                                <p class="mb-2">
                                    <i class="fas fa-users me-2 text-info"></i>
                                    <strong>Curso:</strong> ${event.extendedProps.curso}
                                </p>
                            ` : ''}
                            ${event.extendedProps.encargado ? `
                                <p class="mb-2">
                                    <i class="fas fa-user me-2 text-info"></i>
                                    <strong>Encargado:</strong> ${event.extendedProps.encargado}
                                </p>
                            ` : ''}
                            ${event.extendedProps.description ? `
                                <p class="mb-2">
                                    <i class="fas fa-info-circle me-2 text-info"></i>
                                    <strong>Descripción:</strong> ${event.extendedProps.description}
                                </p>
                            ` : ''}
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    <button type="button" class="btn btn-warning" onclick="editarEvento('${event.id}')">
                        <i class="fas fa-edit me-1"></i>Editar
                    </button>
                    <button type="button" class="btn btn-danger" onclick="eliminarEvento('${event.id}', '${event.title}')">
                        <i class="fas fa-trash me-1"></i>Eliminar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Limpiar modal cuando se cierre
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

// Funciones de editar y eliminar eventos
function editarEvento(eventoId) {
    console.log('Editando evento:', eventoId);
    
    // Buscar el evento en los datos para pre-llenar el formulario
    const evento = eventosDataAdmin.find(e => e.id === eventoId);
    if (!evento) {
        alert('Error: No se encontró el evento');
        return;
    }
    
    // Crear modal de edición con datos pre-llenados
    const modalHtml = `
        <div class="modal fade" id="modalEditarEvento" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title">
                            <i class="fas fa-edit me-2"></i>Editar Evento: ${evento.title}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="formEditarEvento">
                            <input type="hidden" id="eventoId" value="${eventoId}">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="tituloEvento" class="form-label">Título del Evento</label>
                                        <input type="text" class="form-control" id="tituloEvento" name="titulo" value="${evento.title}" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="fechaEvento" class="form-label">Fecha</label>
                                        <input type="date" class="form-control" id="fechaEvento" name="fecha" value="${evento.start.split('T')[0]}" required>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="horaEvento" class="form-label">Hora</label>
                                        <input type="time" class="form-control" id="horaEvento" name="hora" value="${new Date(evento.start).toTimeString().slice(0,5)}" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="ubicacionEvento" class="form-label">Ubicación</label>
                                        <input type="text" class="form-control" id="ubicacionEvento" name="ubicacion" value="${evento.extendedProps.ubicacion || ''}">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="descripcionEvento" class="form-label">Descripción</label>
                                <textarea class="form-control" id="descripcionEvento" name="descripcion" rows="3">${evento.extendedProps.description || ''}</textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-warning" onclick="guardarCambiosEvento()">
                            <i class="fas fa-save me-1"></i>Guardar Cambios
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal anterior si existe
    const existingModal = document.getElementById('modalEditarEvento');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Agregar nuevo modal
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('modalEditarEvento'));
    modal.show();
    
    // Limpiar cuando se cierre
    document.getElementById('modalEditarEvento').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

function guardarCambiosEvento() {
    const form = document.getElementById('formEditarEvento');
    const formData = new FormData(form);
    const eventoId = document.getElementById('eventoId').value;
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Mostrar indicador de carga
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Guardando...';
    button.disabled = true;
    
    // Enviar datos al backend
    fetch(`/admin-editar-evento-calendario/${eventoId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalEditarEvento'));
            modal.hide();
            
            // Mostrar mensaje de éxito
            showNotification('Evento actualizado exitosamente', 'success');
            
            // Recargar calendario
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showNotification('Error al actualizar el evento: ' + (data.message || 'Error desconocido'), 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error de conexión al actualizar el evento', 'error');
    })
    .finally(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

function eliminarEvento(eventoId, titulo) {
    console.log('Eliminando evento:', eventoId);
    
    // Crear modal de confirmación personalizado
    const modalHtml = `
        <div class="modal fade" id="modalEliminarEvento" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-exclamation-triangle me-2"></i>Confirmar Eliminación
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="text-center">
                            <i class="fas fa-trash-alt text-danger" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                            <h6>¿Estás seguro de que deseas eliminar este evento?</h6>
                            <p class="text-muted mb-0">"${titulo}"</p>
                            <small class="text-danger">Esta acción no se puede deshacer.</small>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-1"></i>Cancelar
                        </button>
                        <button type="button" class="btn btn-danger" onclick="confirmarEliminarEvento('${eventoId}')">
                            <i class="fas fa-trash me-1"></i>Eliminar Evento
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal anterior si existe
    const existingModal = document.getElementById('modalEliminarEvento');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Agregar nuevo modal
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('modalEliminarEvento'));
    modal.show();
    
    // Limpiar cuando se cierre
    document.getElementById('modalEliminarEvento').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

function confirmarEliminarEvento(eventoId) {
    // Mostrar indicador de carga
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Eliminando...';
    button.disabled = true;
    
    // Enviar solicitud de eliminación
    fetch(`/admin-eliminar-evento-calendario/${eventoId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalEliminarEvento'));
            modal.hide();
            
            // Mostrar mensaje de éxito
            showNotification('Evento eliminado exitosamente', 'success');
            
            // Recargar calendario
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showNotification('Error al eliminar el evento: ' + (data.message || 'Error desconocido'), 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error de conexión al eliminar el evento', 'error');
    })
    .finally(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

// Función auxiliar para mostrar notificaciones
function showNotification(message, type) {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const iconClass = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        <i class="fas ${iconClass} me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
} 