# Panel del Docente - Versión Modular

## Descripción
Este directorio contiene los componentes modulares del panel del docente, organizados de manera que faciliten el mantenimiento y la reutilización del código.

## Estructura de Archivos

### Componentes Principales
- **`header.html`** - Encabezado con información del docente (nombre, correo, especialidad)
- **`navigation_tabs.html`** - Pestañas de navegación del panel
- **`scripts.html`** - Scripts y estilos específicos del panel del docente

### Pestañas de Contenido
- **`tab_resumen.html`** - Resumen con estadísticas y actividad reciente
- **`tab_cursos.html`** - Gestión de cursos como profesor jefe
- **`tab_asignaturas.html`** - Asignaturas que imparte el docente
- **`tab_evaluaciones.html`** - Gestión de evaluaciones y calificaciones
- **`tab_retroalimentacion.html`** - Sistema de retroalimentación para estudiantes
- **`tab_asistencia.html`** - Registro y seguimiento de asistencia
- **`tab_calendario.html`** - Calendario académico y eventos
- **`tab_mensajes.html`** - Sistema de mensajería y comunicación
- **`tab_materiales.html`** - Gestión de materiales educativos

### Vistas de Detalle
- **`curso_detalle.html`** - Vista detallada de un curso específico (múltiples pestañas)
- **`asignatura_detalle.html`** - Vista detallada de una asignatura específica (múltiples pestañas)

### Archivo Principal
- **`teacher_panel_modular.html`** - Template principal que incluye todos los componentes

## Funcionalidades por Pestaña

### 📊 Resumen
- Estadísticas de cursos jefe y asignaturas
- Actividad reciente del docente
- Próximas tareas y eventos
- Notificaciones pendientes

### 👥 Cursos Jefe
- Lista de cursos donde es profesor jefe
- Estadísticas de rendimiento por curso
- Acceso a detalles de cada curso
- Generación de reportes

### 📚 Asignaturas
- Lista de asignaturas que imparte
- Acceso directo a detalles de cada asignatura
- Creación de nuevas evaluaciones
- Estadísticas de horas impartidas

### 📝 Evaluaciones
- Gestión completa de evaluaciones
- Estado de calificación (pendiente, en proceso, completada)
- Barras de progreso de calificación
- Integración con IA para generación de preguntas
- Estadísticas de evaluaciones

### 💬 Retroalimentación
- Generación de retroalimentación personalizada
- Integración con IA para retroalimentación automática
- Historial de retroalimentaciones enviadas
- Plantillas rápidas para diferentes tipos de feedback
- Filtros por curso, estudiante y asignatura

### ✅ Asistencia
- Registro de asistencia por clase
- Estadísticas de asistencia del mes
- Próximas clases programadas
- Generación de reportes de asistencia
- Vista de estado de registros

### 📅 Calendario
- Vista mensual del calendario académico
- Filtros por tipo de evento (evaluaciones, reuniones, actividades)
- Próximos eventos importantes
- Integración con eventos del colegio
- Navegación entre meses

### 💌 Mensajes
- Sistema de chat en tiempo real
- Lista de conversaciones activas
- Mensajes importantes y notificaciones
- Integración con coordinación y apoderados
- Historial de mensajes

### 📁 Materiales
- Gestión de materiales educativos
- Subida y organización de archivos
- Estadísticas de descargas
- Categorización por tipo de material
- Control de espacio de almacenamiento

## Vistas de Detalle

### 🎓 Curso Detalle (`curso_detalle.html`)
**Acceso**: Desde panel del docente → Cursos → "Ver Detalles"
**Funcionalidades**:
- Información general del curso (nivel, letra, profesor jefe)
- Lista de estudiantes con información de contacto
- Asignaturas del curso con enlaces a detalles
- Comunicaciones y herramientas IA (prototipo)
- Estadísticas de asistencia y rendimiento por estudiante
- Fichas de estudiantes con observaciones

### 📖 Asignatura Detalle (`asignatura_detalle.html`)
**Acceso**: Desde panel del docente → Asignaturas → "Ver Detalles"
**Funcionalidades**:
- Información general de la asignatura (código, profesor, estadísticas)
- Lista de estudiantes inscritos con información detallada
- Horario de clases con días, horarios y salas
- Materiales de la asignatura (archivos, presentaciones)
- Estadísticas de asistencia y promedio general

## URLs de Acceso a Vistas de Detalle

### Curso Detalle
- **URL**: `/curso/<int:curso_id>/`
- **Vista**: `CursoDetalleView`
- **Template**: `teacher/curso_detalle.html`

### Asignatura Detalle
- **URL**: `/asignatura/<int:asignatura_id>/`
- **Vista**: `AsignaturaDetalleView`
- **Template**: `teacher/asignatura_detalle.html`

## Ventajas de la Modularización

### 🔧 Mantenimiento
- **Código organizado**: Cada funcionalidad está en su propio archivo
- **Fácil actualización**: Modificar una pestaña no afecta a las demás
- **Debugging simplificado**: Problemas aislados por componente

### 🚀 Desarrollo
- **Reutilización**: Componentes pueden usarse en otras partes del sistema
- **Trabajo en paralelo**: Múltiples desarrolladores pueden trabajar en diferentes pestañas
- **Testing**: Pruebas unitarias por componente

### 🎨 Diseño
- **Consistencia**: Estilos centralizados en `scripts.html`
- **Flexibilidad**: Fácil personalización de componentes individuales
- **Responsive**: Cada componente mantiene su diseño responsive

## URLs Disponibles

### Panel Original
- **URL**: `/profesor-panel/`
- **Vista**: `ProfesorPanelView`
- **Template**: `teacher_panel.html`

### Panel Modular (Nuevo)
- **URL**: `/profesor-panel-modular/`
- **Vista**: `ProfesorPanelModularView`
- **Template**: `teacher_panel_modular.html`

## Cómo Usar

### Para Desarrolladores
1. **Modificar una pestaña**: Edita el archivo correspondiente en `Core/templates/teacher/`
2. **Agregar nueva funcionalidad**: Crea un nuevo archivo de pestaña y inclúyelo en `teacher_panel_modular.html`
3. **Personalizar estilos**: Modifica `scripts.html` para cambios de diseño
4. **Vistas de detalle**: Los templates de detalle están organizados en esta carpeta para mantener coherencia

### Para Usuarios
1. **Acceso**: Los docentes pueden acceder al panel modular desde `/profesor-panel-modular/`
2. **Navegación**: Usar las pestañas para acceder a diferentes funcionalidades
3. **Funcionalidades**: Todas las funcionalidades del panel original están disponibles
4. **Detalles**: Acceder a vistas detalladas desde los listados de cursos y asignaturas

## Tecnologías Utilizadas

### Frontend
- **Bootstrap 5**: Framework CSS para diseño responsive
- **Font Awesome**: Iconografía
- **JavaScript**: Funcionalidades interactivas
- **Chart.js**: Gráficos y estadísticas (preparado para implementación)

### Backend
- **Django**: Framework web
- **Django Templates**: Sistema de plantillas
- **Django ORM**: Consultas a la base de datos

## Próximas Mejoras

### Funcionalidades Planificadas
- [ ] Integración con sistema de notificaciones en tiempo real
- [ ] Implementación de gráficos interactivos con Chart.js
- [ ] Sistema de búsqueda avanzada en materiales
- [ ] Exportación de reportes en PDF
- [ ] Integración con calendario externo (Google Calendar)

### Optimizaciones
- [ ] Lazy loading de componentes pesados
- [ ] Caché de consultas frecuentes
- [ ] Compresión de assets estáticos
- [ ] Implementación de Service Workers para funcionalidad offline

## Contribución

Para contribuir al desarrollo del panel del docente:

1. **Crear rama**: `git checkout -b feature/nueva-funcionalidad`
2. **Desarrollar**: Trabajar en los archivos correspondientes
3. **Probar**: Verificar que todas las funcionalidades funcionen correctamente
4. **Documentar**: Actualizar este README si es necesario
5. **Merge**: Crear pull request para integrar los cambios

## Soporte

Para reportar problemas o solicitar nuevas funcionalidades:
- Crear un issue en el repositorio
- Incluir descripción detallada del problema o solicitud
- Adjuntar capturas de pantalla si es relevante
- Especificar el navegador y sistema operativo 