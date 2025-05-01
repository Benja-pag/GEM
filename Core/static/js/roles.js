// Funciones específicas para cada rol

// Funciones del Administrador
const AdminFunctions = {
    // Gestión de Usuarios
    createUser: function(userData) {
        $.post('/core/users/create/', userData, function(response) {
            showNotification('Usuario creado exitosamente');
            location.reload();
        });
    },

    updateUser: function(userId, userData) {
        $.post(`/core/users/${userId}/update/`, userData, function(response) {
            showNotification('Usuario actualizado exitosamente');
            $('#editUserModal').modal('hide');
            location.reload();
        });
    },

    deleteUser: function(userId) {
        $.post(`/core/users/${userId}/delete/`, function(response) {
            showNotification('Usuario eliminado exitosamente');
            location.reload();
        });
    },

    // Gestión de Cursos
    createCourse: function(courseData) {
        $.post('/core/courses/create/', courseData, function(response) {
            showNotification('Curso creado exitosamente');
            location.reload();
        });
    },

    updateCourse: function(courseId, courseData) {
        $.post(`/core/courses/${courseId}/update/`, courseData, function(response) {
            showNotification('Curso actualizado exitosamente');
            $('#editCourseModal').modal('hide');
            location.reload();
        });
    },

    deleteCourse: function(courseId) {
        $.post(`/core/courses/${courseId}/delete/`, function(response) {
            showNotification('Curso eliminado exitosamente');
            location.reload();
        });
    }
};

// Funciones del Profesor
const TeacherFunctions = {
    // Gestión de Calificaciones
    addGrade: function(gradeData) {
        $.post('/core/grades/add/', gradeData, function(response) {
            showNotification('Calificación agregada exitosamente');
            $('#addGradeModal').modal('hide');
            location.reload();
        });
    },

    updateGrade: function(gradeId, gradeData) {
        $.post(`/core/grades/${gradeId}/update/`, gradeData, function(response) {
            showNotification('Calificación actualizada exitosamente');
            $('#editGradeModal').modal('hide');
            location.reload();
        });
    },

    // Gestión de Estudiantes
    viewStudentDetails: function(studentId) {
        $.get(`/core/students/${studentId}/details/`, function(data) {
            $('#studentDetailsModal .modal-body').html(data);
            $('#studentDetailsModal').modal('show');
        });
    },

    // Gestión de Material del Curso
    uploadMaterial: function(courseId, formData) {
        $.ajax({
            url: `/core/courses/${courseId}/upload-material/`,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                showNotification('Material subido exitosamente');
                location.reload();
            }
        });
    }
};

// Funciones del Estudiante
const StudentFunctions = {
    // Ver Calificaciones
    viewGrades: function(courseId) {
        $.get(`/core/courses/${courseId}/my-grades/`, function(data) {
            $('#gradesModal .modal-body').html(data);
            $('#gradesModal').modal('show');
        });
    },

    // Descargar Material
    downloadMaterial: function(materialId) {
        window.location.href = `/core/material/${materialId}/download/`;
    },

    // Ver Progreso
    viewProgress: function() {
        $.get('/core/my-progress/', function(data) {
            $('#progressModal .modal-body').html(data);
            $('#progressModal').modal('show');
        });
    }
};

// Exportar las funciones
window.AdminFunctions = AdminFunctions;
window.TeacherFunctions = TeacherFunctions;
window.StudentFunctions = StudentFunctions; 