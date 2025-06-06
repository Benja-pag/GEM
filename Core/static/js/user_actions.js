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
    console.log('Token CSRF:', csrftoken); // Para depuración

    // Configurar AJAX para incluir el token CSRF
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Manejar el cambio de estado de usuario
    $('.toggle-user-status').click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const userId = $(this).data('user-id');
        const button = $(this);
        const row = button.closest('tr');
        const statusCell = row.find('td:nth-child(5) .badge');

        Swal.fire({
            title: '¿Estás seguro?',
            text: '¿Quieres cambiar el estado de este usuario?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, cambiar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `/users/${userId}/toggle-status/`,
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    success: function(response) {
                        if (response.success) {
                            if (response.is_active) {
                                button.removeClass('btn-danger').addClass('btn-success');
                                button.find('i').removeClass('fa-user-slash').addClass('fa-user-check');
                                statusCell.removeClass('bg-danger').addClass('bg-success').text('Activo');
                            } else {
                                button.removeClass('btn-success').addClass('btn-danger');
                                button.find('i').removeClass('fa-user-check').addClass('fa-user-slash');
                                statusCell.removeClass('bg-success').addClass('bg-danger').text('Inactivo');
                            }
                            button.data('is-active', response.is_active.toString());

                            Swal.fire({
                                icon: 'success',
                                title: '¡Éxito!',
                                text: `Usuario ${response.is_active ? 'activado' : 'desactivado'} exitosamente`,
                                timer: 2000,
                                showConfirmButton: false
                            });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: response.error || 'No se pudo cambiar el estado del usuario'
                            });
                        }
                    },
                    error: function(xhr, status, error) {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'Error al cambiar el estado del usuario: ' + error
                        });
                    }
                });
            }
        });
    });

    // Manejar la eliminación de usuarios
    $('.delete-user').on('click', function() {
        const userId = $(this).data('user-id');
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
                $.ajax({
                    url: `/users/${userId}/delete/`,
                    type: 'POST',
                    success: function(response) {
                        if (response.success) {
                            Swal.fire({
                                icon: 'success',
                                title: '¡Éxito!',
                                text: 'Usuario eliminado exitosamente'
                            }).then(() => {
                                location.reload();
                            });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: response.error
                            });
                        }
                    },
                    error: function(xhr, status, error) {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'Error al eliminar el usuario: ' + error
                        });
                    }
                });
            }
        });
    });

    // Manejar el envío del formulario de creación de curso
    $('#crearCursoForm').on('submit', function(e) {
        e.preventDefault();
        
        // Limpiar errores previos
        $('.is-invalid').removeClass('is-invalid');
        $('.invalid-feedback').remove();
        $('.alert').remove();
        
        const form = $(this);
        const profesorJefeSelect = $('#profesor_jefe_id');
        const profesorJefeId = profesorJefeSelect.val();
        
        // Logs detallados para depuración
        console.log('Formulario enviado');
        console.log('Select de profesor jefe:', profesorJefeSelect);
        console.log('Valor seleccionado:', profesorJefeId);
        console.log('HTML del select:', profesorJefeSelect.prop('outerHTML'));
        
        // Log detallado de cada opción
        profesorJefeSelect.find('option').each(function(index) {
            console.log(`Opción ${index}:`, {
                value: $(this).val(),
                text: $(this).text().trim(),
                selected: $(this).prop('selected'),
                dataNombre: $(this).data('nombre'),
                html: $(this).prop('outerHTML')
            });
        });
        
        // Validar que se haya seleccionado un profesor jefe
        if (!profesorJefeId) {
            profesorJefeSelect.addClass('is-invalid');
            profesorJefeSelect.after('<div class="invalid-feedback">Por favor seleccione un profesor jefe</div>');
            return;
        }

        // Crear objeto con los datos
        const formData = new FormData(form[0]);
        formData.append('action', 'crear_curso');
        formData.append('csrfmiddlewaretoken', csrftoken);
        
        console.log('Datos a enviar:', Object.fromEntries(formData));
        
        // Enviar el formulario
        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log('Respuesta del servidor:', response);
                if (response.success) {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Éxito!',
                        text: 'Curso creado exitosamente',
                        timer: 2000,
                        showConfirmButton: false
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    if (response.errors) {
                        if (response.errors.__all__) {
                            const errorDiv = $('<div>')
                                .addClass('alert alert-danger mb-3')
                                .text(response.errors.__all__[0]);
                            form.prepend(errorDiv);
                        } else {
                            Object.keys(response.errors).forEach(function(field) {
                                const input = $(`#${field}`);
                                input.addClass('is-invalid');
                                input.after(`<div class="invalid-feedback">${response.errors[field][0]}</div>`);
                            });
                        }
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error('Error en la petición:', error);
                console.error('Estado de la respuesta:', xhr.status);
                console.error('Respuesta del servidor:', xhr.responseText);
                
                if (xhr.status === 302) {
                    window.location.href = '/login/';
                    return;
                }
                
                const errorDiv = $('<div>')
                    .addClass('alert alert-danger mb-3')
                    .text('Error al procesar la solicitud: ' + error);
                form.prepend(errorDiv);
            }
        });
    });

    // Limpiar validación cuando se cierra el modal
    $('#crearCursoModal').on('hidden.bs.modal', function() {
        const form = $('#crearCursoForm');
        form.find('.is-invalid').removeClass('is-invalid');
        form.find('.invalid-feedback').remove();
        form.find('.alert').remove();
        form[0].reset();
    });
});

// Función para mostrar alertas
function showAlert(type, message) {
    const alertDiv = $('<div>')
        .addClass(`alert alert-${type} alert-dismissible fade show`)
        .attr('role', 'alert')
        .html(`
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `);
    
    $('#alertContainer').append(alertDiv);
    
    // Auto cerrar la alerta después de 5 segundos
    setTimeout(function() {
        alertDiv.alert('close');
    }, 5000);
}

// Manejar el envío del formulario de creación de estudiante
$('form[action="{% url \'admin_panel\' %}"]').on('submit', function(e) {
    e.preventDefault();
    
    // Limpiar errores previos
    $('.is-invalid').removeClass('is-invalid');
    $('.invalid-feedback').remove();
    $('.alert').remove();
    
    const form = $(this);
    const action = form.find('input[name="action"]').val();
    
    // Validar campos requeridos según el tipo de formulario
    let hasErrors = false;
    let prefix = '';
    
    switch(action) {
        case 'crear_estudiante':
            prefix = 'estudiante_';
            break;
        case 'crear_docente':
            prefix = 'docente_';
            break;
        case 'crear_administrador':
            prefix = 'admin_';
            break;
    }
    
    const requiredFields = ['nombre', 'apellido_paterno', 'apellido_materno', 'rut', 'div', 'correo', 'telefono', 'direccion', 'fecha_nacimiento', 'password', 'confirm_password'];
    
    requiredFields.forEach(function(field) {
        const input = $(`#${prefix}${field}`);
        if (!input.val()) {
            input.addClass('is-invalid');
            input.after(`<div class="invalid-feedback">Este campo es obligatorio</div>`);
            hasErrors = true;
        }
    });
    
    if (hasErrors) {
        return;
    }
    
    $.ajax({
        url: form.attr('action'),
        method: 'POST',
        data: form.serialize(),
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function(response) {
            if (response.success) {
                showAlert('success', response.message);
                $(`#${action}Modal`).modal('hide');
                setTimeout(function() {
                    window.location.reload();
                }, 1500);
            } else {
                if (response.errors) {
                    if (response.errors.__all__) {
                        const errorDiv = $('<div>')
                            .addClass('alert alert-danger mb-3')
                            .text(response.errors.__all__[0]);
                        form.prepend(errorDiv);
                    } else {
                        Object.keys(response.errors).forEach(function(field) {
                            const input = $(`#${prefix}${field}`);
                            input.addClass('is-invalid');
                            input.after(`<div class="invalid-feedback">${response.errors[field][0]}</div>`);
                        });
                    }
                }
            }
        },
        error: function(xhr, status, error) {
            const errorDiv = $('<div>')
                .addClass('alert alert-danger mb-3')
                .text('Error al procesar la solicitud: ' + error);
            form.prepend(errorDiv);
        }
    });
}); 