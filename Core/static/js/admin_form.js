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
        const alertaError = document.getElementById('errorAlertAdmin');
        const listaErrores = document.getElementById('errorListAdmin');
        
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
    const password = document.getElementById('admin_password');
    const confirmPassword = document.getElementById('admin_confirm_password');

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
    const form = document.getElementById('crearAdminForm');
    console.log('Configurando formulario de administrador');
    
    if (form) {
        console.log('Formulario de administrador encontrado');
        form.addEventListener('submit', async function(event) {
            console.log('Formulario de administrador enviado');
            event.preventDefault();
            
            document.getElementById('errorAlertAdmin').style.display = 'none';
            const errores = [];

            // Validar RUT
            const rut = document.getElementById('admin_rut').value;
            const dv = document.getElementById('admin_div').value;
            if (!validarRut(rut, dv)) {
                errores.push('El RUT ingresado no es válido');
            }

            // Validar correo institucional
            const correo = document.getElementById('admin_correo').value;
            if (!validarCorreoInstitucional(correo)) {
                errores.push('El correo debe ser institucional (@gem.cl)');
            }

            // Validar fecha de nacimiento
            const fechaNacimiento = new Date(document.getElementById('admin_fecha_nacimiento').value);
            const hoy = new Date();
            const edad = hoy.getFullYear() - fechaNacimiento.getFullYear();
            
            if (edad < 21) {
                errores.push('El administrador debe ser mayor de 21 años');
            }

            // Validar contraseñas
            const password = document.getElementById('admin_password').value;
            const confirmPassword = document.getElementById('admin_confirm_password').value;
            if (password !== confirmPassword) {
                errores.push('Las contraseñas no coinciden');
            }
            if (password.length < 8) {
                errores.push('La contraseña debe tener al menos 8 caracteres');
            }

            // Validar rol administrativo
            const rol = document.getElementById('admin_rol');
            if (rol && !rol.value) {
                errores.push('Debe seleccionar un rol administrativo');
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
                    const modal = bootstrap.Modal.getInstance(document.getElementById('crearAdminModal'));
                    modal.hide();
                    
                    // Mostrar mensaje de éxito
                    mostrarMensajeExito('Administrador creado exitosamente');
                    
                    // Recargar la página después de un breve retraso
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    // Mostrar errores
                    mostrarErrores(data.errors.__all__ || ['Error al crear administrador']);
                }
            } catch (error) {
                console.error('Error:', error);
                mostrarErrores(['Error al procesar la solicitud']);
            }
        });
    }
}); 