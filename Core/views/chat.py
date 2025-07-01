from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.conf import settings
import json
import requests
import os
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from Core.models import AsignaturaImpartida, AlumnoEvaluacion, Asistencia
from django.db.models import Avg, Count

class ChatPublicoView(View):
    template_name = 'base/chat_gem.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def _cargar_documentacion(self):
        """Carga la documentación del sistema desde los archivos markdown"""
        documentacion = ""
        carpeta_ia = os.path.join(settings.BASE_DIR, 'ia')
        
        if os.path.exists(carpeta_ia):
            for archivo in os.listdir(carpeta_ia):
                if archivo.endswith('.md'):
                    with open(os.path.join(carpeta_ia, archivo), 'r', encoding='utf-8') as f:
                        documentacion += f"\n\n=== {archivo} ===\n" + f.read()
        
        return documentacion
        
    def post(self, request):
        try:
            data = json.loads(request.body)
            mensaje_usuario = data.get('mensaje', '')
            
            if not mensaje_usuario:
                return JsonResponse({'error': 'Mensaje vacío'}, status=400)
            
            # Cargar la documentación del sistema
            documentacion_sistema = self._cargar_documentacion()
            
            # Configuración de la llamada a OpenAI
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {settings.OPENAI_API_KEY}'
            }
            
            # Mensaje del sistema con el contexto de la documentación
            system_message = f"""Eres un asistente amigable del colegio GEM (Gestión Educativa Moderna). 
Tu función es ayudar a estudiantes, profesores y personal administrativo con sus dudas sobre el sistema.
Respondes de manera educada, concisa y precisa, basándote en la siguiente documentación del sistema:

{documentacion_sistema}

Algunas pautas importantes:
1. Usa la documentación proporcionada para dar respuestas precisas sobre el funcionamiento del sistema
2. Si la pregunta es sobre una funcionalidad específica, menciona el módulo o sección correspondiente
3. Adapta tus respuestas según el rol del usuario (estudiante, profesor, administrador)
4. Si no encuentras la información específica en la documentación, indícalo claramente
5. Mantén un tono profesional pero amigable"""
            
            payload = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': system_message
                    },
                    {
                        'role': 'user',
                        'content': mensaje_usuario
                    }
                ],
                'max_tokens': 1000,
                'temperature': 0.7
            }
            
            # Llamada directa a la API de OpenAI
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f'Error en la API de OpenAI: {response.text}')
            
            data = response.json()
            respuesta_ia = data['choices'][0]['message']['content']
            
            return JsonResponse({
                'success': True,
                'mensaje_usuario': mensaje_usuario,
                'respuesta_ia': respuesta_ia
            })
            
        except Exception as e:
            print(f"Error en el chat: {str(e)}")  # Para debug
            return JsonResponse({
                'success': False,
                'error': 'Lo siento, ha ocurrido un error al procesar tu mensaje. Por favor, intenta de nuevo.'
            }, status=500) 

@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ChatIAView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            consulta = data.get('consulta')
            asignatura_id = data.get('asignatura_id')
            
            if not consulta or not asignatura_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Consulta y asignatura_id son requeridos'
                })
            
            # Obtener la asignatura
            asignatura = AsignaturaImpartida.objects.get(id=asignatura_id)
            
            # Verificar permisos
            if not request.user.usuario.auth_user == asignatura.docente.usuario.auth_user:
                return JsonResponse({
                    'success': False,
                    'error': 'No tienes permiso para esta asignatura'
                })
            
            # Obtener datos relevantes
            evaluaciones = AlumnoEvaluacion.objects.filter(
                evaluacion__clase__asignatura_impartida=asignatura
            )
            
            asistencias = Asistencia.objects.filter(
                clase__asignatura_impartida=asignatura
            )
            
            # Calcular estadísticas
            stats = {
                'promedio_general': evaluaciones.aggregate(Avg('nota'))['nota__avg'] or 0,
                'total_evaluaciones': evaluaciones.count(),
                'asistencia_promedio': (
                    asistencias.filter(presente=True).count() / asistencias.count() * 100
                    if asistencias.count() > 0 else 0
                )
            }
            
            # Procesar la consulta y generar respuesta
            respuesta = self.procesar_consulta(consulta, stats, asignatura)
            
            return JsonResponse({
                'success': True,
                'respuesta': respuesta
            })
            
        except AsignaturaImpartida.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Asignatura no encontrada'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    def procesar_consulta(self, consulta, stats, asignatura):
        """
        Procesa la consulta y genera una respuesta basada en las estadísticas
        y el contexto de la asignatura
        """
        consulta = consulta.lower()
        
        # Análisis de rendimiento
        if 'rendimiento' in consulta or 'análisis' in consulta:
            return self.generar_analisis_rendimiento(stats)
        
        # Retroalimentación
        elif 'retroalimentación' in consulta or 'feedback' in consulta:
            return self.generar_retroalimentacion(stats)
        
        # Estrategias de evaluación
        elif 'estrategias' in consulta or 'evaluación' in consulta:
            return self.generar_estrategias_evaluacion(stats)
        
        # Respuesta por defecto
        return self.generar_respuesta_general(stats, asignatura)
    
    def generar_analisis_rendimiento(self, stats):
        promedio = round(stats['promedio_general'], 1)
        asistencia = round(stats['asistencia_promedio'], 1)
        
        analisis = f"Basado en los datos actuales:\n\n"
        analisis += f"• El promedio general es {promedio}\n"
        analisis += f"• La asistencia promedio es {asistencia}%\n\n"
        
        if promedio >= 5.5:
            analisis += "El rendimiento general es muy bueno. "
        elif promedio >= 4.0:
            analisis += "El rendimiento es satisfactorio, pero hay espacio para mejora. "
        else:
            analisis += "El rendimiento está por debajo de lo esperado. "
        
        if asistencia >= 85:
            analisis += "La asistencia es excelente."
        elif asistencia >= 70:
            analisis += "La asistencia es aceptable."
        else:
            analisis += "La asistencia necesita mejorar."
        
        return analisis
    
    def generar_retroalimentacion(self, stats):
        promedio = stats['promedio_general']
        
        if promedio >= 5.5:
            return """
            Recomendaciones para mantener el alto rendimiento:
            • Continuar con el ritmo actual de trabajo
            • Implementar actividades de mayor complejidad
            • Fomentar el aprendizaje entre pares
            • Considerar proyectos especiales para estudiantes destacados
            """
        elif promedio >= 4.0:
            return """
            Sugerencias para mejorar el rendimiento:
            • Identificar áreas específicas de mejora
            • Implementar más ejercicios prácticos
            • Realizar evaluaciones formativas frecuentes
            • Fomentar la participación activa en clase
            """
        else:
            return """
            Acciones recomendadas para mejorar el rendimiento:
            • Realizar un diagnóstico detallado de dificultades
            • Implementar actividades de reforzamiento
            • Considerar tutorías o apoyo adicional
            • Mantener comunicación constante con los estudiantes
            """
    
    def generar_estrategias_evaluacion(self, stats):
        return """
        Estrategias de evaluación recomendadas:
        
        1. Evaluación Continua:
           • Pruebas cortas semanales
           • Trabajos prácticos
           • Participación en clase
        
        2. Evaluación Formativa:
           • Retroalimentación inmediata
           • Autoevaluación
           • Evaluación entre pares
        
        3. Evaluación Sumativa:
           • Proyectos integradores
           • Exámenes parciales
           • Presentaciones orales
        
        4. Herramientas de Evaluación:
           • Rúbricas detalladas
           • Portafolios digitales
           • Mapas conceptuales
        """
    
    def generar_respuesta_general(self, stats, asignatura):
        return f"""
        Información general de la asignatura {asignatura.asignatura.nombre}:
        
        • Total de evaluaciones: {stats['total_evaluaciones']}
        • Promedio general: {round(stats['promedio_general'], 1)}
        • Asistencia promedio: {round(stats['asistencia_promedio'], 1)}%
        
        ¿En qué aspecto específico necesitas ayuda? Puedo asistirte con:
        • Análisis de rendimiento
        • Sugerencias de retroalimentación
        • Estrategias de evaluación
        """ 