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

    // Función para mostrar/ocultar campos específicos según el tipo de usuario
    function toggleSpecificFields(tipoUsuario) {
        $('.estudiante-fields, .docente-fields, .administrativo-fields').hide();
        if (tipoUsuario === 'estudiante') {
            $('.estudiante-fields').show();
        } else if (tipoUsuario === 'docente') {
            $('.docente-fields').show();
        } else if (tipoUsuario === 'administrativo') {
            $('.administrativo-fields').show();
        }
    }

    // Manejar el cambio de tipo de usuario
    $('#edit-tipo-usuario').change(function() {
        toggleSpecificFields($(this).val());
    });

    // Manejar el clic en el botón de editar (usando delegación)
    $(document).on('click', '.edit-user', function(e) {
        e.preventDefault();
        const userId = $(this).data('user-id');
        console.log('ID del usuario:', userId);

        // Cargar los datos del usuario
        $.ajax({
            url: `/users/${userId}/data/`,
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    const userData = response.data;
                    console.log('Datos recibidos:', userData);
                    
                    // Llenar los campos del formulario con el ID correcto
                    $('#edit-user-id').val(userId);
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
            },
            error: function(xhr, status, error) {
                console.error('Error en la petición:', error);
                console.error('Respuesta del servidor:', xhr.responseText);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error al cargar los datos del usuario: ' + error
                });
            }
        });
    });

    // Manejar el envío del formulario de edición
    $('#editUserForm').submit(function(e) {
        e.preventDefault();
        const userId = $('#edit-user-id').val();
        const formData = new FormData(this);
        
        // Asegurarse de que el tipo de usuario se incluya
        if (!formData.has('tipo_usuario')) {
            formData.append('tipo_usuario', $('#edit-tipo-usuario').val());
        }
        
        // Asegurarse de que el ID del usuario se incluya
        formData.append('user_id', userId);

        $.ajax({
            url: `/users/${userId}/update/`,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    $('#editUserModal').modal('hide');
                    Swal.fire({
                        icon: 'success',
                        title: '¡Éxito!',
                        text: 'Usuario actualizado exitosamente',
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    console.error('Error en la respuesta:', response);
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: response.error || 'No se pudo actualizar el usuario'
                    });
                }
            },
            error: function(xhr, status, error) {
                console.error('Error en la petición:', error);
                console.error('Respuesta del servidor:', xhr.responseText);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error al actualizar el usuario: ' + error
                });
            }
        });
    });
}); 