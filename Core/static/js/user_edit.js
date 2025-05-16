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

    // Función para cargar los datos del usuario
    function loadUserData(userId) {
        $.ajax({
            url: `/users/${userId}/get_data/`,
            type: 'GET',
            success: function(response) {
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

                    // Ocultar el campo de tipo de usuario si no es administrador
                    const isAdmin = $('body').data('is-admin');
                    if (!isAdmin) {
                        $('#edit-tipo-usuario').closest('.mb-3').hide();
                    }

                    // Mostrar campos específicos según el tipo de usuario
                    toggleSpecificFields(userData.tipo_usuario);

                    // Llenar campos específicos según el tipo de usuario
                    if (userData.tipo_usuario === 'estudiante') {
                        $('#edit-contacto-emergencia').val(userData.contacto_emergencia);
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
            },
            error: function(xhr, status, error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error al cargar los datos del usuario: ' + error
                });
            }
        });
    }

    // Función para mostrar/ocultar campos específicos según el tipo de usuario
    function toggleSpecificFields(tipoUsuario) {
        // Ocultar todos los campos específicos primero
        $('.estudiante-fields').hide();
        $('.administrativo-fields').hide();

        // Mostrar los campos correspondientes al tipo de usuario
        if (tipoUsuario === 'estudiante') {
            $('.estudiante-fields').show();
        } else if (tipoUsuario === 'administrativo') {
            $('.administrativo-fields').show();
        }
    }

    // Manejar el cambio de tipo de usuario en el formulario de edición
    $('#edit-tipo-usuario').change(function() {
        toggleSpecificFields($(this).val());
    });

    // Manejar el clic en el botón de editar
    $('.edit-user').click(function() {
        const rutCompleto = $(this).closest('tr').find('td:first').text().trim();
        $('#edit-user-id').val(rutCompleto);
        loadUserData(rutCompleto);
    });

    // Manejar el envío del formulario de edición
    $('#editUserForm').submit(function(e) {
        e.preventDefault();
        const rutCompleto = $('#edit-user-id').val();
        
        // Crear un objeto FormData para enviar los datos
        const formData = new FormData(this);
        
        // Convertir FormData a objeto para enviar como JSON
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        // Si no es administrador, no enviar el tipo de usuario
        const isAdmin = $('body').data('is-admin');
        if (!isAdmin) {
            delete data['tipo_usuario'];
        }

        $.ajax({
            url: `/users/${rutCompleto}/update/`,
            type: 'POST',
            data: data,
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
                        // Forzar recarga de la página
                        window.location.href = window.location.href;
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: response.error || 'No se pudo actualizar el usuario'
                    });
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
                console.error('Response:', xhr.responseText);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error al actualizar el usuario: ' + error
                });
            }
        });
    });
}); 