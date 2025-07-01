$(document).ready(function() {
    let asignaturaIdActual = null;

    // Obtener el token CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Configurar AJAX para incluir el token CSRF
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Crear asignatura
    $('#btnCrearAsignatura').click(function() {
        const nombre = $('#nombre').val();
        const nivel = $('#nivel').val();
        const es_electivo = $('#es_electivo').is(':checked');

        // Validaciones
        if (!nombre) {
            mostrarError('El nombre es requerido');
            return;
        }
        if (!nivel) {
            mostrarError('Debe seleccionar un nivel');
            return;
        }

        // Enviar datos al servidor
        $.ajax({
            url: '/asignaturas/create/',
            type: 'POST',
            data: JSON.stringify({
                nombre: nombre,
                nivel: nivel,
                es_electivo: es_electivo
            }),
            contentType: 'application/json',
            success: function(response) {
                if (response.success) {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Éxito!',
                        text: response.message,
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    mostrarError(response.error || 'Error al crear la asignatura');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
                mostrarError('Error al crear la asignatura');
            }
        });
    });

    // Ver detalles de la asignatura
    $(document).on('click', '.view-asignatura', function(e) {
        e.preventDefault();
        const asignaturaId = $(this).data('asignatura-id');
        verDetalleAsignatura(asignaturaId);
    });

    // Editar asignatura
    $(document).on('click', '.edit-asignatura', function(e) {
        e.preventDefault();
        const asignaturaId = $(this).data('asignatura-id');
        editarAsignatura(asignaturaId);
    });

    // Eliminar asignatura
    $(document).on('click', '.delete-asignatura', function(e) {
        e.preventDefault();
        const asignaturaId = $(this).data('asignatura-id');
        const row = $(this).closest('tr');
        confirmarEliminarAsignatura(asignaturaId, row);
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

    // Función para ver detalles de la asignatura
    function verDetalleAsignatura(asignaturaId) {
        $.ajax({
            url: `/asignaturas/${asignaturaId}/data/`,
            type: 'GET',
            success: function(data) {
                if (data.success) {
                    // Crear el contenido del modal
                    let contenido = `
                        <div class="modal-body">
                            <h5 class="mb-3">Detalles de la Asignatura ${data.data.nombre}</h5>
                            
                            <div class="mb-3">
                                <h6>Información General</h6>
                                <p><strong>Nivel:</strong> ${data.data.nivel}°</p>
                                <p><strong>Tipo:</strong> ${data.data.es_electivo ? 'Electivo' : 'Obligatorio'}</p>
                            </div>
                            
                            <div class="mb-3">
                                <h6>Imparticiones (${data.data.imparticiones.length})</h6>
                                <ul class="list-group">
                                    ${data.data.imparticiones.map(imp => `
                                        <li class="list-group-item">
                                            ${imp.codigo} - ${imp.docente}
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                            
                            <div class="mb-3">
                                <h6>Objetivos (${data.data.objetivos.length})</h6>
                                <ul class="list-group">
                                    ${data.data.objetivos.map(obj => `
                                        <li class="list-group-item">
                                            ${obj.descripcion}
                                            <span class="badge ${obj.completado ? 'bg-success' : 'bg-warning'} float-end">
                                                ${obj.completado ? 'Completado' : 'Pendiente'}
                                            </span>
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                            
                            <div class="mb-3">
                                <h6>Recursos (${data.data.recursos.length})</h6>
                                <ul class="list-group">
                                    ${data.data.recursos.map(rec => `
                                        <li class="list-group-item">
                                            ${rec.titulo} - ${rec.tipo}
                                            <small class="d-block text-muted">${rec.descripcion}</small>
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                            
                            <div class="mb-3">
                                <h6>Evaluaciones Base (${data.data.evaluaciones.length})</h6>
                                <ul class="list-group">
                                    ${data.data.evaluaciones.map(eval => `
                                        <li class="list-group-item">
                                            ${eval.nombre} (${eval.ponderacion}%)
                                            <small class="d-block text-muted">${eval.descripcion}</small>
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        </div>
                    `;
                    
                    // Mostrar el modal con los detalles
                    Swal.fire({
                        title: `Asignatura ${data.data.nombre}`,
                        html: contenido,
                        width: '600px',
                        showConfirmButton: false,
                        showCloseButton: true
                    });
                } else {
                    mostrarError(data.error || 'No se pudieron cargar los detalles de la asignatura');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
                mostrarError('Error al cargar los detalles de la asignatura');
            }
        });
    }

    // Función para editar asignatura
    function editarAsignatura(asignaturaId) {
        // Primero obtener los datos actuales de la asignatura
        $.ajax({
            url: `/asignaturas/${asignaturaId}/data/`,
            type: 'GET',
            success: function(data) {
                if (data.success) {
                    // Crear el formulario de edición
                    let formulario = `
                        <form id="editarAsignaturaForm">
                            <div class="mb-3">
                                <label for="nombre" class="form-label">Nombre</label>
                                <input type="text" class="form-control" id="nombre" value="${data.data.nombre}" required>
                            </div>
                            <div class="mb-3">
                                <label for="nivel" class="form-label">Nivel</label>
                                <input type="number" class="form-control" id="nivel" value="${data.data.nivel}" min="1" max="4" required>
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input type="checkbox" class="form-check-input" id="es_electivo" ${data.data.es_electivo ? 'checked' : ''}>
                                    <label class="form-check-label" for="es_electivo">Es electivo</label>
                                </div>
                            </div>
                        </form>
                    `;

                    // Mostrar el modal de edición
                    Swal.fire({
                        title: `Editar Asignatura ${data.data.nombre}`,
                        html: formulario,
                        showCancelButton: true,
                        confirmButtonText: 'Guardar',
                        cancelButtonText: 'Cancelar',
                        preConfirm: () => {
                            // Validar y recoger los datos del formulario
                            const nombre = $('#nombre').val();
                            const nivel = $('#nivel').val();
                            const es_electivo = $('#es_electivo').is(':checked');

                            // Validaciones
                            if (!nombre) {
                                Swal.showValidationMessage('El nombre es requerido');
                                return false;
                            }
                            if (!nivel || nivel < 1 || nivel > 4) {
                                Swal.showValidationMessage('El nivel debe estar entre 1 y 4');
                                return false;
                            }

                            return {
                                nombre: nombre,
                                nivel: nivel,
                                es_electivo: es_electivo
                            };
                        }
                    }).then((result) => {
                        if (result.isConfirmed) {
                            // Enviar los datos actualizados al servidor
                            $.ajax({
                                url: `/asignaturas/${asignaturaId}/update/`,
                                type: 'POST',
                                data: JSON.stringify(result.value),
                                contentType: 'application/json',
                                success: function(response) {
                                    if (response.success) {
                                        Swal.fire({
                                            icon: 'success',
                                            title: '¡Éxito!',
                                            text: response.message,
                                            showConfirmButton: false,
                                            timer: 1500
                                        }).then(() => {
                                            window.location.reload();
                                        });
                                    } else {
                                        mostrarError(response.error || 'Error al actualizar la asignatura');
                                    }
                                },
                                error: function(xhr, status, error) {
                                    console.error('Error:', error);
                                    mostrarError('Error al actualizar la asignatura');
                                }
                            });
                        }
                    });
                } else {
                    mostrarError(data.error || 'Error al cargar los datos de la asignatura');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
                mostrarError('Error al cargar los datos de la asignatura');
            }
        });
    }

    // Función para confirmar eliminación
    function confirmarEliminarAsignatura(asignaturaId, row) {
        Swal.fire({
            title: '¿Estás seguro?',
            text: "Esta acción eliminará la asignatura y todos sus datos relacionados. Esta acción no se puede deshacer.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                eliminarAsignatura(asignaturaId, row);
            }
        });
    }

    // Función para eliminar asignatura
    function eliminarAsignatura(asignaturaId, row) {
        $.ajax({
            url: `/asignaturas/${asignaturaId}/delete/`,
            type: 'POST',
            success: function(response) {
                if (response.success) {
                    // Eliminar la fila de la tabla
                    row.fadeOut(400, function() {
                        $(this).remove();
                        
                        // Si no quedan más filas, mostrar mensaje
                        if ($('table tbody tr').length === 0) {
                            $('table tbody').append(
                                '<tr><td colspan="6" class="text-center">No hay asignaturas registradas</td></tr>'
                            );
                        }
                    });
                    
                    Swal.fire({
                        icon: 'success',
                        title: '¡Éxito!',
                        text: response.message,
                        showConfirmButton: false,
                        timer: 1500
                    });
                } else {
                    mostrarError(response.error || 'Error al eliminar la asignatura');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
                mostrarError('Error al eliminar la asignatura: ' + error);
            }
        });
    }
}); 