// Funciones para manejar el CRUD de notas
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const selectorEvaluacion = document.getElementById('selector-evaluacion');
    const tablaNotas = document.getElementById('tabla-notas');

    // Configuración para las peticiones fetch
    const fetchConfig = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    };

    // Cargar notas cuando se selecciona una evaluación
    selectorEvaluacion.addEventListener('change', function() {
        if (this.value) {
            cargarNotas(this.value);
        } else {
            tablaNotas.innerHTML = '';
        }
    });

    // Función para cargar las notas de una evaluación
    function cargarNotas(evaluacionId) {
        fetch(`/api/evaluacion/${evaluacionId}/notas/`, {
            ...fetchConfig,
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            renderizarTablaNotas(data);
        })
        .catch(error => {
            mostrarMensaje('Error al cargar las notas', 'error');
            console.error('Error:', error);
        });
    }

    // Función para renderizar la tabla de notas
    function renderizarTablaNotas(data) {
        const tabla = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Estudiante</th>
                            <th>Nota</th>
                            <th>Fecha</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.map(nota => `
                            <tr data-nota-id="${nota.id}">
                                <td>${nota.estudiante_nombre}</td>
                                <td>
                                    <span class="nota-valor">${nota.nota}</span>
                                    <input type="number" class="form-control nota-input d-none" 
                                           value="${nota.nota}" min="1.0" max="7.0" step="0.1">
                                </td>
                                <td>${nota.fecha}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary editar-nota">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-success guardar-nota d-none">
                                        <i class="fas fa-save"></i>
                                    </button>
                                    <button class="btn btn-sm btn-danger eliminar-nota">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        tablaNotas.innerHTML = tabla;

        // Agregar event listeners para las acciones
        document.querySelectorAll('.editar-nota').forEach(btn => {
            btn.addEventListener('click', iniciarEdicion);
        });

        document.querySelectorAll('.guardar-nota').forEach(btn => {
            btn.addEventListener('click', guardarNota);
        });

        document.querySelectorAll('.eliminar-nota').forEach(btn => {
            btn.addEventListener('click', eliminarNota);
        });
    }

    // Función para iniciar la edición de una nota
    function iniciarEdicion(event) {
        const fila = event.target.closest('tr');
        const notaSpan = fila.querySelector('.nota-valor');
        const notaInput = fila.querySelector('.nota-input');
        const editarBtn = fila.querySelector('.editar-nota');
        const guardarBtn = fila.querySelector('.guardar-nota');

        notaSpan.classList.add('d-none');
        notaInput.classList.remove('d-none');
        editarBtn.classList.add('d-none');
        guardarBtn.classList.remove('d-none');
    }

    // Función para guardar una nota editada
    function guardarNota(event) {
        const fila = event.target.closest('tr');
        const notaId = fila.dataset.notaId;
        const nuevaNota = fila.querySelector('.nota-input').value;

        fetch(`/api/nota/${notaId}/`, {
            ...fetchConfig,
            method: 'PUT',
            body: JSON.stringify({
                nota: nuevaNota
            })
        })
        .then(response => {
            if (!response.ok) throw new Error('Error al guardar la nota');
            return response.json();
        })
        .then(data => {
            const notaSpan = fila.querySelector('.nota-valor');
            const notaInput = fila.querySelector('.nota-input');
            const editarBtn = fila.querySelector('.editar-nota');
            const guardarBtn = fila.querySelector('.guardar-nota');

            notaSpan.textContent = nuevaNota;
            notaSpan.classList.remove('d-none');
            notaInput.classList.add('d-none');
            editarBtn.classList.remove('d-none');
            guardarBtn.classList.add('d-none');

            mostrarMensaje('Nota actualizada correctamente', 'success');
        })
        .catch(error => {
            mostrarMensaje('Error al guardar la nota', 'error');
            console.error('Error:', error);
        });
    }

    // Función para eliminar una nota
    function eliminarNota(event) {
        if (!confirm('¿Está seguro de que desea eliminar esta nota?')) return;

        const fila = event.target.closest('tr');
        const notaId = fila.dataset.notaId;

        fetch(`/api/nota/${notaId}/`, {
            ...fetchConfig,
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) throw new Error('Error al eliminar la nota');
            fila.remove();
            mostrarMensaje('Nota eliminada correctamente', 'success');
        })
        .catch(error => {
            mostrarMensaje('Error al eliminar la nota', 'error');
            console.error('Error:', error);
        });
    }

    // Función para mostrar mensajes al usuario
    function mostrarMensaje(mensaje, tipo) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${tipo === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        tablaNotas.insertAdjacentElement('beforebegin', alertDiv);

        // Remover el mensaje después de 3 segundos
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }
}); 