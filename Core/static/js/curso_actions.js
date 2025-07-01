$(document).ready(function() {
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

    // Ver detalles del curso
    $(document).on('click', '.view-curso', function(e) {
        e.preventDefault();
        const cursoId = $(this).data('curso-id');
        verDetalleCurso(cursoId);
    });

    // Editar curso
    $(document).on('click', '.edit-curso', function(e) {
        e.preventDefault();
        const cursoId = $(this).data('curso-id');
        editarCurso(cursoId);
    });

    // Eliminar curso
    $(document).on('click', '.delete-curso', function(e) {
        e.preventDefault();
        const cursoId = $(this).data('curso-id');
        const row = $(this).closest('tr');
        confirmarEliminarCurso(cursoId, row);
    });
});

// Función para mostrar errores
function mostrarError(mensaje) {
    Swal.fire({
        icon: 'error',
        title: 'Error',
        text: mensaje
    });
}

// Función para ver detalles del curso
function verDetalleCurso(cursoId) {
    $.ajax({
        url: `/cursos/${cursoId}/data/`,
        type: 'GET',
        success: function(data) {
            if (data.success) {
                // Crear el contenido del modal
                let contenido = `
                    <div class="modal-body">
                        <h5 class="mb-3">Detalles del Curso ${data.nivel}°${data.letra}</h5>
                        
                        <div class="mb-3">
                            <h6>Profesor Jefe</h6>
                            <p>${data.profesor_jefe ? data.profesor_jefe.nombre : 'Sin profesor jefe asignado'}</p>
                        </div>
                        
                        <div class="mb-3">
                            <h6>Estudiantes (${data.estudiantes.length})</h6>
                            <ul class="list-group">
                                ${data.estudiantes.map(estudiante => `
                                    <li class="list-group-item">
                                        ${estudiante.nombre} - ${estudiante.rut}
                                    </li>
                                `).join('')}
                            </ul>
            </div>
            
                        <div class="mb-3">
                            <h6>Asignaturas (${data.asignaturas.length})</h6>
                            <ul class="list-group">
                                ${data.asignaturas.map(asignatura => `
                                    <li class="list-group-item">
                                        ${asignatura.nombre} - ${asignatura.docente}
                </li>
                                `).join('')}
            </ul>
                </div>
            </div>
        `;
        
                // Mostrar el modal con los detalles
                Swal.fire({
                    title: `Curso ${data.nivel}°${data.letra}`,
                    html: contenido,
                    width: '600px',
                    showConfirmButton: false,
                    showCloseButton: true
                });
            } else {
                mostrarError(data.error || 'No se pudieron cargar los detalles del curso');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            mostrarError('Error al cargar los detalles del curso');
        }
    });
}

// Función para editar curso
function editarCurso(cursoId) {
    // Primero obtener los datos actuales del curso
    $.ajax({
        url: `/cursos/${cursoId}/data/`,
        type: 'GET',
        success: function(data) {
            if (data.success) {
                // Crear el formulario de edición
                let formulario = `
                    <form id="editarCursoForm">
                        <div class="mb-3">
                            <label for="nivel" class="form-label">Nivel</label>
                            <input type="number" class="form-control" id="nivel" value="${data.nivel}" min="1" max="4" required>
                        </div>
                        <div class="mb-3">
                            <label for="letra" class="form-label">Letra</label>
                            <input type="text" class="form-control" id="letra" value="${data.letra}" maxlength="1" required>
                            <small class="text-muted">La letra debe ser entre A e I</small>
                </div>
                        <div class="mb-3">
                            <label for="profesor_jefe_id" class="form-label">Profesor Jefe</label>
                            <select class="form-select" id="profesor_jefe_id" required>
                                <option value="">-- Seleccione un profesor jefe --</option>
                                ${data.docentes_disponibles.map(docente => `
                                    <option value="${docente.id}" ${data.profesor_jefe && data.profesor_jefe.id === docente.id ? 'selected' : ''}>
                                        ${docente.nombre}
                                    </option>
                                `).join('')}
                            </select>
            </div>
                    </form>
                `;

                // Mostrar el modal de edición
                Swal.fire({
                    title: `Editar Curso ${data.nivel}°${data.letra}`,
                    html: formulario,
                    showCancelButton: true,
                    confirmButtonText: 'Guardar',
                    cancelButtonText: 'Cancelar',
                    preConfirm: () => {
                        // Validar y recoger los datos del formulario
                        const nivel = $('#nivel').val();
                        const letra = $('#letra').val().toUpperCase();
                        const profesorJefeId = $('#profesor_jefe_id').val();

                        // Validaciones
                        if (!nivel || nivel < 1 || nivel > 4) {
                            Swal.showValidationMessage('El nivel debe estar entre 1 y 4');
                            return false;
                        }
                        if (!letra || !/^[A-I]$/.test(letra)) {
                            Swal.showValidationMessage('La letra debe ser entre A e I');
                            return false;
                        }
                        if (!profesorJefeId) {
                            Swal.showValidationMessage('Debe seleccionar un profesor jefe');
                            return false;
                        }

                        return {
                            nivel: nivel,
                            letra: letra,
                            profesor_jefe_id: profesorJefeId
                        };
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        // Enviar los datos actualizados al servidor
                        $.ajax({
                            url: `/cursos/${cursoId}/update/`,
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
                                    mostrarError(response.error || 'Error al actualizar el curso');
                                }
                            },
                            error: function(xhr, status, error) {
                                console.error('Error:', error);
                                mostrarError('Error al actualizar el curso');
                            }
                        });
                    }
                });
            } else {
                mostrarError(data.error || 'Error al cargar los datos del curso');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            mostrarError('Error al cargar los datos del curso');
        }
    });
}

// Función para confirmar eliminación
function confirmarEliminarCurso(cursoId, row) {
    Swal.fire({
        title: '¿Estás seguro?',
        text: "Esta acción eliminará el curso y todos sus datos relacionados. Esta acción no se puede deshacer.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            eliminarCurso(cursoId, row);
        }
    });
}

// Función para eliminar curso
function eliminarCurso(cursoId, row) {
    $.ajax({
        url: `/cursos/${cursoId}/delete/`,
        type: 'POST',
        success: function(response) {
            if (response.success) {
                // Eliminar la fila de la tabla
                row.fadeOut(400, function() {
                    $(this).remove();
                    
                    // Si no quedan más filas, mostrar mensaje
                    if ($('table tbody tr').length === 0) {
                        $('table tbody').append(
                            '<tr><td colspan="6" class="text-center">No hay cursos registrados</td></tr>'
                        );
                    }
                });
                
                Swal.fire({
                    icon: 'success',
                    title: '¡Éxito!',
                    text: 'Curso eliminado exitosamente',
                    showConfirmButton: false,
                    timer: 1500
                });
            } else {
                mostrarError(response.error || 'Error al eliminar el curso');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            mostrarError('Error al eliminar el curso: ' + error);
        }
    });
}