document.addEventListener('DOMContentLoaded', function() {
    // Función para validar RUT chileno
    function validarRut(rut, dv) {
        if (typeof rut !== 'string' || typeof dv !== 'string') return false;
        if (!/^[0-9]{7,8}$/.test(rut)) return false;
        if (!/^[0-9kK]{1}$/.test(dv)) return false;

        let suma = 0;
        let multiplo = 2;
        
        for (let i = rut.length - 1; i >= 0; i--) {
            suma += Number(rut[i]) * multiplo;
            multiplo = multiplo === 7 ? 2 : multiplo + 1;
        }

        const dvEsperado = 11 - (suma % 11);
        const dvCalculado = dvEsperado === 11 ? '0' : dvEsperado === 10 ? 'K' : String(dvEsperado);
        
        return dvCalculado.toLowerCase() === dv.toLowerCase();
    }

    // Función para validar el formato del correo institucional
    function validarCorreoInstitucional(correo) {
        return correo.endsWith('@gem.cl');
    }

    // Función para mostrar errores en el formulario
    function mostrarErrores(errores) {
        const alertaError = document.getElementById('errorAlertDocente');
        const listaErrores = document.getElementById('errorListDocente');
        
        if (!alertaError || !listaErrores) {
            console.error('No se encontraron elementos de error');
            return;
        }
        
        listaErrores.innerHTML = '';
        errores.forEach(error => {
            const li = document.createElement('li');
            li.textContent = error;
            listaErrores.appendChild(li);
        });
        
        alertaError.style.display = 'block';
    }

    // Función para mostrar mensajes de éxito
    function mostrarMensajeExito(mensaje) {
        const alertaExito = document.createElement('div');
        alertaExito.className = 'alert alert-success alert-dismissible fade show';
        alertaExito.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.getElementById('alertContainer').appendChild(alertaExito);
        
        setTimeout(() => {
            alertaExito.remove();
        }, 3000);
    }

    // Configurar validación de contraseñas
    const password = document.getElementById('docente_password');
    const confirmPassword = document.getElementById('docente_confirm_password');

    if (password && confirmPassword) {
        function validarContraseñas() {
            if (confirmPassword.value !== password.value) {
                confirmPassword.setCustomValidity('Las contraseñas no coinciden');
            } else {
                confirmPassword.setCustomValidity('');
            }
        }

        password.addEventListener('change', validarContraseñas);
        confirmPassword.addEventListener('keyup', validarContraseñas);
    }

    // Configurar el formulario
    const form = document.getElementById('crearDocenteForm');
    console.log('Configurando formulario de docente');
    
    if (form) {
        console.log('Formulario de docente encontrado');
        form.addEventListener('submit', async function(event) {
            console.log('Formulario de docente enviado');
            event.preventDefault();
            
            document.getElementById('errorAlertDocente').style.display = 'none';
            const errores = [];

            // Validar RUT
            const rut = document.getElementById('docente_rut').value;
            const dv = document.getElementById('docente_div').value;
            if (!validarRut(rut, dv)) {
                errores.push('El RUT ingresado no es válido');
            }

            // Validar correo institucional
            const correo = document.getElementById('docente_correo').value;
            if (!validarCorreoInstitucional(correo)) {
                errores.push('El correo debe ser institucional (@gem.cl)');
            }

            // Validar fecha de nacimiento
            const fechaNacimiento = new Date(document.getElementById('docente_fecha_nacimiento').value);
            const hoy = new Date();
            const edad = hoy.getFullYear() - fechaNacimiento.getFullYear();
            
            if (edad < 21) {
                errores.push('El docente debe ser mayor de 21 años');
            }

            // Validar contraseñas
            const password = document.getElementById('docente_password').value;
            const confirmPassword = document.getElementById('docente_confirm_password').value;
            if (password !== confirmPassword) {
                errores.push('Las contraseñas no coinciden');
            }
            if (password.length < 8) {
                errores.push('La contraseña debe tener al menos 8 caracteres');
            }

            // Validar especialidad
            const especialidad = document.getElementById('docente_especialidad');
            if (especialidad && !especialidad.value) {
                errores.push('Debe seleccionar una especialidad');
            }

            // Si hay errores, mostrarlos y activar validación de Bootstrap
            if (errores.length > 0 || !form.checkValidity()) {
                mostrarErrores(errores);
                form.classList.add('was-validated');
                return;
            }

            try {
                // Enviar el formulario usando fetch
                const formData = new FormData(form);
                
                // Manejar el checkbox es_profesor_jefe
                const esProfesorJefe = document.getElementById('docente_es_profesor_jefe');
                if (esProfesorJefe) {
                    formData.set('es_profesor_jefe', esProfesorJefe.checked ? 'true' : 'false');
                }

                const response = await fetch('/admin-panel/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Cerrar el modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('crearDocenteModal'));
                    modal.hide();
                    
                    // Mostrar mensaje de éxito
                    mostrarMensajeExito('Docente creado exitosamente');
                    
                    // Recargar la página después de un breve retraso
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    // Mostrar errores
                    mostrarErrores(data.errors.__all__ || ['Error al crear docente']);
                }
            } catch (error) {
                console.error('Error:', error);
                mostrarErrores(['Error al procesar la solicitud']);
            }
        });
    }
}); 