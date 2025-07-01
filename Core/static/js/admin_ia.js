// Variables globales
let chatHistory = [];

// Funciones del chat
function agregarMensajeChat(mensaje, tipo = 'user') {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${tipo}`;
    
    const timestamp = new Date().toLocaleTimeString();
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <small class="timestamp">${timestamp}</small>
            <p class="mb-0">${mensaje}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function enviarMensaje(event) {
    event.preventDefault();
    
    const input = document.getElementById('mensaje-input');
    const mensaje = input.value.trim();
    
    if (!mensaje) return;
    
    // Limpiar input
    input.value = '';
    
    // Mostrar mensaje del usuario
    agregarMensajeChat(mensaje, 'user');
    
    try {
        // Enviar mensaje al servidor
        const response = await fetch('/api/ia/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                message: mensaje,
                history: chatHistory
            })
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Error en la comunicación');
        }

        // Mostrar respuesta del asistente
        agregarMensajeChat(data.response, 'assistant');
        
        // Actualizar historial
        chatHistory.push(
            { role: 'user', content: mensaje },
            { role: 'assistant', content: data.response }
        );

    } catch (error) {
        agregarMensajeChat('Error: ' + error.message, 'error');
    }
}

function limpiarChat() {
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = '';
    chatHistory = [];
}

// Funciones de utilidad
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function mostrarError(mensaje) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Funciones para comunicados automáticos
async function generateIACommunication(type) {
    try {
        const loadingToast = showLoadingToast('Generando comunicado...');
        
        const response = await fetch('/api/ia/generate-communication/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ type: type })
        });

        if (!response.ok) throw new Error('Error al generar el comunicado');
        
        const data = await response.json();
        hideLoadingToast(loadingToast);
        
        if (data.success) {
            showSuccessToast('Comunicado generado exitosamente');
            // Mostrar el comunicado en el modal
            showCommunicationModal(data.communication);
        } else {
            showErrorToast(data.error || 'Error al generar el comunicado');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorToast('Error al generar el comunicado');
    }
}

// Funciones de utilidad
function showLoadingToast(message) {
    return Swal.fire({
        title: message,
        didOpen: () => {
            Swal.showLoading();
        },
        allowOutsideClick: false,
        allowEscapeKey: false,
        allowEnterKey: false
    });
}

function hideLoadingToast(toast) {
    toast.close();
}

function showSuccessToast(message) {
    Swal.fire({
        icon: 'success',
        title: message,
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000
    });
}

function showErrorToast(message) {
    Swal.fire({
        icon: 'error',
        title: 'Error',
        text: message,
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000
    });
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function displayReport(report) {
    // Implementar lógica para mostrar el reporte en la interfaz
    const reportContainer = document.getElementById('ia-report-container');
    if (reportContainer) {
        reportContainer.innerHTML = report;
    }
}

function showCommunicationModal(communication) {
    Swal.fire({
        title: 'Comunicado Generado',
        html: `
            <div class="text-start">
                <div class="mb-3">
                    <label class="form-label">Asunto</label>
                    <input type="text" class="form-control" value="${communication.subject}">
                </div>
                <div class="mb-3">
                    <label class="form-label">Contenido</label>
                    <textarea class="form-control" rows="5">${communication.content}</textarea>
                </div>
            </div>
        `,
        showCancelButton: true,
        confirmButtonText: 'Enviar',
        cancelButtonText: 'Cancelar',
        width: '600px'
    }).then((result) => {
        if (result.isConfirmed) {
            // Implementar lógica para enviar el comunicado
            sendCommunication(communication);
        }
    });
}

async function sendCommunication(communication) {
    try {
        const response = await fetch('/api/ia/send-communication/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(communication)
        });

        if (!response.ok) throw new Error('Error al enviar el comunicado');
        
        const data = await response.json();
        
        if (data.success) {
            showSuccessToast('Comunicado enviado exitosamente');
        } else {
            showErrorToast(data.error || 'Error al enviar el comunicado');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorToast('Error al enviar el comunicado');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    let messageHistory = [];

    // Función para agregar un mensaje al chat
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isUser ? 'user' : 'assistant'} p-2 mb-2 rounded`;
        messageDiv.style.backgroundColor = isUser ? '#e3f2fd' : '#f5f5f5';
        messageDiv.style.marginLeft = isUser ? 'auto' : '0';
        messageDiv.style.marginRight = !isUser ? 'auto' : '0';
        messageDiv.style.maxWidth = '80%';
        
        const textDiv = document.createElement('div');
        textDiv.textContent = message;
        messageDiv.appendChild(textDiv);
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Función para enviar mensaje al servidor
    async function sendMessage(message) {
        try {
            const response = await fetch('/admin/ia/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    message: message,
                    history: messageHistory
                })
            });

            const data = await response.json();
            
            if (data.success) {
                addMessage(data.response, false);
                messageHistory.push({
                    role: "assistant",
                    content: data.response
                });
            } else {
                addMessage("Lo siento, hubo un error al procesar tu mensaje.", false);
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage("Lo siento, ocurrió un error al comunicarse con el servidor.", false);
        }
    }

    // Manejador del formulario
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = messageInput.value.trim();
        
        if (message) {
            addMessage(message, true);
            messageHistory.push({
                role: "user",
                content: message
            });
            
            messageInput.value = '';
            sendMessage(message);
        }
    });

    // Mensaje inicial
    addMessage("¡Hola! Soy tu asistente del sistema GEM. ¿En qué puedo ayudarte?", false);
});

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Agregar contenedor para alertas si no existe
    if (!document.getElementById('alert-container')) {
        const alertContainer = document.createElement('div');
        alertContainer.id = 'alert-container';
        alertContainer.className = 'position-fixed top-0 start-50 translate-middle-x mt-3';
        alertContainer.style.zIndex = '9999';
        document.body.appendChild(alertContainer);
    }
}); 