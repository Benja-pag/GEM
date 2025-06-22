# Panel de Estudiante Modular

Este directorio contiene los componentes modulares del panel de estudiante del sistema GEM.

## Estructura de Archivos

### Componentes Principales

- **`header.html`** - Encabezado con información personal del estudiante
- **`summary_cards.html`** - Tarjetas de resumen con estadísticas
- **`navigation_tabs.html`** - Pestañas de navegación principales

### Pestañas de Contenido

- **`tab_asignaturas.html`** - Lista de asignaturas inscritas
- **`tab_horario.html`** - Horario semanal del estudiante
- **`tab_calificaciones.html`** - Sistema de calificaciones por asignatura
- **`tab_asistencia.html`** - Control de asistencia y estadísticas
- **`tab_calendario.html`** - Calendario escolar y eventos
- **`tab_comunicacion.html`** - Chat y foros de discusión
- **`tab_electivos.html`** - Gestión de electivos disponibles

### Recursos

- **`scripts.html`** - JavaScript y estilos CSS personalizados

## Archivo Principal

- **`student_panel_modular.html`** - Archivo principal que incluye todos los componentes

## Uso

### Para usar el panel modular:

1. **Acceso directo**: `/estudiante-panel-modular/`
2. **Vista original**: `/estudiante-panel/`

### Para incluir componentes en otros templates:

```html
{% include 'student/header.html' %}
{% include 'student/summary_cards.html' %}
{% include 'student/tab_asignaturas.html' %}
```

## Ventajas de la Modularización

### ✅ **Mantenibilidad**
- Cada componente es independiente y fácil de modificar
- Cambios en una pestaña no afectan a las demás
- Código más organizado y legible

### ✅ **Reutilización**
- Los componentes pueden usarse en otros templates
- Fácil creación de nuevas pestañas
- Componentes intercambiables

### ✅ **Desarrollo en Equipo**
- Múltiples desarrolladores pueden trabajar en diferentes componentes
- Menos conflictos de merge
- Especialización por funcionalidad

### ✅ **Testing**
- Cada componente puede probarse de forma independiente
- Fácil identificación de problemas
- Tests más específicos

## Contexto Requerido

Los componentes necesitan las siguientes variables en el contexto:

```python
context = {
    'alumno': usuario,                    # Información del estudiante
    'curso': curso,                       # Curso actual
    'estudiantes_curso': estudiantes_curso, # Compañeros de curso
    'asignaturas_estudiante': asignaturas_estudiante, # Asignaturas inscritas
    'horario_estudiante': horario_estudiante, # Horario semanal
}
```

## Funcionalidades JavaScript

### Funciones Principales

- **`entrarAsignatura(nombre, codigo)`** - Abre modal de asignatura
- **`navegarSeccion(seccion)`** - Navegación entre secciones
- **`enviarMensaje()`** - Envío de mensajes en chat
- **`inscribirseElectivo(electivoId)`** - Inscripción a electivos

### Event Listeners

- Chat input con Enter
- Botones de inscripción a electivos
- Modales dinámicos

## Estilos CSS

### Clases Principales

- **`.asignatura-card`** - Tarjetas de asignaturas con hover
- **`.hover-card`** - Efectos de hover para tarjetas
- **`.clase-item`** - Elementos del horario
- **`.chat-container`** - Contenedor del chat
- **`.message-content`** - Estilos de mensajes

## Compatibilidad

- **Bootstrap 5** - Framework CSS principal
- **Font Awesome** - Iconos
- **FullCalendar** - Calendario interactivo
- **Chart.js** - Gráficos (opcional)

## Migración

Para migrar del panel original al modular:

1. Cambiar la URL en las vistas
2. Actualizar enlaces en templates
3. Verificar que todas las variables del contexto estén disponibles
4. Probar funcionalidades JavaScript

## Próximas Mejoras

- [ ] Componentes adicionales para funcionalidades específicas
- [ ] Sistema de notificaciones modular
- [ ] Componentes de gráficos independientes
- [ ] Templates para diferentes tipos de estudiantes
- [ ] Componentes de exportación de datos 