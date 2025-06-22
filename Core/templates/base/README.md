# Directorio Base - Templates Principales

Este directorio contiene los templates base y principales del sistema GEM.

## Archivos Incluidos

### `base.html`
- **Descripción**: Template base principal que define la estructura HTML común para todas las páginas
- **Funcionalidad**: 
  - Incluye Bootstrap, FontAwesome y otros recursos CSS/JS
  - Define el layout principal con navbar y footer
  - Proporciona bloques para contenido dinámico
- **Uso**: Todos los demás templates extienden de este archivo

### `home.html`
- **Descripción**: Página de inicio del sistema
- **Funcionalidad**:
  - Muestra información general del colegio
  - Enlaces a diferentes secciones
  - Dashboard básico para usuarios no autenticados
- **Acceso**: Público (no requiere autenticación)

### `login.html`
- **Descripción**: Página de inicio de sesión
- **Funcionalidad**:
  - Formulario de login con correo y contraseña
  - Validación de credenciales
  - Redirección según el rol del usuario
- **Acceso**: Público (no requiere autenticación)

## Estructura de Referencias

### Templates que extienden de base.html:
- `admin_panel.html` → `{% extends 'base/base.html' %}`
- `student_panel.html` → `{% extends 'base/base.html' %}`
- `teacher_panel.html` → `{% extends 'base/base.html' %}`
- `student_panel_modular.html` → `{% extends 'base/base.html' %}`
- `teacher_panel_modular.html` → `{% extends 'base/base.html' %}`
- Y otros templates del sistema...

### Vistas que referencian estos templates:
- `HomeView` → `template_name = 'base/home.html'`
- `LoginView` → `template_name = 'base/login.html'`

## Ventajas de esta Organización

1. **Separación Clara**: Los templates base están separados de los templates específicos de funcionalidad
2. **Mantenimiento**: Más fácil de mantener y actualizar los templates principales
3. **Organización**: Estructura más clara y lógica
4. **Escalabilidad**: Facilita agregar nuevos templates base en el futuro

## Notas Importantes

- Todos los templates que extienden de `base.html` deben actualizar su referencia a `{% extends 'base/base.html' %}`
- Las vistas que renderizan estos templates deben actualizar las rutas a `'base/home.html'` y `'base/login.html'`
- Esta estructura mantiene la funcionalidad original pero con mejor organización 