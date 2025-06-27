// Funciones del Chat

// Ajusta automáticamente la altura del textarea
function autoResizeTextarea(element) {
    element.style.height = 'auto';
    element.style.height = (element.scrollHeight) + 'px';
}

// Envía el mensaje al servidor
async function sendChatMessage(event) {
    event.preventDefault();
    
    const input = document.getElementById('chat-input');
    const button = document.getElementById('chat-submit');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    if (!input || !button) {
        console.error('Elementos del chat no encontrados');
        return;
    }

    const message = input.value.trim();
    if (!message) return;
    
    try {
        // Deshabilitar input y botón
        input.disabled = true;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        // Agregar mensaje del usuario al chat
        addChatMessage(message, 'user');
        
        // Enviar mensaje al servidor
        const response = await fetch('/api/ia/chat-publico/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                mensaje: message
            })
        });
        
        // Procesar respuesta
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `Error del servidor: ${response.status}`);
        }
        
        // Mostrar respuesta del sistema
        if (data && data.respuesta) {
            addChatMessage(data.respuesta, 'system');
        } else {
            throw new Error('Respuesta inválida del servidor');
        }
        
    } catch (error) {
        console.error('Error:', error);
        addChatMessage(
            'Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.',
            'system error'
        );
    } finally {
        // Restaurar estado de los elementos
        input.value = '';
        input.disabled = false;
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-paper-plane"></i>';
        input.focus();
        
        // Resetear altura del textarea
        autoResizeTextarea(input);
    }
}

// Agrega un mensaje al chat
function addChatMessage(message, type) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) {
        console.error('Contenedor de mensajes no encontrado');
        return;
    }

    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${type} mb-3`;
    
    const backgroundColor = type === 'user' ? 'bg-primary text-white' : 
                          type === 'system error' ? 'bg-danger text-white' : 
                          'bg-light';
    
    messageElement.innerHTML = `
        <div class="message-content ${backgroundColor} rounded p-2">
            <small class="text-${type === 'user' || type === 'system error' ? 'light' : 'muted'}">
                ${type === 'user' ? 'Tú' : 'Sistema'}
            </small>
            <p class="mb-0">${message}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Inicialización cuando el documento está listo
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');
    
    if (form && input) {
        // Enfocar el input al cargar
        input.focus();
        
        // Auto-resize del textarea
        input.addEventListener('input', function() {
            autoResizeTextarea(this);
        });
        
        // Manejar envío con Enter (pero permitir nueva línea con Shift+Enter)
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                form.dispatchEvent(new Event('submit'));
            }
        });
    }
}); 