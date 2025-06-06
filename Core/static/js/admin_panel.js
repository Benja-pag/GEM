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