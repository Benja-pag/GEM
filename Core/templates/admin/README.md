# Panel de Administrador Modular

Este directorio contiene todos los componentes modulares del panel de administrador del sistema GEM.

## 📁 Estructura del Directorio

```
Core/templates/admin/
├── README.md                           # Este archivo
├── header.html                         # Encabezado del panel
├── stats_cards.html                    # Tarjetas de estadísticas
├── create_buttons.html                 # Botones de creación
├── navigation_tabs.html                # Pestañas de navegación
├── tab_usuarios.html                   # Pestaña de usuarios
├── tab_cursos.html                     # Pestaña de cursos
├── tab_asignaturas.html                # Pestaña de asignaturas
├── tab_reportes.html                   # Pestaña de reportes
├── tab_comunicaciones.html             # Pestaña de comunicaciones
├── tab_calendario.html                 # Pestaña de calendario
└── forms/                              # Formularios modulares
    ├── form_crear_estudiante.html      # Formulario crear estudiante
    ├── form_crear_docente.html         # Formulario crear docente
    ├── form_crear_admin.html           # Formulario crear administrador
    ├── form_crear_curso.html           # Formulario crear curso
    └── form_crear_asignatura.html      # Formulario crear asignatura
```

## 🎯 Componentes Principales

### **header.html**
- **Función**: Encabezado con información del usuario y botón de cerrar sesión
- **Incluye**: Nombre del administrador, rol y botón de logout
- **Uso**: `{% include 'admin/header.html' %}`

### **stats_cards.html**
- **Función**: Tarjetas de estadísticas del sistema
- **Incluye**: Total de estudiantes, profesores, asignaturas, administradores, clases y cursos
- **Uso**: `{% include 'admin/stats_cards.html' %}`

### **create_buttons.html**
- **Función**: Botones para crear nuevos registros
- **Incluye**: Botones para crear estudiante, docente, administrador, curso y asignatura
- **Uso**: `{% include 'admin/create_buttons.html' %}`

### **navigation_tabs.html**
- **Función**: Pestañas de navegación del panel
- **Incluye**: Pestañas para Usuarios, Cursos, Asignaturas, Reportes, Comunicaciones, Calendario y Configuración
- **Uso**: `{% include 'admin/navigation_tabs.html' %}`

## 📋 Pestañas de Contenido

### **tab_usuarios.html**
- **Función**: Gestión completa de usuarios
- **Características**:
  - Tabla de usuarios con filtros
  - Acciones: ver, editar, activar/desactivar, eliminar
  - Búsqueda avanzada
  - Filtros por tipo y estado

### **tab_cursos.html**
- **Función**: Gestión de cursos
- **Características**:
  - Lista de cursos con profesores jefe
  - Estadísticas por curso
  - Acciones de gestión
  - Métricas de distribución

### **tab_asignaturas.html**
- **Función**: Gestión de asignaturas
- **Características**:
  - Tabla detallada de asignaturas
  - Información de horarios y salas
  - Filtros por curso y profesor
  - Estado de asignaciones

### **tab_reportes.html**
- **Función**: Generación y gestión de reportes
- **Características**:
  - Reportes académicos y administrativos
  - Exportación en múltiples formatos
  - Reportes rápidos
  - Configuración de reportes

### **tab_comunicaciones.html**
- **Función**: Sistema de comunicaciones
- **Características**:
  - Creación de comunicaciones
  - Plantillas predefinidas
  - Historial de comunicaciones
  - Estadísticas de envío

### **tab_calendario.html**
- **Función**: Gestión del calendario escolar
- **Características**:
  - Vista de calendario interactivo
  - Gestión de eventos
  - Filtros por tipo de evento
  - Estadísticas del mes

## 📝 Formularios Modulares

### **forms/form_crear_estudiante.html**
- **Campos**: RUT, nombre, apellidos, correo, curso, contraseña
- **Validación**: Campos requeridos y formato de email

### **forms/form_crear_docente.html**
- **Campos**: RUT, nombre, apellidos, correo, especialidad, contraseña
- **Validación**: Campos requeridos y especialidad

### **forms/form_crear_admin.html**
- **Campos**: RUT, nombre, apellidos, correo, rol, contraseña
- **Validación**: Campos requeridos y rol válido

### **forms/form_crear_curso.html**
- **Campos**: Nivel, letra, capacidad máxima
- **Validación**: Nivel 1-3, letra A-B

### **forms/form_crear_asignatura.html**
- **Campos**: Código, nombre, curso, profesor, descripción
- **Validación**: Código y nombre únicos

## 🔗 URLs Disponibles

### **Panel Original**
- **URL**: `/admin-panel/`
- **Vista**: `AdminPanelView`
- **Template**: `admin_panel.html`

### **Panel Modular**
- **URL**: `/admin-panel-modular/`
- **Vista**: `AdminPanelModularView`
- **Template**: `admin_panel_modular.html`

## 🚀 Ventajas de la Modularización

1. **Mantenibilidad**: Cada componente es independiente y fácil de modificar
2. **Reutilización**: Los componentes pueden usarse en otros paneles
3. **Organización**: Código más limpio y estructurado
4. **Escalabilidad**: Fácil agregar nuevos componentes
5. **Colaboración**: Múltiples desarrolladores pueden trabajar en diferentes componentes

## 📊 Estadísticas Adicionales

El panel modular incluye estadísticas adicionales no presentes en el panel original:

- **Cursos con profesor jefe**: `{{ cursos_con_jefe }}`
- **Cursos sin profesor jefe**: `{{ cursos_sin_jefe }}`
- **Promedio de estudiantes por curso**: `{{ promedio_estudiantes }}`
- **Asignaturas sin profesor**: `{{ asignaturas_sin_profesor }}`

## 🔧 Funcionalidades del Panel Modular

### **Gestión de Usuarios**
- Crear, editar, activar/desactivar usuarios
- Filtros avanzados por tipo y estado
- Búsqueda por nombre, RUT o correo

### **Gestión de Cursos**
- Crear cursos con asignación de profesor jefe
- Ver estadísticas de estudiantes por curso
- Gestionar asignaturas por curso

### **Gestión de Asignaturas**
- Crear asignaturas con código único
- Asignar profesores a asignaturas
- Ver horarios y salas

### **Reportes**
- Generar reportes académicos y administrativos
- Exportar en PDF, Excel y CSV
- Configurar parámetros de reportes

### **Comunicaciones**
- Enviar comunicaciones a diferentes grupos
- Usar plantillas predefinidas
- Programar envíos

### **Calendario**
- Gestionar eventos escolares
- Filtrar por tipo de evento
- Ver estadísticas mensuales

## 🎨 Personalización

Cada componente puede ser personalizado independientemente:

1. **Estilos**: Modificar CSS en `admin/forms/` o en el archivo principal
2. **Funcionalidad**: Agregar JavaScript específico por componente
3. **Contenido**: Modificar el HTML de cada componente sin afectar otros
4. **Validación**: Agregar validaciones específicas por formulario

## 📝 Notas de Desarrollo

- Todos los componentes usan Bootstrap 5 para el diseño
- Los formularios incluyen validación HTML5 y JavaScript
- Los modales usan Bootstrap Modal para la interactividad
- Las tablas incluyen DataTables para funcionalidad avanzada
- Los componentes son responsivos y funcionan en móviles

## 🔄 Migración

Para migrar del panel original al modular:

1. **Actualizar URLs**: Cambiar referencias de `admin_panel` a `admin_panel_modular`
2. **Actualizar vistas**: Usar `AdminPanelModularView` en lugar de `AdminPanelView`
3. **Verificar funcionalidad**: Asegurar que todos los formularios funcionen correctamente
4. **Probar estadísticas**: Verificar que las estadísticas adicionales se muestren correctamente 