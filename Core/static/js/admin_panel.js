// Funciones para el Panel de Control

// Función para inicializar DataTables
function initDataTables() {
    if ($.fn.DataTable) {
        $('.table').DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json'
            },
            responsive: true,
            pageLength: 10,
            order: [[0, 'asc']],
            dom: 'Bfrtip',
            buttons: [
                'copy', 'csv', 'excel', 'pdf', 'print'
            ]
        });
    }
}

// Función para manejar las acciones de los botones
function initButtonActions() {
    // Botones de Editar Usuario
    $('.btn-edit-user').click(function() {
        const userId = $(this).data('user-id');
        openEditUserModal(userId);
    });

    // Botones de Eliminar Usuario
    $('.btn-delete-user').click(function() {
        const userId = $(this).data('user-id');
        confirmDeleteUser(userId);
    });

    // Botones de Ver Estudiantes
    $('.btn-view-students').click(function() {
        const courseId = $(this).data('course-id');
        openStudentsModal(courseId);
    });

    // Botones de Agregar Calificación
    $('.btn-add-grade').click(function() {
        const courseId = $(this).data('course-id');
        openAddGradeModal(courseId);
    });
}

// Función para manejar modales
function initModals() {
    // Modal de Edición de Usuario
    function openEditUserModal(userId) {
        $.get(`/users/${userId}/data/`, function(response) {
            if (response.success) {
                const userData = response.data;
                
                // Llenar los campos del formulario
                $('#edit-nombre').val(userData.nombre);
                $('#edit-apellido-paterno').val(userData.apellido_paterno);
                $('#edit-apellido-materno').val(userData.apellido_materno);
                $('#edit-rut').val(userData.rut);
                $('#edit-div').val(userData.div);
                $('#edit-correo').val(userData.correo);
                $('#edit-telefono').val(userData.telefono);
                $('#edit-direccion').val(userData.direccion);
                $('#edit-fecha-nacimiento').val(userData.fecha_nacimiento);
                $('#edit-tipo-usuario').val(userData.tipo_usuario);

                // Mostrar campos específicos según el tipo de usuario
                toggleSpecificFields(userData.tipo_usuario);

                // Llenar campos específicos según el tipo de usuario
                if (userData.tipo_usuario === 'estudiante') {
                    $('#edit-contacto-emergencia').val(userData.contacto_emergencia);
                    if (userData.curso) {
                        $('#edit-curso').val(userData.curso.id);
                    }
                } else if (userData.tipo_usuario === 'docente') {
                    if (userData.especialidad) {
                        $('#edit-especialidad').val(userData.especialidad.id);
                    }
                    $('#edit-es-profesor-jefe').prop('checked', userData.es_profesor_jefe);
                } else if (userData.tipo_usuario === 'administrativo') {
                    $('#edit-rol-administrativo').val(userData.rol_administrativo);
                }

                // Mostrar el modal
                $('#editUserModal').modal('show');
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: response.error || 'No se pudieron cargar los datos del usuario'
                });
            }
        }).fail(function(xhr, status, error) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error al cargar los datos del usuario: ' + error
            });
        });
    }

    // Modal de Confirmación de Eliminación
    function confirmDeleteUser(userId) {
        Swal.fire({
            title: '¿Estás seguro?',
            text: "Esta acción no se puede deshacer",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                deleteUser(userId);
            }
        });
    }

    // Modal de Lista de Estudiantes
    function openStudentsModal(courseId) {
        $.get(`/core/course/${courseId}/students/`, function(data) {
            $('#studentsModal .modal-body').html(data);
            $('#studentsModal').modal('show');
        });
    }

    // Modal de Agregar Calificación
    function openAddGradeModal(courseId) {
        $.get(`/core/course/${courseId}/add-grade/`, function(data) {
            $('#addGradeModal .modal-body').html(data);
            $('#addGradeModal').modal('show');
        });
    }
}

// Función para mostrar/ocultar campos específicos según el tipo de usuario
function toggleSpecificFields(tipoUsuario) {
    // Ocultar todos los campos específicos
    $('.estudiante-fields, .docente-fields, .administrativo-fields').hide();
    
    // Mostrar los campos correspondientes al tipo de usuario
    if (tipoUsuario === 'estudiante') {
        $('.estudiante-fields').show();
    } else if (tipoUsuario === 'docente') {
        $('.docente-fields').show();
    } else if (tipoUsuario === 'administrativo') {
        $('.administrativo-fields').show();
    }
}

// Función para manejar las notificaciones
function showNotification(message, type = 'success') {
    Toastify({
        text: message,
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: type === 'success' ? "#28a745" : "#dc3545",
        stopOnFocus: true
    }).showToast();
}

// Función para manejar errores AJAX
function handleAjaxError(xhr, status, error) {
    showNotification('Ha ocurrido un error: ' + error, 'error');
}

// Función para actualizar datos en tiempo real
function initRealTimeUpdates() {
    // Actualizar contadores cada 5 minutos
    setInterval(function() {
        $.get('/core/stats/', function(data) {
            $('#totalStudents').text(data.total_estudiantes);
            $('#totalTeachers').text(data.total_profesores);
            $('#activeCourses').text(data.cursos_activos);
        });
    }, 300000); // 5 minutos
}

// Inicialización cuando el documento está listo
$(document).ready(function() {
    initDataTables();
    initButtonActions();
    initModals();
    initRealTimeUpdates();

    // Event listener para el cambio de tipo de usuario
    $('#edit-tipo-usuario').change(function() {
        const tipoUsuario = $(this).val();
        toggleSpecificFields(tipoUsuario);
    });

    // Manejar el envío del formulario de edición
    $('#editUserForm').submit(function(e) {
        e.preventDefault();
        
        const userId = $('#edit-user-id').val();
        const formData = $(this).serialize();
        
        $.ajax({
            url: `/users/${userId}/update/`,
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    // Cerrar el modal
                    $('#editUserModal').modal('hide');
                    
                    // Mostrar mensaje de éxito
                    Swal.fire({
                        icon: 'success',
                        title: '¡Éxito!',
                        text: 'Usuario actualizado exitosamente',
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        // Recargar la página para mostrar los cambios
                        location.reload();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: response.error || 'Error al actualizar el usuario'
                    });
                }
            },
            error: function(xhr, status, error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error al actualizar el usuario: ' + error
                });
            }
        });
    });

    // Configuración global de AJAX
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        error: handleAjaxError
    });
}); 

// ===============================
// FUNCIONES PARA REPORTES ESPECÍFICOS DE ASISTENCIA
// ===============================

// Variables globales para los reportes específicos
let currentEstudianteId = null;
let currentCursoId = null;

// Variable global para cachear los datos de estudiantes
let estudiantesCache = null;
let estudiantesCacheTime = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutos en millisegundos

// Función para limpiar el cache de estudiantes
function limpiarCacheEstudiantes() {
    estudiantesCache = null;
    estudiantesCacheTime = null;
}

// Función para cargar tabla de estudiantes
function cargarTablaEstudiantes(forzarRecarga = false) {
    // Verificar si tenemos datos en cache y no han expirado
    const ahora = new Date().getTime();
    if (!forzarRecarga && estudiantesCache && estudiantesCacheTime && 
        (ahora - estudiantesCacheTime) < CACHE_DURATION) {
        // Usar datos del cache
        mostrarTablaEstudiantes(estudiantesCache);
        return;
    }
    
    // Verificar si ya hay una tabla cargada y no forzamos recarga
    if (!forzarRecarga && $('#tabla-estudiantes-container').find('table').length > 0) {
        return;
    }
    
    $('#tabla-estudiantes-container').html(`
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando estudiantes...</span>
            </div>
            <p class="mt-2">Cargando lista de estudiantes...</p>
        </div>
    `);
    
    $.get('/api/lista-estudiantes/', function(response) {
        if (response.success) {
            // Guardar en cache
            estudiantesCache = response.data;
            estudiantesCacheTime = new Date().getTime();
            
            mostrarTablaEstudiantes(response.data);
        } else {
            $('#tabla-estudiantes-container').html(`
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error al cargar estudiantes: ${response.error}
                </div>
            `);
        }
    }).fail(function() {
        $('#tabla-estudiantes-container').html(`
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error de conexión al cargar estudiantes
            </div>
        `);
    });
}

// Función para mostrar la tabla de estudiantes
function mostrarTablaEstudiantes(estudiantes) {
    let html = `
        <div class="table-responsive">
            <table class="table table-striped table-hover align-middle" id="tabla-estudiantes">
                <thead class="table-primary">
                    <tr>
                        <th><i class="fas fa-user me-1"></i>Nombre Completo</th>
                        <th><i class="fas fa-id-card me-1"></i>RUT</th>
                        <th><i class="fas fa-envelope me-1"></i>Correo Electrónico</th>
                        <th><i class="fas fa-graduation-cap me-1"></i>Curso</th>
                        <th><i class="fas fa-cogs me-1"></i>Acciones</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    estudiantes.forEach(function(estudiante) {
        html += `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="avatar-sm bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-2" style="width: 35px; height: 35px; font-size: 12px; font-weight: bold;">
                            ${estudiante.nombre.charAt(0)}${estudiante.apellido_paterno.charAt(0)}
                        </div>
                        <div>
                            <strong>${estudiante.nombre_completo}</strong>
                        </div>
                    </div>
                </td>
                <td>
                    <code>${estudiante.rut_completo}</code>
                </td>
                <td>
                    <small class="text-muted">
                        <i class="fas fa-envelope me-1"></i>${estudiante.correo}
                    </small>
                </td>
                <td>
                    <span class="badge bg-info">${estudiante.curso}</span>
                </td>
                <td>
                    <div class="btn-group" role="group">
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="descargarPDFEstudianteDirecto(${estudiante.id}, '${estudiante.nombre_completo}')"
                                title="Descargar PDF de Asistencia">
                            <i class="fas fa-file-pdf"></i> PDF
                        </button>
                        <button class="btn btn-sm btn-outline-info" 
                                onclick="verDetalleEstudiante(${estudiante.id})"
                                title="Ver detalle en pantalla">
                            <i class="fas fa-eye"></i> Detalle
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
        
        <div class="mt-3">
            <div class="row">
                <div class="col-md-6">
                    <p class="text-muted">
                        <i class="fas fa-info-circle me-1"></i>
                        Total de estudiantes: <strong>${estudiantes.length}</strong>
                    </p>
                </div>
                <div class="col-md-6 text-end">
                    <small class="text-muted">
                        Haz clic en "PDF" para descargar el reporte de asistencia
                    </small>
                </div>
            </div>
        </div>
    `;
    
    $('#tabla-estudiantes-container').html(html);
    
    // Inicializar DataTable si está disponible
    if ($.fn.DataTable) {
        // Destruir DataTable existente si existe
        if ($.fn.DataTable.isDataTable('#tabla-estudiantes')) {
            $('#tabla-estudiantes').DataTable().destroy();
        }
        
        $('#tabla-estudiantes').DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json'
            },
            responsive: true,
            pageLength: 25,
            order: [[0, 'asc']],
            columnDefs: [
                { orderable: false, targets: [4] } // Deshabilitar ordenamiento en la columna de acciones
            ],
            dom: 'Bfrtip',
            buttons: [
                {
                    extend: 'excel',
                    text: '<i class="fas fa-file-excel me-1"></i>Excel',
                    className: 'btn btn-sm btn-success'
                },
                {
                    extend: 'pdf',
                    text: '<i class="fas fa-file-pdf me-1"></i>PDF',
                    className: 'btn btn-sm btn-danger'
                }
            ]
        });
    }
}

// Función para cargar cursos en el select
function cargarCursos() {
    $.get('/api/cursos/', function(response) {
        if (response.success) {
            const select = $('#select-curso');
            select.empty();
            select.append('<option value="">Selecciona un curso...</option>');
            
            response.data.forEach(function(curso) {
                select.append(`<option value="${curso.id}">${curso.nivel}°${curso.letra} (${curso.total_estudiantes} estudiantes)</option>`);
            });
        }
    }).fail(function() {
        $('#select-curso').html('<option value="">Error al cargar cursos</option>');
    });
}

// Función para generar reporte de asistencia de estudiante específico
window.generarReporteAsistenciaEstudiante = function() {
    const estudianteId = $('#select-estudiante').val();
    const periodo = $('#periodo-estudiante').val();
    
    if (!estudianteId) {
        Swal.fire({
            icon: 'warning',
            title: 'Atención',
            text: 'Por favor selecciona un estudiante'
        });
        return;
    }
    
    currentEstudianteId = estudianteId;
    
    // Mostrar loading
    $('#reporte-asistencia-estudiante').html(`
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Generando reporte...</span>
            </div>
            <p class="mt-2">Generando reporte de asistencia...</p>
        </div>
    `);
    
    // Realizar petición AJAX
    $.get('/api/reporte-asistencia-estudiante/', {
        estudiante_id: estudianteId,
        periodo: periodo
    }, function(response) {
        if (response.success) {
            mostrarReporteEstudiante(response.data, response.periodo_info);
            $('#btn-pdf-estudiante').prop('disabled', false);
        } else {
            $('#reporte-asistencia-estudiante').html(`
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error al generar el reporte: ${response.error}
                </div>
            `);
        }
    }).fail(function() {
        $('#reporte-asistencia-estudiante').html(`
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error de conexión al generar el reporte
            </div>
        `);
    });
}

// Función para mostrar el reporte del estudiante
function mostrarReporteEstudiante(data, periodoInfo) {
    const estudiante = data.estudiante;
    const stats = data.estadisticas;
    
    // Determinar clase de estado
    let estadoClass = 'success';
    if (stats.estado === 'Crítico') estadoClass = 'danger';
    else if (stats.estado === 'En Riesgo') estadoClass = 'warning';
    
    let html = `
        <div class="row mb-4">
            <div class="col-12">
                <div class="card border-primary">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0"><i class="fas fa-user me-2"></i>${estudiante.nombre}</h5>
                        <small>RUT: ${estudiante.rut} | Curso: ${estudiante.curso}</small>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">📊 Estadísticas Generales</h6>
                                        <ul class="list-unstyled">
                                            <li><strong>Total de Clases:</strong> ${stats.total_registros}</li>
                                            <li><strong>Clases Presentes:</strong> ${stats.presentes}</li>
                                            <li><strong>Clases Ausentes:</strong> ${stats.ausentes}</li>
                                            <li><strong>Faltas Justificadas:</strong> ${stats.justificados}</li>
                                            <li><strong>Faltas Injustificadas:</strong> ${stats.injustificados}</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card bg-${estadoClass} text-white">
                                    <div class="card-body text-center">
                                        <h2 class="display-4">${stats.porcentaje_asistencia}%</h2>
                                        <h6>Porcentaje de Asistencia</h6>
                                        <span class="badge badge-light">${stats.estado}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Agregar tabla de asignaturas si hay datos
    if (data.asignaturas && data.asignaturas.length > 0) {
        html += `
            <div class="card mb-4">
                <div class="card-header">
                    <h6 class="mb-0"><i class="fas fa-book me-2"></i>Detalle por Asignatura</h6>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Asignatura</th>
                                    <th>Total Clases</th>
                                    <th>Presentes</th>
                                    <th>Ausentes</th>
                                    <th>Justificadas</th>
                                    <th>% Asistencia</th>
                                </tr>
                            </thead>
                            <tbody>
        `;
        
        data.asignaturas.forEach(function(asig) {
            let porcentajeClass = 'success';
            if (asig.porcentaje < 70) porcentajeClass = 'danger';
            else if (asig.porcentaje < 85) porcentajeClass = 'warning';
            
            html += `
                <tr>
                    <td>${asig.asignatura}</td>
                    <td>${asig.total_clases}</td>
                    <td>${asig.presentes}</td>
                    <td>${asig.ausentes}</td>
                    <td>${asig.justificados}</td>
                    <td><span class="badge bg-${porcentajeClass}">${asig.porcentaje}%</span></td>
                </tr>
            `;
        });
        
        html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }
    
    $('#reporte-asistencia-estudiante').html(html);
}

// Función para generar reporte de asistencia de curso específico
window.generarReporteAsistenciaCurso = function() {
    const cursoId = $('#select-curso').val();
    const periodo = $('#periodo-curso').val();
    
    if (!cursoId) {
        Swal.fire({
            icon: 'warning',
            title: 'Atención',
            text: 'Por favor selecciona un curso'
        });
        return;
    }
    
    currentCursoId = cursoId;
    
    // Mostrar loading
    $('#reporte-asistencia-curso').html(`
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Generando reporte...</span>
            </div>
            <p class="mt-2">Generando reporte de asistencia del curso...</p>
        </div>
    `);
    
    // Realizar petición AJAX
    $.get('/api/reporte-asistencia-curso/', {
        curso_id: cursoId,
        periodo: periodo
    }, function(response) {
        if (response.success) {
            mostrarReporteCurso(response.data, response.periodo_info);
            $('#btn-pdf-curso').prop('disabled', false);
        } else {
            $('#reporte-asistencia-curso').html(`
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error al generar el reporte: ${response.error}
                </div>
            `);
        }
    }).fail(function() {
        $('#reporte-asistencia-curso').html(`
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error de conexión al generar el reporte
            </div>
        `);
    });
};

// Función para mostrar el reporte del curso
function mostrarReporteCurso(data, periodoInfo) {
    const curso = data.curso;
    const stats = data.estadisticas;
    
    let html = `
        <div class="row mb-4">
            <div class="col-12">
                <div class="card border-primary">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0"><i class="fas fa-users me-2"></i>Curso ${curso.nombre}</h5>
                        <small>Total de Estudiantes: ${curso.total_estudiantes}</small>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-8">
                                <div class="row">
                                    <div class="col-md-4">
                                        <div class="card bg-success text-white text-center">
                                            <div class="card-body">
                                                <h3>${stats.estudiantes_buenos}</h3>
                                                <small>Buen Estado</small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="card bg-warning text-white text-center">
                                            <div class="card-body">
                                                <h3>${stats.estudiantes_riesgo}</h3>
                                                <small>En Riesgo</small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="card bg-danger text-white text-center">
                                            <div class="card-body">
                                                <h3>${stats.estudiantes_criticos}</h3>
                                                <small>Estado Crítico</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card bg-info text-white">
                                    <div class="card-body text-center">
                                        <h2 class="display-4">${stats.promedio_asistencia}%</h2>
                                        <h6>Promedio del Curso</h6>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Agregar tabla de estudiantes si hay datos
    if (data.estudiantes && data.estudiantes.length > 0) {
        html += `
            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0"><i class="fas fa-list me-2"></i>Detalle por Estudiante</h6>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Estudiante</th>
                                    <th>RUT</th>
                                    <th>Total</th>
                                    <th>Presentes</th>
                                    <th>Ausentes</th>
                                    <th>Justificadas</th>
                                    <th>% Asistencia</th>
                                    <th>Estado</th>
                                </tr>
                            </thead>
                            <tbody>
        `;
        
        data.estudiantes.forEach(function(est) {
            let estadoClass = 'success';
            if (est.estado === 'Crítico') estadoClass = 'danger';
            else if (est.estado === 'En Riesgo') estadoClass = 'warning';
            
            html += `
                <tr>
                    <td>${est.nombre}</td>
                    <td>${est.rut}</td>
                    <td>${est.total_clases}</td>
                    <td>${est.presentes}</td>
                    <td>${est.ausentes}</td>
                    <td>${est.justificados}</td>
                    <td><span class="badge bg-${estadoClass}">${est.porcentaje}%</span></td>
                    <td><span class="badge bg-${estadoClass}">${est.estado}</span></td>
                </tr>
            `;
        });
        
        html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }
    
    $('#reporte-asistencia-curso').html(html);
}

// Función para descargar PDF de asistencia de estudiante directamente desde la tabla
window.descargarPDFEstudianteDirecto = function(estudianteId, nombreEstudiante) {
    const periodo = 'ano_actual'; // Período fijo: año actual
    const url = `/pdf/reporte-asistencia-estudiante/?estudiante_id=${estudianteId}&periodo=${periodo}`;
    
    // Mostrar notificación de descarga
    Swal.fire({
        icon: 'info',
        title: 'Descargando PDF',
        text: `Generando reporte de asistencia para ${nombreEstudiante}`,
        timer: 2000,
        showConfirmButton: false
    });
    
    // Abrir en nueva ventana para descargar
    window.open(url, '_blank');
};



// Función para descargar PDF de asistencia de estudiante (mantener compatibilidad)
window.descargarPDFAsistenciaEstudiante = function() {
    if (!currentEstudianteId) {
        Swal.fire({
            icon: 'warning',
            title: 'Atención',
            text: 'Primero genera un reporte de estudiante'
        });
        return;
    }
    
    const periodo = $('#periodo-estudiante').val();
    const url = `/pdf/reporte-asistencia-estudiante/?estudiante_id=${currentEstudianteId}&periodo=${periodo}`;
    
    // Abrir en nueva ventana para descargar
    window.open(url, '_blank');
};

// Función para descargar PDF de asistencia de curso
window.descargarPDFAsistenciaCurso = function() {
    if (!currentCursoId) {
        Swal.fire({
            icon: 'warning',
            title: 'Atención',
            text: 'Primero genera un reporte de curso'
        });
        return;
    }
    
    const periodo = $('#periodo-curso').val();
    const url = `/pdf/reporte-asistencia-curso/?curso_id=${currentCursoId}&periodo=${periodo}`;
    
    // Abrir en nueva ventana para descargar
    window.open(url, '_blank');
};

// Inicializar los reportes específicos cuando se carga la pestaña
$(document).ready(function() {
    // Precargar datos de estudiantes en background si estamos en la página de reportes
    if (window.location.hash === '#reportes' || $('#reportes').hasClass('active')) {
        // Precargar en background después de un pequeño delay
        setTimeout(function() {
            cargarTablaEstudiantes();
        }, 500);
    }
    
    // Cargar datos cuando se activa la pestaña de asistencia
    $('button[data-bs-target="#asistencia-reporte"]').on('shown.bs.tab', function() {
        cargarCursos();
        // Cargar automáticamente la tabla de estudiantes si estamos en esa sub-pestaña
        setTimeout(function() {
            if ($('#asistencia-estudiante-tab').hasClass('active')) {
                cargarTablaEstudiantes();
            }
        }, 100);
    });
    
    // Cargar inmediatamente cuando se activa la sub-pestaña de estudiantes
    $('button[data-bs-target="#asistencia-estudiante"]').on('shown.bs.tab', function() {
        cargarTablaEstudiantes();
    });
    
    // Cargar tabla automáticamente cuando se hace clic en la pestaña principal de asistencia
    $('button[data-bs-target="#asistencia-reporte"]').on('click', function() {
        setTimeout(function() {
            if ($('#asistencia-estudiante-tab').hasClass('active')) {
                cargarTablaEstudiantes();
            }
        }, 100);
    });
    
    $('button[data-bs-target="#asistencia-curso"]').on('shown.bs.tab', function() {
        if ($('#select-curso option').length <= 1) {
            cargarCursos();
        }
    });
    
    // Limpiar cache cada 10 minutos para mantener datos frescos
    setInterval(limpiarCacheEstudiantes, 10 * 60 * 1000);
}); 