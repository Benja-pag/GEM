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

    function mostrarExito(mensaje) {
        // Función para mostrar éxito - integrar con el sistema de notificaciones existente
        if (typeof mostrarNotificacion === 'function') {
            mostrarNotificacion(mensaje, 'success');
        } else {
            alert(mensaje);
        }
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function descargarReporte(data) {
        // Implementar lógica para descargar reporte
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

    // Funciones auxiliares globales
    function mostrarCargando(mensaje) {
        const contenedor = document.getElementById('contenedor-resultados');
        contenedor.style.display = 'block';
        document.getElementById('titulo-resultados').textContent = mensaje;
        document.getElementById('contenido-resultados').innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-3 text-muted">${mensaje}</p>
            </div>
        `;
    }

    function ocultarCargando() {
        // Esta función se deja vacía porque mostrarResultados ya maneja la visualización
    }

    function mostrarError(mensaje) {
        const contenedor = document.getElementById('contenedor-resultados');
        contenedor.style.display = 'block';
        document.getElementById('titulo-resultados').textContent = 'Error';
        document.getElementById('contenido-resultados').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>${mensaje}
            </div>
        `;
    }

    // Funciones de Análisis IA
    async function analizarRendimiento(cursoId) {
        try {
            mostrarCargando('Analizando rendimiento...');
            const response = await fetch(`/api/curso/${cursoId}/analisis-rendimiento/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });

            if (!response.ok) {
                throw new Error('Error al analizar rendimiento');
            }

            const data = await response.json();
            mostrarResultados('Análisis de Rendimiento', generarContenidoAnalisis(data));
        } catch (error) {
            mostrarError('Error: ' + error.message);
        } finally {
            ocultarCargando();
        }
    }

    async function predecirRiesgo(cursoId) {
        try {
            mostrarCargando('Analizando riesgo académico...');
            const response = await fetch(`/api/curso/${cursoId}/prediccion-riesgo/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });

            if (!response.ok) {
                throw new Error('Error al predecir riesgo');
            }

            const data = await response.json();
            mostrarResultados('Predicción de Riesgo Académico', generarContenidoPrediccion(data));
        } catch (error) {
            mostrarError('Error: ' + error.message);
        } finally {
            ocultarCargando();
        }
    }

    async function obtenerRecomendaciones(cursoId) {
        try {
            mostrarCargando('Generando recomendaciones...');
            const response = await fetch(`/api/curso/${cursoId}/recomendaciones/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });

            if (!response.ok) {
                throw new Error('Error al obtener recomendaciones');
            }

            const data = await response.json();
            mostrarResultados('Recomendaciones Personalizadas', generarContenidoRecomendaciones(data));
        } catch (error) {
            mostrarError('Error: ' + error.message);
        } finally {
            ocultarCargando();
        }
    }

    function mostrarResultados(titulo, contenido) {
        const contenedor = document.getElementById('contenedor-resultados');
        contenedor.style.display = 'block';
        document.getElementById('titulo-resultados').textContent = titulo;
        document.getElementById('contenido-resultados').innerHTML = contenido;
    }

    function cerrarResultados() {
        document.getElementById('contenedor-resultados').style.display = 'none';
    }

    async function descargarPDF() {
        try {
            const contenido = document.getElementById('contenido-resultados').innerHTML;
            const titulo = document.getElementById('titulo-resultados').textContent;
            
            const response = await fetch('/api/generar-pdf/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    contenido: contenido,
                    titulo: titulo
                })
            });

            if (!response.ok) {
                throw new Error('Error al generar PDF');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${titulo.toLowerCase().replace(/\s+/g, '_')}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            mostrarError('Error al descargar PDF: ' + error.message);
        }
    }

    function generarContenidoAnalisis(data) {
        return `
            <div class="row">
                <div class="col-12 mb-4">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>${data.resumen}
                    </div>
                </div>
                <div class="col-md-4 mb-4">
                    <div class="card border-primary">
                        <div class="card-body text-center">
                            <h3 class="text-primary mb-0">${data.promedio_general}</h3>
                            <p class="text-muted">Promedio General</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-4">
                    <div class="card border-success">
                        <div class="card-body text-center">
                            <h3 class="text-success mb-0">${data.asistencia_promedio}</h3>
                            <p class="text-muted">Asistencia Promedio</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-4">
                    <div class="card border-info">
                        <div class="card-body text-center">
                            <h3 class="text-info mb-0">${data.total_estudiantes}</h3>
                            <p class="text-muted">Total Estudiantes</p>
                        </div>
                    </div>
                </div>
                <div class="col-12">
                    <h6 class="mb-3">Distribución de Notas</h6>
                    <div class="progress" style="height: 25px;">
                        <div class="progress-bar bg-success" style="width: ${(data.distribucion.sobre_6 / data.total_estudiantes) * 100}%" 
                             title="Sobre 6.0">
                            ${data.distribucion.sobre_6} (≥6.0)
                        </div>
                        <div class="progress-bar bg-info" style="width: ${(data.distribucion.entre_5_6 / data.total_estudiantes) * 100}%" 
                             title="Entre 5.0 y 5.9">
                            ${data.distribucion.entre_5_6} (5.0-5.9)
                        </div>
                        <div class="progress-bar bg-warning" style="width: ${(data.distribucion.entre_4_5 / data.total_estudiantes) * 100}%" 
                             title="Entre 4.0 y 4.9">
                            ${data.distribucion.entre_4_5} (4.0-4.9)
                        </div>
                        <div class="progress-bar bg-danger" style="width: ${(data.distribucion.bajo_4 / data.total_estudiantes) * 100}%" 
                             title="Bajo 4.0">
                            ${data.distribucion.bajo_4} (<4.0)
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function generarContenidoPrediccion(data) {
        return `
            <div class="row">
                <div class="col-12 mb-4">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        Se han identificado ${data.total_riesgo || 0} estudiantes en riesgo académico.
                    </div>
                </div>
                ${(data.estudiantes || []).map(est => `
                    <div class="col-md-6 mb-4">
                        <div class="card h-100 ${est.nivel_riesgo === 'alto' ? 'border-danger' : 'border-warning'}">
                            <div class="card-body">
                                <h6 class="card-title">${est.nombre}</h6>
                                <p class="card-text small text-muted">RUT: ${est.rut}</p>
                                <div class="mb-3">
                                    <span class="badge bg-${est.nivel_riesgo === 'alto' ? 'danger' : 'warning'}">
                                        Riesgo ${est.nivel_riesgo}
                                    </span>
                                </div>
                                <p class="card-text">
                                    <strong>Factores de riesgo:</strong><br>
                                    ${est.factores.join('<br>')}
                                </p>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    function generarContenidoRecomendaciones(data) {
        return `
            <div class="row">
                <div class="col-12 mb-4">
                    <div class="alert alert-success">
                        <i class="fas fa-lightbulb me-2"></i>
                        Se han generado recomendaciones personalizadas para ${data.total_estudiantes || 0} estudiantes.
                    </div>
                </div>
                ${(data.recomendaciones || []).map(rec => `
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header bg-light">
                                <h6 class="card-title mb-0">${rec.estudiante}</h6>
                                <small class="text-muted">RUT: ${rec.rut}</small>
                            </div>
                            <div class="card-body">
                                <ul class="list-unstyled mb-0">
                                    ${rec.sugerencias.map(sug => `
                                        <li class="mb-2">
                                            <i class="fas fa-check-circle text-success me-2"></i>
                                            ${sug}
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Funciones auxiliares
    function mostrarCargando(mensaje) {
        const contenedor = document.getElementById('contenedor-resultados');
        contenedor.style.display = 'block';
        document.getElementById('titulo-resultados').textContent = mensaje;
        document.getElementById('contenido-resultados').innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-3 text-muted">${mensaje}</p>
            </div>
        `;
    }

    function ocultarCargando() {
        // Esta función se deja vacía porque mostrarResultados ya maneja la visualización
    }
}); 