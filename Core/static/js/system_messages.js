class GEMSystemMessage {
    static show(message, options = {}) {
        // Crear el overlay con opacidad 0
        const overlay = document.createElement('div');
        overlay.className = 'gem-system-message-overlay';
        overlay.style.opacity = '0';
        document.body.appendChild(overlay);

        // Crear el contenedor del mensaje
        const messageContainer = document.createElement('div');
        messageContainer.className = 'gem-system-message';
        messageContainer.style.opacity = '0';
        messageContainer.style.transform = 'translate(-50%, -60%)';

        // Agregar el ícono
        const iconContainer = document.createElement('div');
        iconContainer.className = 'icon-container';
        const icon = document.createElement('img');
        icon.src = '/static/img/icono_gem.png';
        icon.alt = 'GEM System Icon';
        iconContainer.appendChild(icon);
        messageContainer.appendChild(iconContainer);

        // Agregar el encabezado
        const header = document.createElement('div');
        header.className = 'message-header';
        header.textContent = 'Sistema GEM te informa:';
        messageContainer.appendChild(header);

        // Agregar el contenido del mensaje
        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = message;
        messageContainer.appendChild(content);

        // Agregar botones
        const actionsContainer = document.createElement('div');
        actionsContainer.className = 'message-actions';

        // Siempre agregar botón de confirmar
        const confirmButton = document.createElement('button');
        confirmButton.className = 'confirm-btn';
        confirmButton.textContent = options.confirmText || 'Aceptar';
        confirmButton.onclick = () => {
            this.close(messageContainer, overlay);
            if (options.onConfirm) options.onConfirm();
        };
        actionsContainer.appendChild(confirmButton);

        // Agregar botón de cancelar si es necesario
        if (options.showCancel) {
            const cancelButton = document.createElement('button');
            cancelButton.className = 'cancel-btn';
            cancelButton.textContent = options.cancelText || 'Cancelar';
            cancelButton.onclick = () => {
                this.close(messageContainer, overlay);
                if (options.onCancel) options.onCancel();
            };
            actionsContainer.appendChild(cancelButton);
        }

        messageContainer.appendChild(actionsContainer);
        document.body.appendChild(messageContainer);

        // Animar la entrada
        requestAnimationFrame(() => {
            overlay.style.opacity = '1';
            messageContainer.style.opacity = '1';
            messageContainer.style.transform = 'translate(-50%, -50%)';
        });

        // Cerrar con la tecla Escape
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                this.close(messageContainer, overlay);
                document.removeEventListener('keydown', escHandler);
                if (options.onCancel) options.onCancel();
            }
        };
        document.addEventListener('keydown', escHandler);

        // Cerrar al hacer clic en el overlay si está permitido
        if (options.closeOnOverlayClick !== false) {
            overlay.onclick = () => {
                this.close(messageContainer, overlay);
                if (options.onCancel) options.onCancel();
            };
        }
    }

    static close(messageContainer, overlay) {
        // Animar la salida
        messageContainer.style.opacity = '0';
        messageContainer.style.transform = 'translate(-50%, -60%)';
        overlay.style.opacity = '0';

        // Remover elementos después de la animación
        setTimeout(() => {
            messageContainer.remove();
            overlay.remove();
        }, 300);
    }

    // Método de conveniencia para mensajes informativos simples
    static info(message) {
        this.show(message);
    }

    // Método de conveniencia para confirmaciones
    static confirm(message, onConfirm, onCancel) {
        this.show(message, {
            showCancel: true,
            onConfirm,
            onCancel
        });
    }

    // Método de conveniencia para mensajes de éxito
    static success(message) {
        this.show(message, {
            confirmText: 'Entendido'
        });
    }

    // Método de conveniencia para mensajes de error
    static error(message) {
        this.show(message, {
            confirmText: 'Entendido'
        });
    }
} 