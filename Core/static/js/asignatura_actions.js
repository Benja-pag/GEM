$(document).ready(function() {
    let asignaturaIdActual = null;

    // Ver detalles de la asignatura
    $(document).on('click', '.view-asignatura', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const asignaturaId = $(this).data('asignatura-id');
        
        // Mostrar loading
        $('#asignaturaDetailsModal .modal-body').html('<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Cargando...</div>');
        $('#asignaturaDetailsModal').modal('show');
        
        // Cargar datos de la asignatura
        $.get(`/asignaturas/${asignaturaId}/data/`)
            .done(function(response) {
                if (response.success) {
                    mostrarDetallesAsignatura(response.data);
                } else {
                    mostrarError('Error al cargar los detalles de la asignatura: ' + response.error);
                }
            })
            .fail(function() {
                mostrarError('Error de conexión al cargar los detalles de la asignatura');
            });
    });

    // Editar asignatura
    $(document).on('click', '.edit-asignatura', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const asignaturaId = $(this).data('asignatura-id');
        asignaturaIdActual = asignaturaId;
        
        // Limpiar errores
        $('#editAsignaturaErrors').hide().empty();
        
        // Cargar datos de la asignatura para edición
        $.get(`/asignaturas/${asignaturaId}/data/`)
            .done(function(response) {
                if (response.success) {
                    llenarFormularioEdicionAsignatura(response.data);
                    $('#editAsignaturaModal').modal('show');
                } else {
                    mostrarError('Error al cargar los datos de la asignatura: ' + response.error);
                }
            })
            .fail(function() {
                mostrarError('Error de conexión al cargar los datos de la asignatura');
            });
    });

    // Guardar cambios de edición
    $('#saveEditAsignaturaBtn').click(function() {
        if (!asignaturaIdActual) return;
        
        const formData = new FormData($('#editAsignaturaForm')[0]);
        
        // Mostrar loading
        $(this).prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Guardando...');
        
        $.ajax({
            url: `/asignaturas/${asignaturaIdActual}/update/`,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
            }
        })
        .done(function(response) {
            if (response.success) {
                $('#editAsignaturaModal').modal('hide');
                mostrarExito(response.message);
                // Recargar la página para mostrar los cambios
                setTimeout(() => location.reload(), 1000);
            } else {
                mostrarErroresFormularioAsignatura(response.errors || [response.error]);
            }
        })
        .fail(function() {
            mostrarErroresFormularioAsignatura(['Error de conexión al guardar los cambios']);
        })
        .always(function() {
            $('#saveEditAsignaturaBtn').prop('disabled', false).html('Guardar Cambios');
        });
    });

    // Funciones auxiliares
    function mostrarDetallesAsignatura(asignatura) {
        // Cargar lista de estudiantes
        const estudiantesHtml = asignatura.estudiantes.map(estudiante => `
            <tr>
                <td>${estudiante.nombre}</td>
                <td>${estudiante.rut}</td>
                <td>${estudiante.curso}</td>
            </tr>
        `).join('');
        
        // Cargar lista de horarios
        const horariosHtml = asignatura.horarios.map(horario => `
            <tr>
                <td>${horario.dia}</td>
                <td>${horario.horario}</td>
                <td>${horario.sala}</td>
                <td>${horario.curso}</td>
            </tr>
        `).join('');
        
        // Cargar lista de evaluaciones
        const evaluacionesHtml = asignatura.evaluaciones.map(evaluacion => `
            <tr>
                <td>${evaluacion.nombre}</td>
                <td>${evaluacion.descripcion}</td>
                <td>${evaluacion.fecha}</td>
                <td>${evaluacion.curso}</td>
            </tr>
        `).join('');
        
        // Restaurar el contenido del modal con la estructura original
        const modalContent = `
            <div class="row mb-3">
                <div class="col-md-6">
                    <strong>Código:</strong> <span id="asignaturaDetailCodigo">${asignatura.codigo}</span>
                </div>
                <div class="col-md-6">
                    <strong>Nombre:</strong> <span id="asignaturaDetailNombre">${asignatura.nombre}</span>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col-md-6">
                    <strong>Docente:</strong> <span id="asignaturaDetailDocente">${asignatura.docente.nombre}</span>
                </div>
                <div class="col-md-6">
                    <strong>Total Estudiantes:</strong> <span id="asignaturaDetailEstudiantes">${asignatura.total_estudiantes}</span>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col-12">
                    <strong>Descripción:</strong> <span id="asignaturaDetailDescripcion">${asignatura.descripcion}</span>
                </div>
            </div>
            
            <!-- Tabs para estudiantes, horarios y evaluaciones -->
            <ul class="nav nav-tabs mb-3" id="asignaturaDetailsTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="estudiantes-asig-tab" data-bs-toggle="tab" data-bs-target="#estudiantesAsigTab" type="button" role="tab">
                        <i class="fas fa-users me-1"></i>Estudiantes (${asignatura.total_estudiantes})
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="horarios-tab" data-bs-toggle="tab" data-bs-target="#horariosTab" type="button" role="tab">
                        <i class="fas fa-clock me-1"></i>Horarios (${asignatura.total_horarios})
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="evaluaciones-asig-tab" data-bs-toggle="tab" data-bs-target="#evaluacionesAsigTab" type="button" role="tab">
                        <i class="fas fa-clipboard-list me-1"></i>Evaluaciones (${asignatura.total_evaluaciones})
                    </button>
                </li>
            </ul>
            
            <div class="tab-content" id="asignaturaDetailsTabContent">
                <div class="tab-pane fade show active" id="estudiantesAsigTab" role="tabpanel">
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Nombre</th>
                                    <th>RUT</th>
                                    <th>Curso</th>
                                </tr>
                            </thead>
                            <tbody id="asignaturaEstudiantesList">
                                ${estudiantesHtml || '<tr><td colspan="3" class="text-center text-muted">No hay estudiantes registrados</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="tab-pane fade" id="horariosTab" role="tabpanel">
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Día</th>
                                    <th>Horario</th>
                                    <th>Sala</th>
                                    <th>Curso</th>
                                </tr>
                            </thead>
                            <tbody id="asignaturaHorariosList">
                                ${horariosHtml || '<tr><td colspan="4" class="text-center text-muted">No hay horarios registrados</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="tab-pane fade" id="evaluacionesAsigTab" role="tabpanel">
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Evaluación</th>
                                    <th>Descripción</th>
                                    <th>Fecha</th>
                                    <th>Curso</th>
                                </tr>
                            </thead>
                            <tbody id="asignaturaEvaluacionesList">
                                ${evaluacionesHtml || '<tr><td colspan="4" class="text-center text-muted">No hay evaluaciones registradas</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        $('#asignaturaDetailsModal .modal-body').html(modalContent);
    }

    function llenarFormularioEdicionAsignatura(asignatura) {
        $('#editAsignaturaCodigo').val(asignatura.codigo);
        $('#editAsignaturaNombre').val(asignatura.nombre);
        $('#editAsignaturaDescripcion').val(asignatura.descripcion);
        $('#editAsignaturaDocente').val(asignatura.docente.id || '');
    }

    function mostrarErroresFormularioAsignatura(errores) {
        const errorsHtml = errores.map(error => `<li>${error}</li>`).join('');
        $('#editAsignaturaErrors').html(`<ul>${errorsHtml}</ul>`).show();
    }

    function mostrarError(mensaje) {
        // Función para mostrar errores - integrar con el sistema de notificaciones existente
        if (typeof mostrarNotificacion === 'function') {
            mostrarNotificacion(mensaje, 'error');
        } else {
            alert(mensaje);
        }
    }

    function mostrarExito(mensaje) {
        // Función para mostrar éxito - integrar con el sistema de notificaciones existente
        if (typeof mostrarNotificacion === 'function') {
            mostrarNotificacion(mensaje, 'success');
        } else {
            alert(mensaje);
        }
    }
}); 