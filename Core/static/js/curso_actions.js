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
        // Crear toast para mostrar error
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-danger border-0';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-circle me-2"></i>${mensaje}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.appendChild(toast);
        document.body.appendChild(container);
        
        new bootstrap.Toast(toast).show();
    }

    function mostrarExito(mensaje) {
        // Función para mostrar éxito - integrar con el sistema de notificaciones existente
        if (typeof mostrarNotificacion === 'function') {
            mostrarNotificacion(mensaje, 'success');
        } else {
            alert(mensaje);
        }
    }

    // Funciones para herramientas IA

    async function generarReporteIA(cursoId, tipoReporte) {
        try {
            const response = await fetch('/curso/ia/reporte/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    curso_id: cursoId,
                    tipo_reporte: tipoReporte
                })
            });

            if (!response.ok) {
                throw new Error('Error al generar reporte');
            }

            const data = await response.json();
            mostrarReporteIA(data);
        } catch (error) {
            mostrarError('Error al generar reporte: ' + error.message);
        }
    }

    async function generarSugerenciasIA(cursoId, area) {
        try {
            const response = await fetch('/curso/ia/sugerencias/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    curso_id: cursoId,
                    area: area
                })
            });

            if (!response.ok) {
                throw new Error('Error al generar sugerencias');
            }

            const data = await response.json();
            mostrarSugerenciasIA(data);
        } catch (error) {
            mostrarError('Error al generar sugerencias: ' + error.message);
        }
    }

    async function generarComunicadoIA(cursoId, tipoComunicado) {
        try {
            const response = await fetch('/curso/ia/comunicado/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    curso_id: cursoId,
                    tipo_comunicado: tipoComunicado
                })
            });

            if (!response.ok) {
                throw new Error('Error al generar comunicado');
            }

            const data = await response.json();
            mostrarComunicadoIA(data);
        } catch (error) {
            mostrarError('Error al generar comunicado: ' + error.message);
        }
    }

    function mostrarReporteIA(data) {
        // Crear modal para mostrar el reporte
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'reporteIAModal';
        
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${data.titulo}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <h6 class="text-primary">Resumen Ejecutivo</h6>
                            <p>${data.resumen_ejecutivo}</p>
                        </div>
                        
                        <div class="mb-3">
                            <h6 class="text-primary">Análisis Detallado</h6>
                            <ul class="list-unstyled">
                                ${data.analisis_detallado.map(item => `
                                    <li class="mb-2">• ${item.punto}</li>
                                `).join('')}
                            </ul>
                        </div>
                        
                        <div class="mb-3">
                            <h6 class="text-primary">Conclusiones</h6>
                            <p>${data.conclusiones}</p>
                        </div>
                        
                        <div class="mb-3">
                            <h6 class="text-primary">Recomendaciones</h6>
                            <ul class="list-unstyled">
                                ${data.recomendaciones.map(rec => `
                                    <li class="mb-2">• ${rec}</li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="descargarReporte(${JSON.stringify(data)})">
                            <i class="fas fa-download me-1"></i>Descargar
                        </button>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        new bootstrap.Modal(modal).show();
    }

    function mostrarSugerenciasIA(data) {
        // Crear modal para mostrar las sugerencias
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'sugerenciasIAModal';
        
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Sugerencias de Intervención</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <h6 class="text-primary">Área de Intervención</h6>
                            <p>${data.area_intervencion}</p>
                        </div>
                        
                        <div class="mb-3">
                            <h6 class="text-primary">Objetivos</h6>
                            <ul class="list-unstyled">
                                ${data.objetivos.map(obj => `
                                    <li class="mb-2">• ${obj}</li>
                                `).join('')}
                            </ul>
                        </div>
                        
                        <div class="mb-3">
                            <h6 class="text-primary">Estrategias</h6>
                            <ul class="list-unstyled">
                                ${data.estrategias.map(est => `
                                    <li class="mb-2">• ${est.estrategia}</li>
                                `).join('')}
                            </ul>
                        </div>
                        
                        <div class="mb-3">
                            <h6 class="text-primary">Recursos Necesarios</h6>
                            <ul class="list-unstyled">
                                ${data.recursos_necesarios.map(rec => `
                                    <li class="mb-2">• ${rec}</li>
                                `).join('')}
                            </ul>
                        </div>
                        
                        <div class="mb-3">
                            <h6 class="text-primary">Indicadores de Éxito</h6>
                            <ul class="list-unstyled">
                                ${data.indicadores_exito.map(ind => `
                                    <li class="mb-2">• ${ind}</li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="implementarSugerencias(${JSON.stringify(data)})">
                            <i class="fas fa-check me-1"></i>Implementar
                        </button>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        new bootstrap.Modal(modal).show();
    }

    function mostrarComunicadoIA(data) {
        // Crear modal para mostrar el comunicado
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'comunicadoIAModal';
        
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${data.asunto}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <p class="mb-3">${data.saludo}</p>
                            <p class="mb-3">${data.cuerpo}</p>
                            <p class="mb-3">${data.despedida}</p>
                            <p class="text-end">${data.firma}</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="enviarComunicado(${JSON.stringify(data)})">
                            <i class="fas fa-paper-plane me-1"></i>Enviar
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="editarComunicado(${JSON.stringify(data)})">
                            <i class="fas fa-edit me-1"></i>Editar
                        </button>
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cerrar</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        new bootstrap.Modal(modal).show();
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Funciones auxiliares para acciones posteriores
    function descargarReporte(data) {
        // Implementar lógica para descargar el reporte
        console.log('Descargando reporte:', data);
    }

    function implementarSugerencias(data) {
        // Implementar lógica para guardar/implementar las sugerencias
        console.log('Implementando sugerencias:', data);
    }

    function enviarComunicado(data) {
        // Implementar lógica para enviar el comunicado
        console.log('Enviando comunicado:', data);
    }

    function editarComunicado(data) {
        // Implementar lógica para editar el comunicado
        console.log('Editando comunicado:', data);
    }
}); 