// Inicializar los eventos cuando el documento esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Configurar AJAX para incluir el token CSRF
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
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': csrftoken
        }
    });

    // Registrar eventos para los botones de acciones
    document.querySelectorAll('.view-curso').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const cursoId = this.getAttribute('data-curso-id');
            console.log('Ver curso:', cursoId);
            verDetalleCurso(cursoId);
        });
    });

    document.querySelectorAll('.edit-curso').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const cursoId = this.getAttribute('data-curso-id');
            console.log('Editar curso:', cursoId);
            editarCurso(cursoId);
        });
    });

    document.querySelectorAll('.delete-curso').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const cursoId = this.getAttribute('data-curso-id');
            const row = this.closest('tr');
            console.log('Eliminar curso:', cursoId);
            confirmarEliminarCurso(cursoId, row);
        });
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
    console.log('Cargando detalles del curso:', cursoId);
    $.ajax({
        url: `/cursos/${cursoId}/data/`,
        type: 'GET',
        success: function(data) {
            console.log('Datos recibidos:', data);
            if (data && data.success) {
                Swal.fire({
                    title: false,
                    html: `
                        <div class="card shadow">
                            <div class="card-header bg-primary text-white">
                                <h5 class="mb-0">
                                    <i class="fas fa-chalkboard"></i> 
                                    Curso ${data.nivel}°${data.letra}
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="row mb-3">
                                    <div class="col-12">
                                        <div class="d-flex align-items-center mb-3">
                                            <div class="rounded-circle bg-info text-white p-3 me-3">
                                                <i class="fas fa-user-tie fa-2x"></i>
                                            </div>
                                            <div>
                                                <h6 class="mb-1">Profesor Jefe</h6>
                                                <p class="mb-0 text-muted">
                                                    ${data.profesor_jefe ? data.profesor_jefe.nombre : 'Sin profesor jefe asignado'}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="card bg-light mb-3">
                                            <div class="card-body text-center">
                                                <i class="fas fa-users fa-2x text-primary mb-2"></i>
                                                <h5 class="card-title">${data.total_estudiantes || 0}</h5>
                                                <p class="card-text text-muted">Estudiantes</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="card bg-light mb-3">
                                            <div class="card-body text-center">
                                                <i class="fas fa-book fa-2x text-warning mb-2"></i>
                                                <h5 class="card-title">${data.total_asignaturas || 0}</h5>
                                                <p class="card-text text-muted">Asignaturas</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `,
                    showConfirmButton: true,
                    confirmButtonText: 'Cerrar',
                    confirmButtonColor: '#3085d6',
                    width: '600px',
                    padding: '0'
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data?.error || 'No se pudieron cargar los detalles del curso'
                });
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error al cargar los detalles del curso'
            });
        }
    });
}

// Función para editar curso
function editarCurso(cursoId) {
    console.log('Cargando formulario de edición:', cursoId);
    $.ajax({
        url: `/cursos/${cursoId}/data/`,
        type: 'GET',
        success: function(data) {
            console.log('Datos para edición:', data);
            if (data && data.success) {
                const docentesOptions = data.docentes_disponibles ? 
                    data.docentes_disponibles.map(docente => `
                        <option value="${docente.id}" 
                            ${data.profesor_jefe && data.profesor_jefe.id === docente.id ? 'selected' : ''}>
                            ${docente.nombre}
                        </option>
                    `).join('') : '';

                Swal.fire({
                    title: false,
                    html: `
                        <div class="card shadow">
                            <div class="card-header bg-warning">
                                <h5 class="mb-0">
                                    <i class="fas fa-edit"></i> 
                                    Editar Curso ${data.nivel}°${data.letra}
                                </h5>
                            </div>
                            <div class="card-body">
                                <form id="editarCursoForm">
                                    <div class="alert alert-danger" id="editCursoErrors" style="display: none;"></div>
                                    
                                    <div class="mb-3">
                                        <label for="nivel" class="form-label">
                                            <i class="fas fa-layer-group"></i> Nivel
                                        </label>
                                        <input type="number" class="form-control" id="nivel" 
                                               value="${data.nivel}" min="1" max="4" required>
                                        <div class="form-text">El nivel debe estar entre 1 y 4</div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="letra" class="form-label">
                                            <i class="fas fa-font"></i> Letra
                                        </label>
                                        <input type="text" class="form-control" id="letra" 
                                               value="${data.letra}" maxlength="1" required>
                                        <div class="form-text">La letra debe ser entre A e I</div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="profesor_jefe_id" class="form-label">
                                            <i class="fas fa-user-tie"></i> Profesor Jefe
                                        </label>
                                        <select class="form-select" id="profesor_jefe_id">
                                            <option value="">-- Sin profesor jefe --</option>
                                            ${docentesOptions}
                                        </select>
                                    </div>
                                </form>
                            </div>
                        </div>
                    `,
                    showCancelButton: true,
                    confirmButtonText: 'Guardar',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#198754',
                    cancelButtonColor: '#dc3545',
                    width: '600px',
                    padding: '0',
                    preConfirm: () => {
                        const nivel = document.getElementById('nivel').value;
                        const letra = document.getElementById('letra').value.toUpperCase();
                        const profesorJefeId = document.getElementById('profesor_jefe_id').value;

                        // Validaciones
                        if (!nivel || nivel < 1 || nivel > 4) {
                            Swal.showValidationMessage('El nivel debe estar entre 1 y 4');
                            return false;
                        }
                        if (!letra || !/^[A-I]$/.test(letra)) {
                            Swal.showValidationMessage('La letra debe ser entre A e I');
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
                        actualizarCurso(cursoId, result.value);
                    }
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data?.error || 'No se pudieron cargar los datos del curso'
                });
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error al cargar los datos del curso'
            });
        }
    });
}

// Función para actualizar el curso
function actualizarCurso(cursoId, formData) {
    $.ajax({
        url: `/cursos/${cursoId}/update/`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(data) {
            if (data && data.success) {
                // Actualizar la fila en la tabla
                const row = document.querySelector(`.view-curso[data-curso-id="${cursoId}"]`).closest('tr');
                row.querySelector('td:first-child').innerHTML = `<span class="badge bg-primary">${formData.nivel}°${formData.letra}</span>`;
                
                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: data.message || 'Curso actualizado exitosamente',
                    showConfirmButton: false,
                    timer: 1500
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data?.errors ? data.errors.join('\n') : 'Error al actualizar el curso'
                });
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error al actualizar el curso'
            });
        }
    });
}

// Función para confirmar eliminación de curso
function confirmarEliminarCurso(cursoId, row) {
    Swal.fire({
        title: '¿Estás seguro?',
        text: "Esta acción no se puede deshacer",
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
        success: function(data) {
            if (data && data.success) {
                // Eliminar la fila de la tabla
                row.remove();
                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: data.message || 'Curso eliminado exitosamente',
                    showConfirmButton: false,
                    timer: 1500
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data?.error || 'No se pudo eliminar el curso'
                });
            }
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error al eliminar el curso'
            });
        }
    });
}