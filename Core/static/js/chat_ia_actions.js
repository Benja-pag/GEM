// Funciones para el chat con IA

document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const chatMessages = document.getElementById('chat-messages');
    const inputConsulta = document.getElementById('ia-consulta');
    const btnEnviar = document.getElementById('enviar-consulta');
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');

    // Función para agregar un mensaje al chat
    function agregarMensaje(mensaje, esIA = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${esIA ? 'ai-message' : 'user-message'} mb-2`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = `message-content p-2 rounded ${esIA ? 'bg-light' : 'bg-info text-white'}`;
        
        if (esIA) {
            contentDiv.innerHTML = `<i class="fas fa-robot text-info me-2"></i>${mensaje}`;
        } else {
            contentDiv.innerHTML = `<i class="fas fa-user text-white me-2"></i>${mensaje}`;
        }
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll al último mensaje
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Función para enviar consulta a la IA
    async function enviarConsulta(consulta) {
        // Agregar mensaje del usuario
        agregarMensaje(consulta, false);
        
        try {
            const response = await fetch('/api/chat-ia/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': obtenerCSRFToken()
                },
                body: JSON.stringify({
                    consulta: consulta,
                    asignatura_id: obtenerAsignaturaId()
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                agregarMensaje(data.respuesta, true);
            } else {
                throw new Error(data.error || 'Error al procesar la consulta');
            }
        } catch (error) {
            console.error('Error:', error);
            agregarMensaje('Lo siento, hubo un error al procesar tu consulta. Por favor, intenta de nuevo.', true);
        }
    }

    // Event Listeners
    btnEnviar.addEventListener('click', () => {
        const consulta = inputConsulta.value.trim();
        if (consulta) {
            enviarConsulta(consulta);
            inputConsulta.value = '';
        }
    });

    inputConsulta.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const consulta = inputConsulta.value.trim();
            if (consulta) {
                enviarConsulta(consulta);
                inputConsulta.value = '';
            }
        }
    });

    // Event Listeners para botones de sugerencias
    suggestionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const consulta = btn.dataset.query;
            enviarConsulta(consulta);
        });
    });

    // Función auxiliar para obtener el token CSRF
    function obtenerCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Función auxiliar para obtener el ID de la asignatura
    function obtenerAsignaturaId() {
        // Obtener el ID de la URL o de un data attribute
        const path = window.location.pathname;
        const matches = path.match(/\/asignatura\/(\d+)\//);
        return matches ? matches[1] : null;
    }
}); 