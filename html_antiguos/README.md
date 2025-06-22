# Archivos HTML Antiguos

## Descripción
Esta carpeta contiene los archivos HTML de los paneles antiguos (no modulares) que fueron movidos para dar paso a los paneles modulares.

## Archivos Movidos

### Paneles Principales
- **`admin_panel.html`** - Panel de administrador original (99KB, 1466 líneas)
- **`student_panel.html`** - Panel de estudiante original (72KB, 1229 líneas)
- **`teacher_panel.html`** - Panel de docente original (19KB, 360 líneas)

## Razón del Movimiento

Los paneles modulares ofrecen las siguientes ventajas:

### 🔧 Mantenimiento
- **Código organizado**: Cada funcionalidad está en su propio archivo
- **Fácil actualización**: Modificar una pestaña no afecta a las demás
- **Debugging simplificado**: Problemas aislados por componente

### 🚀 Desarrollo
- **Reutilización**: Componentes pueden usarse en otras partes del sistema
- **Trabajo en paralelo**: Múltiples desarrolladores pueden trabajar en diferentes pestañas
- **Testing**: Pruebas unitarias por componente

### 🎨 Diseño
- **Consistencia**: Estilos centralizados
- **Flexibilidad**: Fácil personalización de componentes individuales
- **Responsive**: Cada componente mantiene su diseño responsive

## URLs Alternativas

Los paneles antiguos siguen disponibles en las siguientes URLs:

- **Panel de Administrador Antiguo**: `/admin-panel-antiguo/`
- **Panel de Docente Antiguo**: `/profesor-panel-antiguo/`
- **Panel de Estudiante Antiguo**: `/estudiante-panel-antiguo/`

## Paneles Modulares Actuales

### Panel de Administrador Modular
- **URL**: `/admin-panel/`
- **Template**: `Core/templates/admin_panel_modular.html`
- **Componentes**: `Core/templates/admin/`

### Panel de Docente Modular
- **URL**: `/profesor-panel/`
- **Template**: `Core/templates/teacher_panel_modular.html`
- **Componentes**: `Core/templates/teacher/`

### Panel de Estudiante Modular
- **URL**: `/estudiante-panel/`
- **Template**: `Core/templates/student_panel_modular.html`
- **Componentes**: `Core/templates/student/`

## Migración Completa

### ✅ Completado
- [x] Mover archivos HTML antiguos a esta carpeta
- [x] Actualizar URLs para usar paneles modulares por defecto
- [x] Mantener URLs alternativas para paneles antiguos
- [x] Verificar que todas las vistas modulares funcionen correctamente

### 📋 Funcionalidades Mantenidas
- Todas las funcionalidades de los paneles originales están disponibles en los modulares
- Mejor organización del código
- Componentes reutilizables
- Mantenimiento simplificado

## Notas Importantes

1. **No eliminar**: Estos archivos se mantienen como respaldo y referencia
2. **Compatibilidad**: Las URLs alternativas permiten acceso a versiones antiguas si es necesario
3. **Desarrollo**: Para nuevas funcionalidades, usar siempre los paneles modulares
4. **Migración**: Los usuarios ahora acceden automáticamente a los paneles modulares

## Estructura de Componentes Modulares

### Admin
```
Core/templates/admin/
├── header.html
├── navigation_tabs.html
├── stats_cards.html
├── create_buttons.html
├── forms/
│   ├── form_crear_admin.html
│   ├── form_crear_asignatura.html
│   ├── form_crear_curso.html
│   ├── form_crear_docente.html
│   └── form_crear_estudiante.html
└── tab_*.html (pestañas de contenido)
```

### Teacher
```
Core/templates/teacher/
├── header.html
├── navigation_tabs.html
├── scripts.html
├── curso_detalle.html
├── asignatura_detalle.html
└── tab_*.html (pestañas de contenido)
```

### Student
```
Core/templates/student/
├── header.html
├── navigation_tabs.html
├── scripts.html
├── summary_cards.html
└── tab_*.html (pestañas de contenido)
```

## Fecha de Migración
**22 de Junio, 2025** - Migración completa de paneles antiguos a modulares 