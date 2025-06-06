document.addEventListener('DOMContentLoaded', function() {
    // Función para mostrar errores
    function mostrarErrores(errores) {
        const alertaError = document.querySelector('#crearCursoModal .alert-danger');
        if (Array.isArray(errores)) {
            alertaError.textContent = errores.join(', ');
        } else if (typeof errores === 'object') {
            alertaError.textContent = Object.values(errores).flat().join(', ');
        } else {
            alertaError.textContent = errores;
        }
        alertaError.style.display = 'block';
    }

    // Función para mostrar mensajes de éxito
    function mostrarMensajeExito(mensaje) {
        Swal.fire({
            icon: 'success',
            title: '¡Éxito!',
            text: mensaje,
            timer: 2000,
            showConfirmButton: false
        }).then(() => {
            window.location.reload();
        });
    }

    // Configurar el formulario
    const form = document.getElementById('crearCursoForm');
    console.log('Configurando formulario de curso');
    
    if (form) {
        console.log('Formulario de curso encontrado');
        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            console.log('Formulario de curso enviado');
            
            // Limpiar errores previos
            const alertaError = form.querySelector('.alert-danger');
            alertaError.style.display = 'none';
            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            
            // Validar campos
            const nivel = document.getElementById('nivel');
            const letra = document.getElementById('letra');
            const profesorJefe = document.getElementById('profesor_jefe_id');
            const errores = [];

            if (!nivel.value || nivel.value < 1 || nivel.value > 4) {
                errores.push('El nivel debe estar entre 1 y 4');
                nivel.classList.add('is-invalid');
            }

            if (!letra.value || !/^[A-B]$/i.test(letra.value)) {
                errores.push('La letra debe ser A o B');
                letra.classList.add('is-invalid');
            }

            if (!profesorJefe.value) {
                errores.push('Debe seleccionar un profesor jefe');
                profesorJefe.classList.add('is-invalid');
            }

            if (errores.length > 0) {
                mostrarErrores(errores);
                return;
            }

            try {
                // Preparar los datos del formulario
                const formData = new FormData(form);
                
                // Enviar el formulario
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Cerrar el modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('crearCursoModal'));
                    modal.hide();
                    
                    // Mostrar mensaje de éxito
                    mostrarMensajeExito('Curso creado exitosamente');
                } else {
                    // Mostrar errores
                    mostrarErrores(data.errors || 'Error al crear el curso');
                }
            } catch (error) {
                console.error('Error:', error);
                mostrarErrores('Error al procesar la solicitud');
            }
        });

        // Limpiar el formulario cuando se cierra el modal
        const modal = document.getElementById('crearCursoModal');
        modal.addEventListener('hidden.bs.modal', function() {
            form.reset();
            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            form.querySelector('.alert-danger').style.display = 'none';
        });
    }
}); 