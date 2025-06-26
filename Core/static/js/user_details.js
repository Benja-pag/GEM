$(document).ready(function() {
    // Función para cargar los detalles del usuario
    function loadUserDetails(userId) {
        $.ajax({
            url: `/users/${userId}/data/`,
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    const userData = response.data;
                    
                    // Información Personal
                    $('#detail-nombre-completo').text(`${userData.nombre} ${userData.apellido_paterno} ${userData.apellido_materno}`);
                    $('#detail-rut').text(`${userData.rut}-${userData.div}`);
                    $('#detail-correo').text(userData.correo);
                    $('#detail-telefono').text(userData.telefono || 'No especificado');
                    $('#detail-direccion').text(userData.direccion || 'No especificada');
                    $('#detail-fecha-nacimiento').text(userData.fecha_nacimiento || 'No especificada');
                    
                    // Información del Sistema
                    $('#detail-tipo-usuario').text(userData.tipo_usuario.charAt(0).toUpperCase() + userData.tipo_usuario.slice(1));
                    
                    // Estado
                    const estadoBadge = $('#detail-estado');
                    if (userData.activador) {
                        estadoBadge.text('Activo').removeClass('bg-danger').addClass('bg-success');
                    } else {
                        estadoBadge.text('Inactivo').removeClass('bg-success').addClass('bg-danger');
                    }
                    
                    $('#detail-fecha-creacion').text(userData.fecha_creacion || 'No especificada');
                    
                    // Ocultar todos los paneles de información específica
                    $('#detail-estudiante-info, #detail-docente-info, #detail-administrativo-info').hide();
                    
                    // Mostrar información específica según el tipo de usuario
                    if (userData.tipo_usuario === 'estudiante') {
                        $('#detail-estudiante-info').show();
                        $('#detail-contacto-emergencia').text(userData.contacto_emergencia || 'No especificado');
                        $('#detail-curso').text(userData.curso ? userData.curso.nombre : 'No asignado');
                    } else if (userData.tipo_usuario === 'docente') {
                        $('#detail-docente-info').show();
                        $('#detail-especialidad').text(userData.especialidad ? userData.especialidad.nombre : 'No especificada');
                        $('#detail-es-profesor-jefe').text(userData.es_profesor_jefe ? 'Sí' : 'No');
                    } else if (userData.tipo_usuario === 'administrativo') {
                        $('#detail-administrativo-info').show();
                        $('#detail-rol-administrativo').text(userData.rol_administrativo || 'No especificado');
                    }
                    
                    // Mostrar el modal
                    $('#userDetailsModal').modal('show');
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

    // Manejar el clic en el botón de ver detalles (usando delegación)
    $(document).on('click', '.view-user', function(e) {
        e.preventDefault();
        const userId = $(this).data('user-id');
        loadUserDetails(userId);
    });
}); 