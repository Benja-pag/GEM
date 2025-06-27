from typing import Dict, List

"""
Configuración para el servicio de IA.
"""

# Configuración de OpenAI
OPENAI_MODEL = "gpt-3.5-turbo"  # Modelo a utilizar
MAX_TOKENS = 500  # Máximo de tokens por respuesta
TEMPERATURE = 0.7  # Creatividad en las respuestas (0.0 - 1.0)

# Contexto del Sistema GEM
SYSTEM_CONTEXT = """
Eres un asistente especializado en el sistema de gestión educativa GEM (Gestión Educativa Moderna).
Este sistema está diseñado para colegios chilenos y maneja:

1. ESTRUCTURA ACADÉMICA:
- Niveles educativos desde 1° medio a 4° medio
- Asignaturas obligatorias y electivas
- Sistema de evaluación con escala 1.0 a 7.0
- Registro de asistencia diaria por asignatura

2. USUARIOS Y ROLES:
- Administradores: Gestión completa del sistema
- Docentes: Registro de notas, asistencia, comunicaciones
- Profesores Jefe: Gestión de curso y reportes especiales
- Estudiantes: Acceso a notas, asistencia, comunicaciones
- Apoderados: Seguimiento del estudiante

3. RESTRICCIONES IMPORTANTES:
- No puedes modificar directamente la base de datos
- No puedes crear, modificar o eliminar usuarios
- No puedes alterar notas o asistencias
- Debes respetar la privacidad de los datos

4. FUNCIONES PERMITIDAS:
- Generar reportes y análisis
- Proporcionar sugerencias basadas en datos existentes
- Ayudar en la redacción de comunicaciones
- Responder consultas sobre el sistema
"""

# Idioma y Localización
LANGUAGE = "es"  # Español
EDUCATION_SYSTEM = "chileno"
ACADEMIC_YEAR = "2025"  # Año académico actual

# Límites de uso
MAX_REQUESTS_PER_DAY = 100  # Máximo de solicitudes por día
MAX_REQUESTS_PER_MINUTE = 5  # Rate limiting
CACHE_DURATION = 3600  # Duración del caché en segundos (1 hora)

# Tipos de análisis disponibles
ANALYSIS_TYPES = {
    'rendimiento': {
        'name': 'Análisis de Rendimiento',
        'description': 'Análisis del rendimiento académico del curso',
        'metrics': ['notas', 'promedios', 'tendencias'],
        'scope': 'curso'
    },
    'asistencia': {
        'name': 'Análisis de Asistencia',
        'description': 'Análisis de la asistencia y puntualidad',
        'metrics': ['porcentaje_asistencia', 'atrasos', 'justificaciones'],
        'scope': 'curso'
    },
    'comportamiento': {
        'name': 'Análisis de Comportamiento',
        'description': 'Análisis del comportamiento y convivencia escolar',
        'metrics': ['anotaciones', 'observaciones', 'incidentes'],
        'scope': 'curso'
    }
}

# Templates para diferentes tipos de interacciones
TEMPLATES = {
    # Templates para reportes
    'reporte_rendimiento': """
        Genera un reporte detallado del rendimiento académico para el curso {curso_id}.
        
        Contexto:
        - Profesor: {profesor}
        - Periodo: {periodo}
        
        El reporte debe incluir:
        1. Análisis general del rendimiento
        2. Tendencias y patrones
        3. Áreas de mejora
        4. Recomendaciones específicas
        
        Formato JSON requerido:
        {
            "titulo": "Reporte de Rendimiento Académico",
            "contenido": [
                "Análisis general...",
                "Tendencias identificadas...",
                "Áreas críticas..."
            ],
            "recomendaciones": [
                "Recomendación 1",
                "Recomendación 2"
            ]
        }
    """,
    
    'reporte_asistencia': """
        Genera un reporte de asistencia para el curso {curso_id}.
        
        Contexto:
        - Profesor: {profesor}
        - Periodo: {periodo}
        
        El reporte debe incluir:
        1. Estadísticas de asistencia
        2. Patrones de inasistencia
        3. Casos críticos
        4. Recomendaciones
        
        Formato JSON requerido:
        {
            "titulo": "Reporte de Asistencia",
            "contenido": [
                "Análisis de asistencia...",
                "Patrones identificados...",
                "Casos que requieren atención..."
            ],
            "recomendaciones": [
                "Recomendación 1",
                "Recomendación 2"
            ]
        }
    """,
    
    'reporte_comportamiento': """
        Genera un reporte de comportamiento para el curso {curso_id}.
        
        Contexto:
        - Profesor: {profesor}
        - Periodo: {periodo}
        
        El reporte debe incluir:
        1. Análisis del clima del aula
        2. Incidentes relevantes
        3. Aspectos positivos
        4. Recomendaciones
        
        Formato JSON requerido:
        {
            "titulo": "Reporte de Comportamiento",
            "contenido": [
                "Análisis del clima...",
                "Incidentes destacados...",
                "Aspectos positivos..."
            ],
            "recomendaciones": [
                "Recomendación 1",
                "Recomendación 2"
            ]
        }
    """,
    
    # Templates para sugerencias
    'sugerencias_academica': """
        Genera sugerencias de mejora académica para el curso {curso_id}.
        
        Contexto:
        - Profesor: {profesor}
        - Periodo: {periodo}
        
        Las sugerencias deben ser:
        1. Específicas y accionables
        2. Basadas en evidencia
        3. Priorizadas por impacto
        
        Formato JSON requerido:
        {
            "area": "Mejora Académica",
            "sugerencias": [
                {
                    "titulo": "Título de la sugerencia",
                    "descripcion": "Descripción detallada",
                    "prioridad": "Alta/Media/Baja"
                }
            ],
            "recursos": [
                "Recurso 1",
                "Recurso 2"
            ]
        }
    """,
    
    'sugerencias_asistencia': """
        Genera sugerencias para mejorar la asistencia en el curso {curso_id}.
        
        Contexto:
        - Profesor: {profesor}
        - Periodo: {periodo}
        
        Las sugerencias deben:
        1. Abordar causas comunes de inasistencia
        2. Proponer estrategias de motivación
        3. Incluir acciones preventivas
        
        Formato JSON requerido:
        {
            "area": "Mejora de Asistencia",
            "sugerencias": [
                {
                    "titulo": "Título de la sugerencia",
                    "descripcion": "Descripción detallada",
                    "prioridad": "Alta/Media/Baja"
                }
            ],
            "recursos": [
                "Recurso 1",
                "Recurso 2"
            ]
        }
    """,
    
    'sugerencias_convivencia': """
        Genera sugerencias para mejorar la convivencia en el curso {curso_id}.
        
        Contexto:
        - Profesor: {profesor}
        - Periodo: {periodo}
        
        Las sugerencias deben:
        1. Promover un ambiente positivo
        2. Abordar conflictos comunes
        3. Fomentar la colaboración
        
        Formato JSON requerido:
        {
            "area": "Mejora de Convivencia",
            "sugerencias": [
                {
                    "titulo": "Título de la sugerencia",
                    "descripcion": "Descripción detallada",
                    "prioridad": "Alta/Media/Baja"
                }
            ],
            "recursos": [
                "Recurso 1",
                "Recurso 2"
            ]
        }
    """,
    
    # Templates para comunicados
    'comunicado_rendimiento': """
        Genera un comunicado sobre rendimiento académico para el curso {curso_id}.
        
        Contexto:
        - Profesor: {profesor}
        - Periodo: {periodo}
        
        El comunicado debe:
        1. Ser profesional y empático
        2. Incluir datos relevantes
        3. Proponer acciones concretas
        
        Formato JSON requerido:
        {
            "asunto": "Asunto del comunicado",
            "contenido": "Contenido detallado...",
            "tipo": "rendimiento"
        }
    """,
    
    'comunicado_asistencia': """
        Genera un comunicado sobre asistencia para el curso {curso_id}.
        
        Contexto:
        - Profesor: {profesor}
        - Periodo: {periodo}
        
        El comunicado debe:
        1. Ser claro y directo
        2. Destacar la importancia de la asistencia
        3. Incluir datos específicos
        
        Formato JSON requerido:
        {
            "asunto": "Asunto del comunicado",
            "contenido": "Contenido detallado...",
            "tipo": "asistencia"
        }
    """,
    
    'comunicado_general': """
        Genera un comunicado general para el curso {curso_id}.
        
        Contexto:
        - Profesor: {profesor}
        - Periodo: {periodo}
        
        El comunicado debe:
        1. Ser informativo y claro
        2. Mantener un tono positivo
        3. Incluir próximos pasos
        
        Formato JSON requerido:
        {
            "asunto": "Asunto del comunicado",
            "contenido": "Contenido detallado...",
            "tipo": "general"
        }
    """,
    
    # Template para chat
    'chat': """
        Responde al siguiente mensaje del usuario para el curso {curso_id}:
        
        Mensaje: {mensaje}
        
        Contexto:
        - Profesor: {profesor}
        - Periodo: {periodo}
        
        La respuesta debe ser:
        1. Clara y concisa
        2. Relevante al contexto
        3. Orientada a la acción cuando sea apropiado
    """
}

# Validaciones y restricciones
CONTENT_RESTRICTIONS = {
    "palabras_prohibidas": [
        "fracaso",
        "malo",
        "pésimo",
        "terrible",
        "deficiente",
        "reprobado",
        "incompetente",
        "mediocre"
    ],
    "temas_sensibles": [
        "diagnósticos médicos",
        "situación familiar",
        "condición socioeconómica",
        "creencias religiosas",
        "orientación sexual",
        "ideología política",
        "conflictos familiares"
    ],
    "datos_personales": [
        "rut",
        "dirección",
        "teléfono",
        "email",
        "contraseña",
        "datos bancarios",
        "información médica"
    ]
}

# Configuración de límites y seguridad
RATE_LIMITS = {
    'requests_per_minute': 10,
    'requests_per_hour': 100,
    'tokens_per_day': 100000
}

SECURITY_CONFIG = {
    'allowed_roles': ['admin', 'profesor', 'profesor_jefe'],
    'sensitive_fields': ['rut', 'telefono', 'direccion', 'email'],
    'max_context_length': 2000
}

# Configuración de respuestas
RESPONSE_STRUCTURE = {
    'reporte': {
        'titulo': str,
        'fecha': str,
        'contenido': list,
        'recomendaciones': list
    },
    'sugerencias': {
        'area': str,
        'sugerencias': list,
        'recursos': list
    },
    'comunicado': {
        'asunto': str,
        'contenido': str,
        'fecha': str
    }
}

# Mensajes de error personalizados
ERROR_MESSAGES = {
    "token_limit": "La solicitud excede el límite de tokens permitido.",
    "rate_limit": "Se ha excedido el límite de solicitudes. Por favor, intente más tarde.",
    "content_restricted": "El contenido generado contiene elementos no permitidos.",
    "api_error": "Error en la comunicación con la API de OpenAI.",
    "validation_error": "Los datos proporcionados no cumplen con los criterios requeridos.",
    "data_protection": "La solicitud incluye información personal protegida.",
    "system_context": "Error al acceder a los módulos del sistema.",
    "module_access": "No tiene permisos para acceder a este módulo.",
    "data_format": "Los datos no cumplen con el formato requerido por el sistema.",
    "business_rules": "La operación viola las reglas de negocio del sistema.",
    'template_not_found': 'Template no encontrado',
    'invalid_format': 'Formato de respuesta inválido',
    'permission_denied': 'No tiene permisos para usar esta función'
}

# Jerarquía y Acceso a Datos
ACCESS_HIERARCHY = {
    "ADMIN": {
        "nivel": 3,
        "acceso_total": True,
        "puede_ver": ["admin", "docente", "estudiante"],
        "datos_permitidos": ["*"]  # Acceso total
    },
    "DOCENTE": {
        "nivel": 2,
        "acceso_total": False,
        "puede_ver": ["docente", "estudiante"],
        "datos_permitidos": [
            "notas_curso",
            "asistencia_curso",
            "anotaciones_curso",
            "comunicaciones_curso",
            "datos_estudiante_basico",
            "reportes_curso",
            "evaluaciones_curso"
        ]
    },
    "PROFESOR_JEFE": {
        "nivel": 2,
        "acceso_total": False,
        "puede_ver": ["docente", "estudiante"],
        "datos_permitidos": [
            "notas_curso",
            "asistencia_curso",
            "anotaciones_curso",
            "comunicaciones_curso",
            "datos_estudiante_completo",
            "reportes_curso",
            "evaluaciones_curso"
        ]
    },
    "ESTUDIANTE": {
        "nivel": 1,
        "acceso_total": False,
        "puede_ver": ["estudiante"],
        "datos_permitidos": [
            "notas_propias",
            "asistencia_propia",
            "anotaciones_propias",
            "comunicaciones_propias",
            "horario_propio"
        ]
    }
}

# Campos sensibles por rol
SENSITIVE_FIELDS = {
    "ADMIN": [],  # Acceso total
    "DOCENTE": [
        "rut",
        "direccion",
        "telefono",
        "email_personal",
        "datos_medicos",
        "situacion_familiar",
        "datos_economicos",
        "contraseñas",
        "datos_admin"
    ],
    "PROFESOR_JEFE": [
        "rut",
        "datos_medicos",
        "datos_economicos",
        "contraseñas",
        "datos_admin"
    ],
    "ESTUDIANTE": [
        "rut_otros",
        "datos_otros_estudiantes",
        "datos_docentes",
        "datos_admin",
        "contraseñas"
    ]
}

# Reglas de visualización de datos
DATA_VISIBILITY_RULES = {
    "notas": {
        "individual": ["ADMIN", "PROFESOR_JEFE", "DOCENTE_ASIGNATURA", "ESTUDIANTE_PROPIO"],
        "curso_completo": ["ADMIN", "PROFESOR_JEFE", "DOCENTE_ASIGNATURA"],
        "todos_cursos": ["ADMIN"]
    },
    "asistencia": {
        "individual": ["ADMIN", "PROFESOR_JEFE", "DOCENTE_ASIGNATURA", "ESTUDIANTE_PROPIO"],
        "curso_completo": ["ADMIN", "PROFESOR_JEFE", "DOCENTE_ASIGNATURA"],
        "todos_cursos": ["ADMIN"]
    },
    "anotaciones": {
        "individual": ["ADMIN", "PROFESOR_JEFE", "DOCENTE_ASIGNATURA", "ESTUDIANTE_PROPIO"],
        "curso_completo": ["ADMIN", "PROFESOR_JEFE"],
        "todos_cursos": ["ADMIN"]
    },
    "datos_personales": {
        "basicos": ["ADMIN", "PROFESOR_JEFE", "DOCENTE_ASIGNATURA"],
        "completos": ["ADMIN", "PROFESOR_JEFE"],
        "sensibles": ["ADMIN"]
    },
    "reportes": {
        "individual": ["ADMIN", "PROFESOR_JEFE", "DOCENTE_ASIGNATURA", "ESTUDIANTE_PROPIO"],
        "curso": ["ADMIN", "PROFESOR_JEFE"],
        "institucion": ["ADMIN"]
    }
}

# Configuración de la API de OpenAI
OPENAI_CONFIG = {
    'model': 'gpt-4',
    'temperature': 0.7,
    'max_tokens': 1000
}

# Configuración de caché
CACHE_CONFIG = {
    'timeout': 3600,  # 1 hora
    'version': 1
} 