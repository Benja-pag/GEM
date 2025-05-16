// Este archivo contiene funciones generales de gestión de usuarios
$(document).ready(function() {
    // Función para validar el RUT chileno
    function validarRut(rut, dv) {
        let suma = 0;
        let multiplicador = 2;
        
        // Para cada dígito del RUT
        for (let i = rut.length - 1; i >= 0; i--) {
            suma += parseInt(rut.charAt(i)) * multiplicador;
            multiplicador = multiplicador === 7 ? 2 : multiplicador + 1;
        }
        
        let dvEsperado = 11 - (suma % 11);
        if (dvEsperado === 11) dvEsperado = '0';
        if (dvEsperado === 10) dvEsperado = 'K';
        
        return dvEsperado.toString() === dv.toUpperCase();
    }

    // Validar RUT al ingresar
    $('#rut, #edit-rut').on('blur', function() {
        const rut = $(this).val().replace(/\./g, '');
        const dv = $('#div, #edit-div').val();
        
        if (rut && dv) {
            if (!validarRut(rut, dv)) {
                Swal.fire({
                    icon: 'error',
                    title: 'RUT Inválido',
                    text: 'El RUT ingresado no es válido'
                });
                $(this).val('');
                $('#div, #edit-div').val('');
            }
        }
    });

    // Formatear RUT mientras se escribe
    $('#rut, #edit-rut').on('input', function() {
        let rut = $(this).val().replace(/\./g, '');
        if (rut.length > 0) {
            rut = rut.match(new RegExp('.{1,3}', 'g')).join('.');
            $(this).val(rut);
        }
    });

    // Validar correo electrónico
    function validarEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    $('#correo, #edit-correo').on('blur', function() {
        const email = $(this).val();
        if (email && !validarEmail(email)) {
            Swal.fire({
                icon: 'error',
                title: 'Correo Inválido',
                text: 'Por favor, ingrese un correo electrónico válido'
            });
            $(this).val('');
        }
    });

    // Validar teléfono
    function validarTelefono(telefono) {
        return /^\+?[\d\s-]{8,}$/.test(telefono);
    }

    $('#telefono, #edit-telefono').on('blur', function() {
        const telefono = $(this).val();
        if (telefono && !validarTelefono(telefono)) {
            Swal.fire({
                icon: 'error',
                title: 'Teléfono Inválido',
                text: 'Por favor, ingrese un número de teléfono válido'
            });
            $(this).val('');
        }
    });

    // Validar contraseña
    function validarPassword(password) {
        // Mínimo 8 caracteres, al menos una letra y un número
        return /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/.test(password);
    }

    $('#password').on('blur', function() {
        const password = $(this).val();
        if (password && !validarPassword(password)) {
            Swal.fire({
                icon: 'error',
                title: 'Contraseña Débil',
                text: 'La contraseña debe tener al menos 8 caracteres, una letra y un número'
            });
            $(this).val('');
        }
    });

    // Validar que las contraseñas coincidan
    $('#confirm_password').on('blur', function() {
        const password = $('#password').val();
        const confirmPassword = $(this).val();
        
        if (password && confirmPassword && password !== confirmPassword) {
            Swal.fire({
                icon: 'error',
                title: 'Contraseñas no coinciden',
                text: 'Las contraseñas ingresadas no coinciden'
            });
            $(this).val('');
        }
    });

    // Validar fecha de nacimiento
    function validarFechaNacimiento(fecha) {
        const fechaNac = new Date(fecha);
        const hoy = new Date();
        const edad = hoy.getFullYear() - fechaNac.getFullYear();
        const mes = hoy.getMonth() - fechaNac.getMonth();
        
        if (mes < 0 || (mes === 0 && hoy.getDate() < fechaNac.getDate())) {
            edad--;
        }
        
        return edad >= 18;
    }

    $('#fecha_nacimiento, #edit-fecha-nacimiento').on('blur', function() {
        const fecha = $(this).val();
        if (fecha && !validarFechaNacimiento(fecha)) {
            Swal.fire({
                icon: 'error',
                title: 'Edad Inválida',
                text: 'El usuario debe ser mayor de 18 años'
            });
            $(this).val('');
        }
    });
}); 