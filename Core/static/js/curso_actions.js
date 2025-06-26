$(document).ready(function() {
    let cursoIdActual = null;

    // Ver detalles del curso
    $(document).on('click', '.view-curso', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const cursoId = $(this).data('curso-id');
        
        // Mostrar loading
        $('#cursoDetailsModal .modal-body').html('<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Cargando...</div>');
        $('#cursoDetailsModal').modal('show');
        
        // Cargar datos del curso
        $.get(`/cursos/${cursoId}/data/`)
            .done(function(response) {
                if (response.success) {
                    mostrarDetallesCurso(response.data);
                } else {
                    mostrarError('Error al cargar los detalles del curso: ' + response.error);
                }
            })
            .fail(function() {
                mostrarError('Error de conexión al cargar los detalles del curso');
            });
    });

    // Editar curso
    $(document).on('click', '.edit-curso', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const cursoId = $(this).data('curso-id');
        cursoIdActual = cursoId;
        
        // Limpiar errores
        $('#editCursoErrors').hide().empty();
        
        // Cargar datos del curso para edición
        $.get(`/cursos/${cursoId}/data/`)
            .done(function(response) {
                if (response.success) {
                    llenarFormularioEdicion(response.data);
                    $('#editCursoModal').modal('show');
                } else {
                    mostrarError('Error al cargar los datos del curso: ' + response.error);
                }
            })
            .fail(function() {
                mostrarError('Error de conexión al cargar los datos del curso');
            });
    });

    // Eliminar curso
    $(document).on('click', '.delete-curso', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const cursoId = $(this).data('curso-id');
        const cursoNombre = $(this).closest('tr').find('td:first').text().trim();
        
        if (confirm(`¿Estás seguro de que deseas eliminar el curso ${cursoNombre}?\n\nEsta acción no se puede deshacer.`)) {
            eliminarCurso(cursoId);
        }
    });

    // Guardar cambios de edición
    $('#saveEditCursoBtn').click(function() {
        if (!cursoIdActual) return;
        
        const formData = new FormData($('#editCursoForm')[0]);
        
        // Mostrar loading
        $(this).prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Guardando...');
        
        $.ajax({
            url: `/cursos/${cursoIdActual}/update/`,
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
                $('#editCursoModal').modal('hide');
                mostrarExito(response.message);
                // Recargar la página para mostrar los cambios
                setTimeout(() => location.reload(), 1000);
            } else {
                mostrarErroresFormulario(response.errors || [response.error]);
            }
        })
        .fail(function() {
            mostrarErroresFormulario(['Error de conexión al guardar los cambios']);
        })
        .always(function() {
            $('#saveEditCursoBtn').prop('disabled', false).html('Guardar Cambios');
        });
    });

    // Funciones auxiliares
    function mostrarDetallesCurso(curso) {
        // Cargar información básica
        $('#cursoDetailNombre').text(curso.nombre);
        $('#cursoDetailProfesor').text(curso.profesor_jefe ? curso.profesor_jefe.nombre : 'Sin profesor jefe');
        $('#cursoDetailEstudiantes').text(curso.total_estudiantes);
        $('#cursoDetailAsignaturas').text(curso.total_asignaturas);
        
        // Cargar lista de estudiantes
        const estudiantesHtml = curso.estudiantes.map(estudiante => `
            <tr>
                <td>${estudiante.nombre}</td>
                <td>${estudiante.rut}</td>
                <td>${estudiante.correo}</td>
            </tr>
        `).join('');
        $('#cursoEstudiantesList').html(estudiantesHtml || '<tr><td colspan="3" class="text-center text-muted">No hay estudiantes registrados</td></tr>');
        
        // Cargar lista de asignaturas
        const asignaturasHtml = curso.asignaturas.map(asignatura => `
            <tr>
                <td>${asignatura.nombre}</td>
                <td>${asignatura.codigo || 'N/A'}</td>
                <td>${asignatura.docente}</td>
            </tr>
        `).join('');
        $('#cursoAsignaturasList').html(asignaturasHtml || '<tr><td colspan="3" class="text-center text-muted">No hay asignaturas registradas</td></tr>');
        
        // Restaurar el contenido del modal con la estructura original
        const modalContent = `
            <div class="row mb-3">
                <div class="col-md-6">
                    <strong>Curso:</strong> <span id="cursoDetailNombre">${curso.nombre}</span>
                </div>
                <div class="col-md-6">
                    <strong>Profesor Jefe:</strong> <span id="cursoDetailProfesor">${curso.profesor_jefe ? curso.profesor_jefe.nombre : 'Sin profesor jefe'}</span>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col-md-6">
                    <strong>Total Estudiantes:</strong> <span id="cursoDetailEstudiantes">${curso.total_estudiantes}</span>
                </div>
                <div class="col-md-6">
                    <strong>Total Asignaturas:</strong> <span id="cursoDetailAsignaturas">${curso.total_asignaturas}</span>
                </div>
            </div>
            
            <!-- Tabs para estudiantes y asignaturas -->
            <ul class="nav nav-tabs mb-3" id="cursoDetailsTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="estudiantes-tab" data-bs-toggle="tab" data-bs-target="#estudiantesTab" type="button" role="tab">
                        <i class="fas fa-users me-1"></i>Estudiantes
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="asignaturas-tab" data-bs-toggle="tab" data-bs-target="#asignaturasTab" type="button" role="tab">
                        <i class="fas fa-book me-1"></i>Asignaturas
                    </button>
                </li>
            </ul>
            
            <div class="tab-content" id="cursoDetailsTabContent">
                <div class="tab-pane fade show active" id="estudiantesTab" role="tabpanel">
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Nombre</th>
                                    <th>RUT</th>
                                    <th>Correo</th>
                                </tr>
                            </thead>
                            <tbody id="cursoEstudiantesList">
                                ${estudiantesHtml || '<tr><td colspan="3" class="text-center text-muted">No hay estudiantes registrados</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="tab-pane fade" id="asignaturasTab" role="tabpanel">
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Asignatura</th>
                                    <th>Código</th>
                                    <th>Docente</th>
                                </tr>
                            </thead>
                            <tbody id="cursoAsignaturasList">
                                ${asignaturasHtml || '<tr><td colspan="3" class="text-center text-muted">No hay asignaturas registradas</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        $('#cursoDetailsModal .modal-body').html(modalContent);
    }

    function llenarFormularioEdicion(curso) {
        $('#editCursoNivel').val(curso.nivel);
        $('#editCursoLetra').val(curso.letra);
        $('#editCursoProfesorJefe').val(curso.profesor_jefe ? curso.profesor_jefe.id : '');
    }

    function eliminarCurso(cursoId) {
        $.ajax({
            url: `/cursos/${cursoId}/delete/`,
            type: 'POST',
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
            }
        })
        .done(function(response) {
            if (response.success) {
                mostrarExito(response.message);
                // Recargar la página para mostrar los cambios
                setTimeout(() => location.reload(), 1000);
            } else {
                mostrarError('Error al eliminar el curso: ' + response.error);
            }
        })
        .fail(function() {
            mostrarError('Error de conexión al eliminar el curso');
        });
    }

    function mostrarErroresFormulario(errores) {
        const errorsHtml = errores.map(error => `<li>${error}</li>`).join('');
        $('#editCursoErrors').html(`<ul>${errorsHtml}</ul>`).show();
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