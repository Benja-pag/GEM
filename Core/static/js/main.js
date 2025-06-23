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
