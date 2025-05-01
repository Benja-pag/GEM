function editarUsuario(id) {
    window.location.href = `/admin-panel/usuarios/${id}/editar/`;
}

function desactivarUsuario(id) {
    if (confirm('¿Está seguro de desactivar este usuario?')) {
        fetch(`/admin-panel/usuarios/${id}/cambiar-estado/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error al desactivar el usuario');
            }
        });
    }
}

function activarUsuario(id) {
    if (confirm('¿Está seguro de activar este usuario?')) {
        fetch(`/admin-panel/usuarios/${id}/cambiar-estado/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error al activar el usuario');
            }
        });
    }
}

function toggleAsignaturas(select) {
    console.log("toggleAsignaturas llamado con valor:", select.value); // Debug
    const asignaturasGroup = document.getElementById('asignaturas-group');
    if (!asignaturasGroup) {
        console.error("Elemento asignaturas-group no encontrado"); // Debug
        return;
    }
    
    if (select.value === 'profesor') {
        console.log("Mostrando asignaturas"); // Debug
        asignaturasGroup.style.display = 'block';
    } else {
        console.log("Ocultando asignaturas"); // Debug
        asignaturasGroup.style.display = 'none';
        // Desmarcar todas las asignaturas cuando no es profesor
        const checkboxes = asignaturasGroup.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => checkbox.checked = false);
    }
}

function limpiarFormulario(form) {
    form.reset();
    // Limpiar mensajes de error
    form.querySelectorAll('.is-invalid').forEach(input => {
        input.classList.remove('is-invalid');
    });
    form.querySelectorAll('.invalid-feedback').forEach(div => {
        div.remove();
    });
    // Ocultar asignaturas
    const asignaturasGroup = document.getElementById('asignaturas-group');
    if (asignaturasGroup) {
        asignaturasGroup.style.display = 'none';
    }
}

// Manejar el envío del formulario de creación de usuario
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar la visibilidad de asignaturas basada en el tipo de usuario seleccionado
    const tipoUsuarioSelect = document.getElementById('id_tipo_usuario');
    if (tipoUsuarioSelect) {
        console.log("Inicializando visibilidad de asignaturas"); // Debug
        toggleAsignaturas(tipoUsuarioSelect);
    }

    const form = document.getElementById('crearUsuarioForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("Formulario enviado"); // Debug
            
            // Limpiar mensajes de error previos
            form.querySelectorAll('.is-invalid').forEach(input => {
                input.classList.remove('is-invalid');
            });
            form.querySelectorAll('.invalid-feedback').forEach(div => {
                div.remove();
            });
            
            const formData = new FormData(form);
            
            // Agregar campos de contraseña ocultos
            const password = Math.random().toString(36).slice(-8); // Generar contraseña aleatoria
            formData.append('password1', password);
            formData.append('password2', password);
            
            console.log("Datos del formulario:", Object.fromEntries(formData)); // Debug
            
            fetch('/admin-panel/usuarios/crear/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                console.log("Respuesta recibida:", response); // Debug
                return response.json();
            })
            .then(data => {
                console.log("Datos recibidos:", data); // Debug
                if (data.success) {
                    // Mostrar mensaje de éxito
                    alert(data.message || 'Usuario creado exitosamente');
                    // Cerrar el modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('crearUsuarioModal'));
                    modal.hide();
                    // Recargar la página para mostrar el nuevo usuario
                    location.reload();
                } else {
                    // Mostrar errores del formulario
                    if (data.errors) {
                        Object.keys(data.errors).forEach(field => {
                            const input = form.querySelector(`[name="${field}"]`);
                            if (input) {
                                input.classList.add('is-invalid');
                                const errorDiv = document.createElement('div');
                                errorDiv.className = 'invalid-feedback';
                                errorDiv.textContent = data.errors[field];
                                input.parentNode.appendChild(errorDiv);
                            }
                        });
                    } else {
                        alert(data.message || 'Error al crear el usuario');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al procesar la solicitud');
            });
        });
    } else {
        console.error("Formulario no encontrado"); // Debug
    }
}); 