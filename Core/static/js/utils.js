// Utilidades y Validaciones

// Validación de Formularios
const FormValidation = {
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    validatePassword: function(password) {
        // Mínimo 8 caracteres, al menos una letra y un número
        const re = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
        return re.test(password);
    },

    validateDate: function(date) {
        const d = new Date(date);
        return d instanceof Date && !isNaN(d);
    },

    validateGrade: function(grade) {
        const num = parseFloat(grade);
        return !isNaN(num) && num >= 1.0 && num <= 7.0;
    }
};

// Formateo de Datos
const DataFormatting = {
    formatDate: function(date) {
        const d = new Date(date);
        return d.toLocaleDateString('es-CL');
    },

    formatGrade: function(grade) {
        return parseFloat(grade).toFixed(1);
    },

    formatCurrency: function(amount) {
        return new Intl.NumberFormat('es-CL', {
            style: 'currency',
            currency: 'CLP'
        }).format(amount);
    }
};

// Utilidades de UI
const UIUtils = {
    showLoading: function() {
        $('#loadingSpinner').show();
    },

    hideLoading: function() {
        $('#loadingSpinner').hide();
    },

    showError: function(message) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: message
        });
    },

    showSuccess: function(message) {
        Swal.fire({
            icon: 'success',
            title: '¡Éxito!',
            text: message
        });
    },

    confirmAction: function(message, callback) {
        Swal.fire({
            title: '¿Estás seguro?',
            text: message,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, continuar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                callback();
            }
        });
    }
};

// Utilidades de Archivo
const FileUtils = {
    validateFileSize: function(file, maxSize) {
        return file.size <= maxSize;
    },

    validateFileType: function(file, allowedTypes) {
        return allowedTypes.includes(file.type);
    },

    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
};

// Exportar las utilidades
window.FormValidation = FormValidation;
window.DataFormatting = DataFormatting;
window.UIUtils = UIUtils;
window.FileUtils = FileUtils; 