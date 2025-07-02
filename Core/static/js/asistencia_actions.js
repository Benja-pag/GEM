$(document).ready(function() {
    // Variables globales
    let asignaturaIdActual = null;
    let claseActual = null;
    
    // Función para formatear la fecha
    function formatearFecha(fecha) {
        const opciones = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        return new Date(fecha).toLocaleDateString('es-ES', opciones);
    }
    
    // Función para cargar los datos de asistencia
    function cargarAsistencia(asignaturaId) {
        asignaturaIdActual = asignaturaId;
        
        // Mostrar loading
        $('#asistenciaContent').html('<div class="text-center py-5"><i class="fas fa-spinner fa-spin fa-3x"></i><p class="mt-3">Cargando datos de asistencia...</p></div>');
        
        // Cargar datos de asistencia
        $.get(`/obtener-asistencia-asignatura/${asignaturaId}/`)
            .done(function(response) {
                if (response.success) {
                    mostrarDatosAsistencia(response);
                } else {
                    mostrarError('Error al cargar los datos de asistencia: ' + response.error);
                }
            })
            .fail(function() {
                mostrarError('Error de conexión al cargar los datos de asistencia');
            });
    }
    
    // Función para mostrar los datos de asistencia
    function mostrarDatosAsistencia(response) {
        if (!response.cursos || response.cursos.length === 0) {
            $('#asistenciaContent').html('<div class="alert alert-info">No hay clases programadas para hoy.</div>');
            return;
        }

        // Formatear la fecha para mostrar el día de la semana en español
        const fecha = new Date(response.fecha + 'T00:00:00');
        const dia_semana = response.dia_semana || 'LUNES'; // Valor por defecto por si acaso

        const meses = [
            'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
        ];

        const fechaFormateada = `${fecha.getDate()} de ${meses[fecha.getMonth()]} de ${fecha.getFullYear()}`;

        let html = `
            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">
                        <i class="fas fa-calendar-day me-2"></i>
                        Registro de Asistencia
                    </h4>
                </div>
                <div class="card-body">
                    <div class="row align-items-center mb-4">
                        <div class="col-md-6">
                            <h5 class="mb-0">
                                <i class="fas fa-calendar me-2"></i>
                                <strong>${dia_semana.charAt(0)}${dia_semana.slice(1).toLowerCase()}, ${fechaFormateada}</strong>
                            </h5>
                        </div>
                        <div class="col-md-6 text-md-end">
                            <h5 class="mb-0 text-primary">
                                <i class="fas fa-book me-2"></i>
                                ${response.asignatura}
                            </h5>
                        </div>
                    </div>
                </div>
            </div>
        `;

        response.cursos.forEach(curso => {
            // Guardar los IDs de las clases como un atributo data en la tarjeta
            const claseIds = curso.clases.map(clase => clase.id);
            
            html += `
            <div class="card mb-4" data-clase-ids='${JSON.stringify(claseIds)}'>
                <div class="card-header bg-primary text-white">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="mb-0 text-white">
                                <i class="fas fa-users me-2"></i>
                                ${curso.curso}
                            </h5>
                            <p class="mb-0 mt-1 text-white">
                                <i class="fas fa-book me-2"></i>
                                ${response.asignatura} <small class="ms-2">(${response.codigo})</small>
                            </p>
                        </div>
                        <div class="d-flex align-items-center">
                            <div class="me-3">
                                <span class="badge ${curso.estado === 'completo' ? 'bg-success' : 
                                                    curso.estado === 'parcial' ? 'bg-warning' : 
                                                    'bg-secondary'} p-2">
                                    <i class="fas ${curso.estado === 'completo' ? 'fa-check-circle' : 
                                                   curso.estado === 'parcial' ? 'fa-clock' : 
                                                   'fa-hourglass'} me-1"></i>
                                    ${curso.estado_texto}
                                </span>
                            </div>
                            <div>
                                <button class="btn btn-light btn-sm me-2 marcar-todos-presentes" 
                                        ${curso.estado === 'completo' ? 'disabled' : ''}>
                                    <i class="fas fa-check-circle me-1"></i>Marcar Todos Presentes
                                </button>
                                <button class="btn btn-light btn-sm marcar-todos-ausentes"
                                        ${curso.estado === 'completo' ? 'disabled' : ''}>
                                    <i class="fas fa-times-circle me-1"></i>Marcar Todos Ausentes
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row mb-4">
                        <div class="col-md-3">
                            <div class="card bg-light">
                                <div class="card-body text-center">
                                    <h6><i class="fas fa-users me-1"></i>Total Estudiantes</h6>
                                    <h4>${curso.total_estudiantes}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-success text-white">
                                <div class="card-body text-center">
                                    <h6><i class="fas fa-check-circle me-1"></i>Presentes</h6>
                                    <h4 class="presentes-count">${curso.presentes}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-danger text-white">
                                <div class="card-body text-center">
                                    <h6><i class="fas fa-times-circle me-1"></i>Ausentes</h6>
                                    <h4 class="ausentes-count">${curso.ausentes}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-warning">
                                <div class="card-body text-center">
                                    <h6><i class="fas fa-question-circle me-1"></i>Sin Registro</h6>
                                    <h4 class="sin-registro-count">${curso.sin_registro}</h4>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead class="table-primary">
                                <tr>
                                    <th><i class="fas fa-id-card me-1"></i>RUT</th>
                                    <th><i class="fas fa-user me-1"></i>Nombre</th>
                                    <th><i class="fas fa-clipboard-check me-1"></i>Estado</th>
                                    <th><i class="fas fa-file-medical me-1"></i>Justificación</th>
                                    <th><i class="fas fa-comment me-1"></i>Observaciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${curso.estudiantes.map(estudiante => `
                                    <tr>
                                        <td>${estudiante.rut}</td>
                                        <td>${estudiante.nombre}</td>
                                        <td>
                                            <select class="form-select estado-asistencia" 
                                                    id="estado_${estudiante.id}"
                                                    name="estado_${estudiante.id}"
                                                    data-estudiante-id="${estudiante.id}"
                                                    ${curso.estado === 'completo' ? 'disabled' : ''}>
                                                <option value="">Sin registro</option>
                                                <option value="presente" ${estudiante.asistencias[0].presente === true ? 'selected' : ''}>Presente</option>
                                                <option value="ausente" ${estudiante.asistencias[0].presente === false ? 'selected' : ''}>Ausente</option>
                                            </select>
                                        </td>
                                        <td>
                                            <div class="form-check">
                                                <input type="checkbox" 
                                                       class="form-check-input justificacion-check"
                                                       id="justificacion_${estudiante.id}"
                                                       name="justificacion_${estudiante.id}"
                                                       data-estudiante-id="${estudiante.id}" 
                                                       ${estudiante.asistencias[0].presente === false ? '' : 'disabled'}
                                                       ${curso.estado === 'completo' ? 'disabled' : ''}
                                                       ${estudiante.asistencias[0].justificado ? 'checked' : ''}>
                                                <label class="form-check-label" 
                                                       for="justificacion_${estudiante.id}">
                                                    Justificado
                                                </label>
                                            </div>
                                        </td>
                                        <td>
                                            <input type="text" 
                                                   class="form-control observacion-input"
                                                   id="observacion_${estudiante.id}"
                                                   name="observacion_${estudiante.id}"
                                                   data-estudiante-id="${estudiante.id}" 
                                                   ${estudiante.asistencias[0].presente === false ? '' : 'disabled'}
                                                   ${curso.estado === 'completo' ? 'disabled' : ''}
                                                   value="${estudiante.asistencias[0].observacion || ''}"
                                                   placeholder="Ingrese observación...">
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="card-footer text-end">
                    <button class="btn btn-success guardar-todo">
                        <i class="fas fa-save me-1"></i>Guardar Asistencia
                    </button>
                </div>
            </div>`;
        });

        $('#asistenciaContent').html(html);

        // Inicializar eventos
        inicializarEventos();
    }
    
    // Función para mostrar error
    function mostrarError(mensaje, detalles = null) {
        let htmlContent = `<div class="text-danger mb-3">${mensaje}</div>`;
        
        if (detalles) {
            if (typeof detalles === 'object' && detalles.resumen) {
                htmlContent += `<div class="text-info mb-2">${detalles.resumen}</div>`;
                
                if (detalles.errores && detalles.errores.length > 0) {
                    htmlContent += '<div class="table-responsive"><table class="table table-sm table-bordered">';
                    htmlContent += '<thead><tr><th>Estudiante</th><th>Error</th><th>Detalles</th></tr></thead><tbody>';
                    
                    detalles.errores.forEach(error => {
                        htmlContent += `<tr>
                            <td>${error.estudiante_id}</td>
                            <td>${error.error}</td>
                            <td>${error.detalles}</td>
                        </tr>`;
                    });
                    
                    htmlContent += '</tbody></table></div>';
                }
            }
        }
        
        Swal.fire({
            icon: 'error',
            title: 'Error',
            html: htmlContent,
            width: '800px'
        });
    }

    // Función para guardar la asistencia
    function guardarAsistencia($card) {
        const claseIds = JSON.parse($card.attr('data-clase-ids'));
        if (!claseIds || claseIds.length === 0) {
            mostrarError('No se encontró el ID de la clase');
            return;
        }

        // Obtener todos los estudiantes con sus estados
        const asistencias = [];
        $card.find('tr').each(function() {
            const $row = $(this);
            const estudianteId = $row.find('.estado-asistencia').data('estudiante-id');
            const estado = $row.find('.estado-asistencia').val();
            
            if (estudianteId && estado) {
                asistencias.push({
                    estudiante_id: estudianteId,
                    presente: estado === 'presente',
                    justificado: $row.find('.justificacion-check').prop('checked'),
                    observaciones: $row.find('.observacion-input').val() || ''
                });
            }
        });

        if (asistencias.length === 0) {
            mostrarError('No hay registros de asistencia para guardar');
            return;
        }

        // Mostrar loading en el botón
        const $btnGuardar = $card.find('.guardar-todo');
        const btnTextoOriginal = $btnGuardar.html();
        $btnGuardar.html('<i class="fas fa-spinner fa-spin me-1"></i>Guardando...').prop('disabled', true);

        // Guardar asistencia para la primera clase
        $.ajax({
            url: `/guardar-asistencia/${claseIds[0]}/`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(asistencias),
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            }
        })
        .done(function(response) {
            if (response.success) {
                mostrarExito(response.message);
                // Actualizar contadores
                actualizarContadores($card);
                // Deshabilitar campos
                $card.find('select, input').prop('disabled', true);
                $btnGuardar.prop('disabled', true).html('<i class="fas fa-check me-1"></i>Guardado');
            } else {
                mostrarError(response.error, response);
                $btnGuardar.html(btnTextoOriginal).prop('disabled', false);
            }
        })
        .fail(function(jqXHR) {
            let mensaje = 'Error al guardar la asistencia';
            try {
                const response = JSON.parse(jqXHR.responseText);
                mensaje = response.error || mensaje;
            } catch (e) {
                mensaje = jqXHR.responseText || mensaje;
            }
            mostrarError(mensaje);
            $btnGuardar.html(btnTextoOriginal).prop('disabled', false);
        });
    }

    // Función para mostrar mensaje de éxito
    function mostrarExito(mensaje) {
        Swal.fire({
            icon: 'success',
            title: '¡Éxito!',
            text: mensaje,
            timer: 3000,
            showConfirmButton: false
        });
    }

    // Función para obtener el token CSRF
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
    
    // Función para inicializar eventos
    function inicializarEventos() {
        // Evento para marcar todos como presentes
        $('.marcar-todos-presentes').on('click', function() {
            const $card = $(this).closest('.card');
            
            // Marcar todos como presentes
            $card.find('.estado-asistencia').each(function() {
                $(this).val('presente').trigger('change');
            });
            
            // Desactivar justificaciones y observaciones
            $card.find('.justificacion-check').prop('checked', false).prop('disabled', true);
            $card.find('.observacion-input').val('').prop('disabled', true);
            
            // Actualizar contadores
            actualizarContadores($card);
        });

        // Evento para marcar todos como ausentes
        $('.marcar-todos-ausentes').on('click', function() {
            const $card = $(this).closest('.card');
            
            // Marcar todos como ausentes
            $card.find('.estado-asistencia').each(function() {
                $(this).val('ausente').trigger('change');
            });
            
            // Habilitar justificaciones y observaciones
            $card.find('.justificacion-check').prop('disabled', false);
            $card.find('.observacion-input').prop('disabled', false);
            
            // Actualizar contadores
            actualizarContadores($card);
        });

        // Evento para cambio de estado
        $('.estado-asistencia').on('change', function() {
            const $row = $(this).closest('tr');
            const estado = $(this).val();
            
            // Habilitar/deshabilitar justificación según el estado
            const $justificacion = $row.find('.justificacion-check');
            const $observacion = $row.find('.observacion-input');
            
            if (estado === 'ausente') {
                $justificacion.prop('disabled', false);
                $observacion.prop('disabled', false);
            } else {
                $justificacion.prop('checked', false).prop('disabled', true);
                $observacion.val('').prop('disabled', true);
            }
            
            // Actualizar contadores
            actualizarContadores($(this).closest('.card'));
        });

        // Evento para guardar asistencia
        $('.guardar-todo').on('click', function() {
            const $card = $(this).closest('.card');
            
            // Verificar si hay cambios sin guardar
            const sinRegistro = $card.find('.estado-asistencia').filter(function() {
                return !$(this).val();
            }).length;
            
            if (sinRegistro > 0) {
                Swal.fire({
                    title: '¿Guardar asistencia?',
                    text: `Hay ${sinRegistro} estudiantes sin registro de asistencia. ¿Desea continuar?`,
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Sí, guardar',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        guardarAsistencia($card);
                    }
                });
            } else {
                guardarAsistencia($card);
            }
        });
    }
    
    // Función para actualizar los contadores
    function actualizarContadores($card) {
        const total = $card.find('.estado-asistencia').length;
        const presentes = $card.find('.estado-asistencia').filter(function() {
            return $(this).val() === 'presente';
        }).length;
        const ausentes = $card.find('.estado-asistencia').filter(function() {
            return $(this).val() === 'ausente';
        }).length;
        const sinRegistro = $card.find('.estado-asistencia').filter(function() {
            return !$(this).val();
        }).length;

        $card.find('.presentes-count').text(presentes);
        $card.find('.ausentes-count').text(ausentes);
        $card.find('.sin-registro-count').text(sinRegistro);
    }
    
    // Función para cargar el historial de asistencia
    function cargarHistorialAsistencia(asignaturaId, filtros = {}) {
        const $tabla = $('#tabla-historial tbody');
        $tabla.html('<tr><td colspan="5" class="text-center"><i class="fas fa-spinner fa-spin"></i> Cargando historial...</td></tr>');

        // Construir la URL con los filtros
        let url = `/obtener-historial-asistencia/${asignaturaId}/`;
        const params = new URLSearchParams(filtros);
        if (Object.keys(filtros).length > 0) {
            url += `?${params.toString()}`;
        }

        $.get(url)
            .done(function(response) {
                if (response.success) {
                    if (response.asistencias && response.asistencias.length > 0) {
                        let html = '';
                        response.asistencias.forEach(asistencia => {
                            const fecha = new Date(asistencia.fecha_registro).toLocaleDateString('es-ES', {
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                            });
                            
                            html += `
                                <tr>
                                    <td>${fecha}</td>
                                    <td>${asistencia.estudiante_nombre}</td>
                                    <td>
                                        <span class="badge ${asistencia.presente ? 'bg-success' : 'bg-danger'}">
                                            ${asistencia.presente ? 'Presente' : 'Ausente'}
                                        </span>
                                    </td>
                                    <td>
                                        ${asistencia.justificado ? 
                                            '<span class="badge bg-info">Justificado</span>' : 
                                            '<span class="badge bg-secondary">Sin Justificar</span>'}
                                    </td>
                                    <td>${asistencia.observaciones || '-'}</td>
                                </tr>
                            `;
                        });
                        $tabla.html(html);
                    } else {
                        $tabla.html('<tr><td colspan="5" class="text-center">No hay registros de asistencia</td></tr>');
                    }
                } else {
                    mostrarError('Error al cargar el historial: ' + response.error);
                }
            })
            .fail(function() {
                mostrarError('Error de conexión al cargar el historial');
            });
    }

    // Inicializar eventos del historial
    function inicializarEventosHistorial() {
        // Manejar cambios en los filtros
        $('#mes-filtro, #estado-filtro, #estudiante-filtro').on('change', function() {
            const filtros = {
                mes: $('#mes-filtro').val(),
                estado: $('#estado-filtro').val(),
                estudiante: $('#estudiante-filtro').val()
            };
            cargarHistorialAsistencia(asignaturaIdActual, filtros);
        });

        // Cargar historial cuando se muestra la pestaña
        $('#historial-asistencia-tab').on('shown.bs.tab', function() {
            cargarHistorialAsistencia(asignaturaIdActual);
        });
    }

    // Exponer funciones globalmente
    window.asistenciaActions = {
        cargarAsistencia: cargarAsistencia
    };

    // Inicializar eventos del historial
    inicializarEventosHistorial();
}); 