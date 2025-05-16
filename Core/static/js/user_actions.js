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

    // Manejar el cambio de estado de usuario
    $('.toggle-user-status').click(function() {
        const userId = $(this).data('user-id');
        const button = $(this);
        const statusCell = button.closest('tr').find('td:nth-child(5)');

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
                    url: `/users/${userId}/toggle_status/`,
                    type: 'POST',
                    success: function(response) {
                        if (response.success) {
                            // Actualizar el botón y el estado en la tabla
                            if (response.is_active) {
                                button.removeClass('btn-danger').addClass('btn-success');
                                button.find('i').removeClass('fa-user-slash').addClass('fa-user-check');
                                statusCell.text('Activo');
                            } else {
                                button.removeClass('btn-success').addClass('btn-danger');
                                button.find('i').removeClass('fa-user-check').addClass('fa-user-slash');
                                statusCell.text('Inactivo');
                            }
                            // Actualizar el atributo data-is-active
                            button.data('is-active', response.is_active.toString());

                            Swal.fire({
                                icon: 'success',
                                title: '¡Éxito!',
                                text: `Usuario ${response.is_active ? 'activado' : 'desactivado'} exitosamente`
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
}); 