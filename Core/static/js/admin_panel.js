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
        $.get(`/core/user/${userId}/`, function(data) {
            $('#editUserModal .modal-body').html(data);
            $('#editUserModal').modal('show');
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

    // Configuración global de AJAX
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        error: handleAjaxError
    });
}); 