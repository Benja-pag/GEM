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
        const fecha = new Date(response.fecha);
        const diasSemana = {
            'LUNES': 'lunes',
            'MARTES': 'martes',
            'MIERCOLES': 'miércoles',
            'JUEVES': 'jueves',
            'VIERNES': 'viernes',
            'SABADO': 'sábado',
            'DOMINGO': 'domingo'
        };

        let html = `
            <div class="alert alert-primary">
                <h4 class="mb-0">
                    <i class="fas fa-calendar-day me-2"></i>
                    Asistencia para el ${formatearFecha(response.fecha)}
                </h4>
            </div>
        `;

        response.cursos.forEach(curso => {
            // Guardar los IDs de las clases como un atributo data en la tarjeta
            const claseIds = curso.clases.map(clase => clase.id);
            
            html += `
            <div class="card mb-4" data-clase-ids='${JSON.stringify(claseIds)}'>
                <div class="card-header bg-primary text-white">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            ${response.asignatura} - ${curso.curso}
                        </h5>
                        <div>
                            <button class="btn btn-light btn-sm me-2 marcar-todos-presentes">
                                <i class="fas fa-check-circle me-1"></i>Marcar Todos Presentes
                            </button>
                            <button class="btn btn-light btn-sm marcar-todos-ausentes">
                                <i class="fas fa-times-circle me-1"></i>Marcar Todos Ausentes
                            </button>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row mb-3">
                        <div class="col">
                            <h6>Bloques de Clase:</h6>
                            ${curso.clases.map(clase => `
                                <span class="badge bg-info me-2">
                                    <i class="fas fa-clock me-1"></i>${clase.horario} - ${clase.sala}
                                </span>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-md-3">
                            <div class="card bg-light">
                                <div class="card-body text-center">
                                    <h6>Total Estudiantes</h6>
                                    <h4>${curso.total_estudiantes}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-success text-white">
                                <div class="card-body text-center">
                                    <h6>Presentes</h6>
                                    <h4 class="presentes-count">0</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-danger text-white">
                                <div class="card-body text-center">
                                    <h6>Ausentes</h6>
                                    <h4 class="ausentes-count">0</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card bg-warning">
                                <div class="card-body text-center">
                                    <h6>Sin Registro</h6>
                                    <h4 class="sin-registro-count">${curso.total_estudiantes}</h4>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>RUT</th>
                                    <th>Nombre</th>
                                    <th>Estado</th>
                                    <th>Justificación</th>
                                    <th>Observaciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${curso.estudiantes.map(estudiante => `
                                    <tr>
                                        <td>${estudiante.rut}</td>
                                        <td>${estudiante.nombre}</td>
                                        <td>
                                            <select class="form-select estado-asistencia" 
                                                    data-estudiante-id="${estudiante.id}">
                                                <option value="">Sin registro</option>
                                                <option value="presente">Presente</option>
                                                <option value="ausente">Ausente</option>
                                            </select>
                                        </td>
                                        <td>
                                            <div class="form-check">
                                                <input type="checkbox" class="form-check-input justificacion-check"
                                                       data-estudiante-id="${estudiante.id}">
                                            </div>
                                        </td>
                                        <td>
                                            <input type="text" class="form-control observacion-input"
                                                   data-estudiante-id="${estudiante.id}">
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
    
    // Función para inicializar eventos
    function inicializarEventos() {
        // Evento para marcar todos como presentes
        $('.marcar-todos-presentes').on('click', function() {
            const $card = $(this).closest('.card');
            $card.find('.estado-asistencia').val('presente').trigger('change');
            actualizarContadores($card);
        });

        // Evento para marcar todos como ausentes
        $('.marcar-todos-ausentes').on('click', function() {
            const $card = $(this).closest('.card');
            $card.find('.estado-asistencia').val('ausente').trigger('change');
            actualizarContadores($card);
        });

        // Evento cuando cambia el estado de asistencia
        $('.estado-asistencia').on('change', function() {
            const $card = $(this).closest('.card');
            actualizarContadores($card);
        });

        // Evento para guardar toda la asistencia
        $('.guardar-todo').on('click', function() {
            const $card = $(this).closest('.card');
            const $btnGuardar = $(this);
            const btnTextoOriginal = $btnGuardar.html();
            
            // Obtener los IDs de las clases del curso
            const claseIds = JSON.parse($card.attr('data-clase-ids'));
            if (!claseIds || claseIds.length === 0) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Atención',
                    text: 'No hay clases disponibles para guardar asistencia'
                });
                return;
            }
            
            // Recolectar datos de todos los estudiantes
            const asistencias = [];
            let hayDatosParaGuardar = false;
            
            $card.find('tbody tr').each(function() {
                const $row = $(this);
                const estudianteId = $row.find('.estado-asistencia').data('estudiante-id');
                const estado = $row.find('.estado-asistencia').val();
                const justificado = $row.find('.justificacion-check').is(':checked');
                const observacion = $row.find('.observacion-input').val();

                // Solo incluir si hay un estado seleccionado
                if (estado) {
                    hayDatosParaGuardar = true;
                    asistencias.push({
                        estudiante_id: estudianteId,
                        presente: estado === 'presente',
                        justificado: justificado,
                        observaciones: observacion
                    });
                }
            });

            if (!hayDatosParaGuardar) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Atención',
                    text: 'No hay asistencias para guardar'
                });
                return;
            }

            // Mostrar loading
            $btnGuardar.html('<i class="fas fa-spinner fa-spin me-1"></i>Guardando...').prop('disabled', true);

            // Mostrar mensaje de guardando
            Swal.fire({
                title: 'Guardando asistencias',
                html: 'Por favor espera...',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });

            // Guardar todas las asistencias en una sola petición
            $.ajax({
                url: `/guardar-asistencia/${claseIds[0]}/`,
                method: 'POST',
                data: JSON.stringify(asistencias),
                contentType: 'application/json'
            })
            .done(function(response) {
                if (response.success) {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Éxito!',
                        text: response.message || 'Asistencias guardadas correctamente',
                        timer: 2000,
                        showConfirmButton: false
                    });
                    // Recargar los datos
                    cargarAsistencia(asignaturaIdActual);
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: response.error || 'Error al guardar las asistencias'
                    });
                }
            })
            .fail(function(jqXHR) {
                let mensaje = 'Error al guardar las asistencias';
                if (jqXHR.responseJSON && jqXHR.responseJSON.error) {
                    mensaje += ': ' + jqXHR.responseJSON.error;
                }
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: mensaje
                });
            })
            .always(function() {
                // Restaurar botón
                $btnGuardar.html(btnTextoOriginal).prop('disabled', false);
            });
        });
    }
    
    // Función para actualizar los contadores
    function actualizarContadores($card) {
        const total = $card.find('.estado-asistencia').length;
        const presentes = $card.find('.estado-asistencia[value="presente"]').length;
        const ausentes = $card.find('.estado-asistencia[value="ausente"]').length;
        const sinRegistro = total - presentes - ausentes;

        $card.find('.presentes-count').text(presentes);
        $card.find('.ausentes-count').text(ausentes);
        $card.find('.sin-registro-count').text(sinRegistro);
    }
    
    // Función para mostrar errores
    function mostrarError(mensaje) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: mensaje
        });
    }
    
    // Exponer funciones globalmente
    window.asistenciaActions = {
        cargarAsistencia: cargarAsistencia
    };
}); 