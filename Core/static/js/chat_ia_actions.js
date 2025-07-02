// Funciones para el chat con IA

document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const chatMessages = document.getElementById('chat-messages');
    const inputConsulta = document.getElementById('ia-consulta');
    const btnEnviar = document.getElementById('enviar-consulta');
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');

    // Verificar si los elementos existen
    if (!chatMessages || !inputConsulta || !btnEnviar) {
        console.warn('Elementos del chat IA no encontrados');
        return;
    }

    // Función para agregar un mensaje al chat
    function agregarMensaje(mensaje, esIA = false, esCarga = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${esIA ? 'ai-message' : 'user-message'} mb-2`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = `message-content p-2 rounded ${esIA ? 'bg-light' : 'bg-info text-white'}`;
        
        if (esCarga) {
            contentDiv.innerHTML = `
                <i class="fas fa-robot text-info me-2"></i>
                <span class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </span>
                Procesando tu consulta...
            `;
        } else if (esIA) {
            // Convertir saltos de línea en <br> para mejor formato
            const mensajeFormateado = mensaje.replace(/\n/g, '<br>');
            contentDiv.innerHTML = `<i class="fas fa-robot text-info me-2"></i>${mensajeFormateado}`;
        } else {
            contentDiv.innerHTML = `<i class="fas fa-user text-white me-2"></i>${mensaje}`;
        }
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll al último mensaje
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }

    // Función para remover indicador de carga
    function removerIndicadorCarga(elemento) {
        if (elemento) {
            elemento.remove();
        }
    }

    // Función para enviar consulta a la IA
    async function enviarConsulta(consulta) {
        // Agregar mensaje del usuario
        agregarMensaje(consulta, false);
        
        // Agregar indicador de carga
        const indicadorCarga = agregarMensaje('', true, true);
        
        // Deshabilitar botón mientras procesa
        btnEnviar.disabled = true;
        inputConsulta.disabled = true;
        
        try {
            const asignaturaId = obtenerAsignaturaId();
            if (!asignaturaId) {
                throw new Error('No se pudo obtener el ID de la asignatura');
            }

            const response = await fetch('/api/chat-ia/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': obtenerCSRFToken()
                },
                body: JSON.stringify({
                    consulta: consulta,
                    asignatura_id: asignaturaId
                })
            });
            
            const data = await response.json();
            
            // Remover indicador de carga
            removerIndicadorCarga(indicadorCarga);
            
            if (data.success) {
                agregarMensaje(data.respuesta, true);
            } else {
                throw new Error(data.error || 'Error al procesar la consulta');
            }
        } catch (error) {
            console.error('Error:', error);
            
            // Remover indicador de carga
            removerIndicadorCarga(indicadorCarga);
            
            // Mostrar mensaje de error
            agregarMensaje('Lo siento, hubo un error al procesar tu consulta. Por favor, intenta de nuevo.', true);
        } finally {
            // Rehabilitar botón y input
            btnEnviar.disabled = false;
            inputConsulta.disabled = false;
            inputConsulta.focus();
        }
    }

    // Autoajuste de altura para el textarea (sin límite de altura)
    if (inputConsulta && inputConsulta.tagName === 'TEXTAREA') {
        inputConsulta.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
            this.style.overflowY = 'hidden';
        });
    }

    // Event Listeners
    btnEnviar.addEventListener('click', () => {
        const consulta = inputConsulta.value.trim();
        if (consulta) {
            enviarConsulta(consulta);
            inputConsulta.value = '';
            if (inputConsulta.tagName === 'TEXTAREA') {
                inputConsulta.style.height = 'auto';
            }
        }
    });

    inputConsulta.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const consulta = inputConsulta.value.trim();
            if (consulta) {
                enviarConsulta(consulta);
                inputConsulta.value = '';
                if (inputConsulta.tagName === 'TEXTAREA') {
                    inputConsulta.style.height = 'auto';
                }
            }
        }
    });

    // Event Listeners para botones de sugerencias
    suggestionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const consulta = btn.dataset.query;
            if (consulta) {
                enviarConsulta(consulta);
            }
        });
    });

    // Función auxiliar para obtener el token CSRF
    function obtenerCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!token) {
            console.error('Token CSRF no encontrado');
            return '';
        }
        return token.value;
    }

    // Función auxiliar para obtener el ID de la asignatura
    function obtenerAsignaturaId() {
        // Obtener el ID de la URL o de un data attribute
        const path = window.location.pathname;
        const matches = path.match(/\/asignatura\/(\d+)\//);
        return matches ? matches[1] : null;
    }

    // Agregar estilos CSS para el indicador de carga
    const style = document.createElement('style');
    style.textContent = `
        .typing-indicator {
            display: inline-flex;
            align-items: center;
            gap: 2px;
        }
        
        .typing-indicator span {
            width: 4px;
            height: 4px;
            border-radius: 50%;
            background-color: #007bff;
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-indicator span:nth-child(1) {
            animation-delay: -0.32s;
        }
        
        .typing-indicator span:nth-child(2) {
            animation-delay: -0.16s;
        }
        
        @keyframes typing {
            0%, 80%, 100% {
                transform: scale(0.8);
                opacity: 0.5;
            }
            40% {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        .chat-message .message-content {
            word-wrap: break-word;
            max-width: 100%;
        }
        
        .ai-message .message-content {
            background-color: #f8f9fa !important;
            border-left: 3px solid #007bff;
        }
        
        .user-message .message-content {
            background-color: #007bff !important;
            color: white !important;
        }
    `;
    document.head.appendChild(style);

    // Mensaje de bienvenida inicial
    if (chatMessages.children.length === 0) {
        agregarMensaje(`
            ¡Hola! Soy tu asistente IA. Puedo ayudarte con:
            <br>• Análisis de rendimiento
            <br>• Sugerencias de retroalimentación
            <br>• Estrategias de evaluación
            <br>• Recomendaciones personalizadas
            <br><br>¿En qué puedo ayudarte hoy?
        `, true);
    }
}); 