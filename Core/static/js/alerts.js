// Reemplazar SweetAlert2 con GEMSystemMessage
window.Swal = {
    fire: function(config) {
        if (typeof config === 'string') {
            return GEMSystemMessage.info(config);
        }

        const message = config.text || config.html || config.title;
        
        if (config.icon === 'question' || config.showCancelButton) {
            return new Promise((resolve) => {
                GEMSystemMessage.confirm(
                    message,
                    () => resolve({ isConfirmed: true, value: true }),
                    () => resolve({ isConfirmed: false, value: false })
                );
            });
        } else {
            return new Promise((resolve) => {
                GEMSystemMessage.info(message);
                resolve({ isConfirmed: true });
            });
        }
    },
    showLoading: function() {
        // Mostrar un mensaje de carga
        GEMSystemMessage.info("Cargando...");
    },
    showValidationMessage: function(message) {
        // Mostrar mensaje de validación
        GEMSystemMessage.info(message);
    }
};

// Reemplazar alert nativo
window.alert = function(message) {
    GEMSystemMessage.info(message);
};

// Reemplazar Toastify
window.Toastify = function(config) {
    GEMSystemMessage.info(config.text);
    return {
        showToast: function() {}
    };
}; 