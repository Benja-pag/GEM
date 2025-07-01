// Lógica para el cambio de tema (Modo Claro/Oscuro)
document.addEventListener('DOMContentLoaded', () => {
    const themeSwitcher = document.getElementById('theme-switcher');
    if (!themeSwitcher) return;

    const htmlEl = document.documentElement;
    const moonIcon = 'fa-moon';
    const sunIcon = 'fa-sun';

    // Función para aplicar el tema
    const setTema = (theme) => {
        htmlEl.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Actualizar el ícono del botón
        const icon = themeSwitcher.querySelector('i');
        if (theme === 'dark') {
            icon.classList.remove(moonIcon);
            icon.classList.add(sunIcon);
        } else {
            icon.classList.remove(sunIcon);
            icon.classList.add(moonIcon);
        }
    };

    // Listener para el click en el botón
    themeSwitcher.addEventListener('click', () => {
        const currentTheme = htmlEl.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTema(newTheme);
    });

    // Cargar el tema guardado al iniciar la página
    const temaGuardado = localStorage.getItem('theme') || 'light';
    setTema(temaGuardado);
});

// Funciones para manejo de estudiantes en curso detalle
function verDetalleEstudiante(estudianteId) {
    // Redirigir directamente a la página de detalle del estudiante
    window.location.href = `/estudiante/${estudianteId}/detalle/`;
}

function contactarEstudiante(email, telefono) {
    // Crear un modal o menú de opciones para contactar al estudiante
    let opciones = [];
    
    if (email && email !== 'None') {
        opciones.push(`📧 Enviar correo: ${email}`);
    }
    
    if (telefono && telefono !== 'None') {
        opciones.push(`📱 Llamar: ${telefono}`);
    }
    
    if (opciones.length === 0) {
        alert('No hay información de contacto disponible para este estudiante.');
        return;
    }
    
    // Mostrar opciones de contacto
    let mensaje = 'Opciones de contacto:\n\n' + opciones.join('\n');
    
    if (confirm(mensaje + '\n\n¿Deseas continuar?')) {
        // Si hay email, abrir cliente de correo
        if (email && email !== 'None') {
            window.location.href = `mailto:${email}?subject=Contacto desde el sistema escolar`;
        }
        // Si hay teléfono, intentar llamar
        else if (telefono && telefono !== 'None') {
            window.location.href = `tel:${telefono}`;
        }
    }
}

$(document).ready(function() {
    // Actualizar asistencia
    $('#actualizarAsistencia').on('click', function() {
        const $btn = $(this);
        const originalHtml = $btn.html();
        
        // Mostrar loading
        $btn.html('<i class="fas fa-spinner fa-spin me-1"></i>Actualizando...').prop('disabled', true);
        
        // Recargar la página
        location.reload();
    });
});
