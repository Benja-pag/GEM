// Funciones para las herramientas de IA
let isProcessing = false;

// Función para generar reportes
async function generateIAReport(type) {
    if (isProcessing) return;
    
    const buttonId = `btn-report-${type}`;
    const button = document.querySelector(`button[onclick="generateIAReport('${type}')"]`);
    const originalHtml = button.innerHTML;
    
    try {
        isProcessing = true;
        showLoadingState(button);
        
        const response = await fetch('/api/ia/generar-reporte/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                tipo: type,
                curso_id: getCurrentCursoId(),
                contexto: await getContextData()
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccessToast('Reporte generado exitosamente');
            displayReport(data);
        } else {
            throw new Error(data.error || 'Error al generar el reporte');
        }
    } catch (error) {
        showErrorToast(error.message);
    } finally {
        isProcessing = false;
        hideLoadingState(button, originalHtml);
    }
}

// Función para generar sugerencias
async function generateIASuggestions(type) {
    if (isProcessing) return;
    
    const button = document.querySelector(`button[onclick="generateIASuggestions('${type}')"]`);
    const originalHtml = button.innerHTML;
    
    try {
        isProcessing = true;
        showLoadingState(button);
        
        const response = await fetch('/api/ia/generar-sugerencias/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                tipo: type,
                curso_id: getCurrentCursoId(),
                contexto: await getContextData()
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccessToast('Sugerencias generadas exitosamente');
            displaySuggestions(data);
        } else {
            throw new Error(data.error || 'Error al generar sugerencias');
        }
    } catch (error) {
        showErrorToast(error.message);
    } finally {
        isProcessing = false;
        hideLoadingState(button, originalHtml);
    }
}

// Función para generar comunicaciones
async function generateIACommunication(type) {
    if (isProcessing) return;
    
    const button = document.querySelector(`button[onclick="generateIACommunication('${type}')"]`);
    const originalHtml = button.innerHTML;
    
    try {
        isProcessing = true;
        showLoadingState(button);
        
        const response = await fetch('/api/ia/generar-comunicado/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                tipo: type,
                curso_id: getCurrentCursoId(),
                contexto: await getContextData()
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccessToast('Comunicado generado exitosamente');
            displayCommunication(data);
        } else {
            throw new Error(data.error || 'Error al generar comunicado');
        }
    } catch (error) {
        showErrorToast(error.message);
    } finally {
        isProcessing = false;
        hideLoadingState(button, originalHtml);
    }
}

// Funciones del Chat
async function sendChatMessage(event) {
    event.preventDefault();
    
    const input = document.getElementById('chat-input');
    const button = event.submitter;
    const message = input.value.trim();
    
    if (!message || isProcessing) return;
    
    try {
        isProcessing = true;
        input.disabled = true;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        // Agregar mensaje del usuario al chat
        addChatMessage(message, 'user');
        
        const response = await fetch('/api/ia/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                mensaje: message,
                curso_id: getCurrentCursoId(),
                contexto: await getContextData()
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            addChatMessage(data.respuesta, 'system');
        } else {
            throw new Error(data.error || 'Error al procesar el mensaje');
        }
    } catch (error) {
        showErrorToast(error.message);
    } finally {
        isProcessing = false;
        input.disabled = false;
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-paper-plane"></i>';
        input.value = '';
        input.focus();
    }
}

// Funciones de visualización
function displayReport(data) {
    const modalHtml = `
        <div class="modal fade" id="reportModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${data.titulo}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${formatReportContent(data)}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="exportReport('pdf')">
                            <i class="fas fa-file-pdf me-2"></i>Exportar PDF
                        </button>
                        <button type="button" class="btn btn-success" onclick="exportReport('excel')">
                            <i class="fas fa-file-excel me-2"></i>Exportar Excel
                        </button>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('reportModal'));
    modal.show();
    
    // Limpiar modal al cerrar
    document.getElementById('reportModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

function displaySuggestions(data) {
    const modalHtml = `
        <div class="modal fade" id="suggestionsModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Sugerencias: ${data.area}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${formatSuggestions(data)}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="applySuggestions()">
                            <i class="fas fa-check me-2"></i>Aplicar
                        </button>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('suggestionsModal'));
    modal.show();
    
    // Limpiar modal al cerrar
    document.getElementById('suggestionsModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

function displayCommunication(data) {
    const modalHtml = `
        <div class="modal fade" id="communicationModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${data.asunto}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label class="form-label">Contenido del comunicado:</label>
                            <textarea class="form-control" rows="8">${data.contenido}</textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="sendCommunication()">
                            <i class="fas fa-paper-plane me-2"></i>Enviar
                        </button>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('communicationModal'));
    modal.show();
    
    // Limpiar modal al cerrar
    document.getElementById('communicationModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Funciones auxiliares
function addChatMessage(message, type) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type} mb-3`;
    
    messageDiv.innerHTML = `
        <div class="message-content rounded p-2">
            <small class="text-muted">${type === 'user' ? 'Tú' : 'Asistente'}</small>
            <p class="mb-0">${message}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showLoadingState(button) {
    button.disabled = true;
    const icon = button.querySelector('i');
    const text = button.textContent.trim();
    button.innerHTML = `<i class="fas fa-spinner fa-spin"></i><br>${text}`;
}

function hideLoadingState(button, originalHtml) {
    button.disabled = false;
    button.innerHTML = originalHtml;
}

function showSuccessToast(message) {
    Toastify({
        text: message,
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "#28a745",
        stopOnFocus: true
    }).showToast();
}

function showErrorToast(message) {
    Toastify({
        text: message,
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "#dc3545",
        stopOnFocus: true
    }).showToast();
}

function formatReportContent(data) {
    let html = '';
    
    if (data.contenido) {
        html += '<div class="mb-4">';
        data.contenido.forEach(item => {
            html += `<p>${item}</p>`;
        });
        html += '</div>';
    }
    
    if (data.recomendaciones) {
        html += '<h6 class="text-primary mb-3">Recomendaciones:</h6>';
        html += '<ul class="list-group">';
        data.recomendaciones.forEach(rec => {
            html += `<li class="list-group-item">${rec}</li>`;
        });
        html += '</ul>';
    }
    
    return html;
}

function formatSuggestions(data) {
    let html = '<div class="list-group">';
    
    data.sugerencias.forEach(sug => {
        html += `
            <div class="list-group-item">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${sug.titulo}</h6>
                    <small class="text-muted">${sug.prioridad}</small>
                </div>
                <p class="mb-1">${sug.descripcion}</p>
            </div>
        `;
    });
    
    html += '</div>';
    
    if (data.recursos) {
        html += '<h6 class="mt-4 mb-3">Recursos sugeridos:</h6>';
        html += '<ul class="list-group">';
        data.recursos.forEach(rec => {
            html += `<li class="list-group-item">${rec}</li>`;
        });
        html += '</ul>';
    }
    
    return html;
}

async function getContextData() {
    return {
        curso_id: getCurrentCursoId(),
        periodo: getCurrentPeriodo(),
        profesor: getCurrentProfesor()
    };
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function getCurrentCursoId() {
    return document.getElementById('curso-id').value;
}

function getCurrentPeriodo() {
    return document.getElementById('periodo-actual').value;
}

function getCurrentProfesor() {
    return {
        id: document.getElementById('profesor-id').value,
        nombre: document.getElementById('profesor-nombre').value,
        rol: document.getElementById('profesor-rol').value
    };
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    // Guardar texto original de los botones
    document.querySelectorAll('.btn').forEach(button => {
        button.setAttribute('data-original-text', button.innerHTML);
    });
}); 