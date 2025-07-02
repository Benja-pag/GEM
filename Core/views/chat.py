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
            
            # Calcular estadísticas detalladas
            stats = self.calcular_estadisticas_detalladas(evaluaciones, asistencias)
            
            # Generar respuesta usando OpenAI
            respuesta = self.generar_respuesta_openai(consulta, stats, asignatura)
            
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
    
    def calcular_estadisticas_detalladas(self, evaluaciones, asistencias):
        """Calcula estadísticas detalladas para el contexto"""
        total_evaluaciones = evaluaciones.count()
        total_asistencias = asistencias.count()
        
        # Estadísticas de evaluaciones
        promedio_general = evaluaciones.aggregate(Avg('nota'))['nota__avg'] or 0
        notas_por_rango = {
            'excelente': evaluaciones.filter(nota__gte=6.0).count(),
            'bueno': evaluaciones.filter(nota__gte=5.0, nota__lt=6.0).count(),
            'aceptable': evaluaciones.filter(nota__gte=4.0, nota__lt=5.0).count(),
            'bajo': evaluaciones.filter(nota__lt=4.0).count()
        }
        
        # Estadísticas de asistencia
        asistencias_presentes = asistencias.filter(presente=True).count()
        asistencias_ausentes = asistencias.filter(presente=False).count()
        asistencias_justificadas = asistencias.filter(justificado=True).count()
        
        asistencia_promedio = (asistencias_presentes / total_asistencias * 100) if total_asistencias > 0 else 0
        
        return {
            'promedio_general': round(promedio_general, 1),
            'total_evaluaciones': total_evaluaciones,
            'total_asistencias': total_asistencias,
            'asistencia_promedio': round(asistencia_promedio, 1),
            'notas_por_rango': notas_por_rango,
            'asistencias_presentes': asistencias_presentes,
            'asistencias_ausentes': asistencias_ausentes,
            'asistencias_justificadas': asistencias_justificadas,
            'porcentaje_justificadas': round((asistencias_justificadas / total_asistencias * 100) if total_asistencias > 0 else 0, 1)
        }
    
    def generar_respuesta_openai(self, consulta, stats, asignatura):
        """Genera respuesta usando la API de OpenAI con contexto específico"""
        try:
            # Verificar que la clave de OpenAI esté configurada
            if not settings.OPENAI_API_KEY:
                print("Error: OPENAI_API_KEY no está configurada")
                return self.generar_respuesta_fallback(consulta, stats, asignatura)
            
            # Configuración de la llamada a OpenAI
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {settings.OPENAI_API_KEY}'
            }
            
            # Crear contexto específico de la asignatura
            contexto_asignatura = f"""
            CONTEXTO DE LA ASIGNATURA:
            - Nombre: {asignatura.asignatura.nombre}
            - Código: {asignatura.codigo}
            - Docente: {asignatura.docente.usuario.nombre} {asignatura.docente.usuario.apellido_paterno}
            
            ESTADÍSTICAS ACTUALES:
            - Promedio general: {stats['promedio_general']}
            - Total evaluaciones: {stats['total_evaluaciones']}
            - Asistencia promedio: {stats['asistencia_promedio']}%
            - Asistencias presentes: {stats['asistencias_presentes']}
            - Asistencias ausentes: {stats['asistencias_ausentes']}
            - Asistencias justificadas: {stats['asistencias_justificadas']} ({stats['porcentaje_justificadas']}%)
            
            DISTRIBUCIÓN DE NOTAS:
            - Excelente (6.0+): {stats['notas_por_rango']['excelente']} estudiantes
            - Bueno (5.0-5.9): {stats['notas_por_rango']['bueno']} estudiantes
            - Aceptable (4.0-4.9): {stats['notas_por_rango']['aceptable']} estudiantes
            - Bajo (<4.0): {stats['notas_por_rango']['bajo']} estudiantes
            """
            
            # Mensaje del sistema
            system_message = f"""Eres un asistente IA especializado en educación que ayuda a docentes con análisis pedagógicos.

Tu función es proporcionar análisis inteligentes, recomendaciones específicas y estrategias educativas basadas en los datos reales de la asignatura.

CONTEXTO ESPECÍFICO DE LA ASIGNATURA:
{contexto_asignatura}

INSTRUCCIONES:
1. Analiza los datos proporcionados para dar respuestas contextualizadas
2. Proporciona recomendaciones específicas y accionables
3. Usa un tono profesional pero amigable
4. Incluye emojis apropiados para hacer la respuesta más atractiva
5. Estructura las respuestas de manera clara con viñetas y secciones
6. Si la consulta es sobre evaluación, enfócate en estrategias pedagógicas
7. Si es sobre asistencia, sugiere métodos para mejorar la participación
8. Si es sobre rendimiento, proporciona análisis detallado y acciones específicas

FORMATO DE RESPUESTA:
- Usa HTML básico para formato (<strong>, <br>, etc.)
- Incluye análisis de datos
- Proporciona recomendaciones específicas
- Mantén un tono motivacional y constructivo"""

            payload = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': system_message
                    },
                    {
                        'role': 'user',
                        'content': f"Consulta del docente: {consulta}"
                    }
                ],
                'max_tokens': 1500,
                'temperature': 0.7
            }
            
            print(f"Enviando consulta a OpenAI: {consulta[:50]}...")
            
            # Llamada a la API de OpenAI
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = f'Error en la API de OpenAI: {response.status_code} - {response.text}'
                print(error_msg)
                raise Exception(error_msg)
            
            data = response.json()
            respuesta_ia = data['choices'][0]['message']['content']
            
            print(f"Respuesta de OpenAI recibida: {len(respuesta_ia)} caracteres")
            return respuesta_ia
            
        except requests.exceptions.Timeout:
            print("Timeout en la llamada a OpenAI")
            return self.generar_respuesta_fallback(consulta, stats, asignatura)
        except requests.exceptions.RequestException as e:
            print(f"Error de red en OpenAI: {str(e)}")
            return self.generar_respuesta_fallback(consulta, stats, asignatura)
        except Exception as e:
            print(f"Error en OpenAI: {str(e)}")
            return self.generar_respuesta_fallback(consulta, stats, asignatura)
    
    def generar_respuesta_fallback(self, consulta, stats, asignatura):
        """Genera una respuesta de respaldo si OpenAI falla"""
        consulta = consulta.lower()
        
        if any(palabra in consulta for palabra in ['rendimiento', 'análisis', 'promedio', 'notas']):
            return self.generar_analisis_rendimiento(stats, asignatura)
        elif any(palabra in consulta for palabra in ['retroalimentación', 'feedback', 'sugerencias', 'recomendaciones']):
            return self.generar_retroalimentacion(stats, asignatura)
        elif any(palabra in consulta for palabra in ['estrategias', 'evaluación', 'métodos', 'técnicas']):
            return self.generar_estrategias_evaluacion(stats, asignatura)
        elif any(palabra in consulta for palabra in ['asistencia', 'presencia', 'falta']):
            return self.generar_analisis_asistencia(stats, asignatura)
        elif any(palabra in consulta for palabra in ['ayuda', 'ayudar', 'qué', 'cómo', 'cuál']):
            return self.generar_ayuda_general(asignatura)
        else:
            return self.generar_respuesta_general(stats, asignatura)
    
    def generar_analisis_rendimiento(self, stats, asignatura):
        promedio = round(stats['promedio_general'], 1)
        asistencia = round(stats['asistencia_promedio'], 1)
        total_eval = stats['total_evaluaciones']
        
        analisis = f"📊 <strong>Análisis de Rendimiento - {asignatura.asignatura.nombre}</strong>\n\n"
        analisis += f"• <strong>Promedio General:</strong> {promedio}\n"
        analisis += f"• <strong>Asistencia Promedio:</strong> {asistencia}%\n"
        analisis += f"• <strong>Total Evaluaciones:</strong> {total_eval}\n\n"
        
        # Análisis del promedio
        if promedio >= 6.0:
            analisis += "🎉 <strong>Excelente rendimiento!</strong> Los estudiantes están demostrando un dominio sólido de los contenidos.\n\n"
        elif promedio >= 5.0:
            analisis += "✅ <strong>Buen rendimiento.</strong> Los estudiantes están alcanzando los objetivos de aprendizaje.\n\n"
        elif promedio >= 4.0:
            analisis += "⚠️ <strong>Rendimiento aceptable.</strong> Hay espacio para mejorar, pero se están cumpliendo los mínimos.\n\n"
        else:
            analisis += "🔴 <strong>Rendimiento bajo.</strong> Se requieren acciones inmediatas para mejorar los resultados.\n\n"
        
        # Análisis de la asistencia
        if asistencia >= 90:
            analisis += "📈 <strong>Asistencia excepcional.</strong> Los estudiantes están muy comprometidos con la asignatura.\n\n"
        elif asistencia >= 80:
            analisis += "📈 <strong>Buena asistencia.</strong> Los estudiantes mantienen un buen nivel de compromiso.\n\n"
        elif asistencia >= 70:
            analisis += "⚠️ <strong>Asistencia regular.</strong> Considera implementar estrategias para mejorar la participación.\n\n"
        else:
            analisis += "🔴 <strong>Asistencia baja.</strong> Se requieren acciones para motivar la participación.\n\n"
        
        # Recomendaciones específicas
        analisis += "<strong>Recomendaciones:</strong>\n"
        if promedio < 5.0:
            analisis += "• Implementar sesiones de reforzamiento\n"
            analisis += "• Realizar evaluaciones diagnósticas más frecuentes\n"
            analisis += "• Considerar tutorías individuales\n"
        if asistencia < 80:
            analisis += "• Implementar actividades más interactivas\n"
            analisis += "• Establecer sistema de incentivos por participación\n"
            analisis += "• Comunicar la importancia de la asistencia\n"
        
        return analisis
    
    def generar_retroalimentacion(self, stats, asignatura):
        promedio = stats['promedio_general']
        asistencia = stats['asistencia_promedio']
        
        retroalimentacion = f"💡 <strong>Sugerencias de Retroalimentación - {asignatura.asignatura.nombre}</strong>\n\n"
        
        if promedio >= 6.0:
            retroalimentacion += "🎯 <strong>Para mantener el alto rendimiento:</strong>\n"
            retroalimentacion += "• Proporcionar desafíos adicionales para estudiantes destacados\n"
            retroalimentacion += "• Implementar proyectos de investigación o extensión\n"
            retroalimentacion += "• Fomentar el aprendizaje entre pares (tutorías estudiantiles)\n"
            retroalimentacion += "• Considerar evaluaciones de mayor complejidad\n\n"
        elif promedio >= 5.0:
            retroalimentacion += "📈 <strong>Para mejorar el rendimiento:</strong>\n"
            retroalimentacion += "• Identificar áreas específicas de mejora por estudiante\n"
            retroalimentacion += "• Implementar más ejercicios prácticos y casos de estudio\n"
            retroalimentacion += "• Realizar evaluaciones formativas semanales\n"
            retroalimentacion += "• Fomentar la participación activa en clase\n\n"
        else:
            retroalimentacion += "🔄 <strong>Para mejorar significativamente:</strong>\n"
            retroalimentacion += "• Realizar un diagnóstico detallado de dificultades\n"
            retroalimentacion += "• Implementar actividades de reforzamiento básico\n"
            retroalimentacion += "• Considerar tutorías individuales o grupales\n"
            retroalimentacion += "• Mantener comunicación constante con los estudiantes\n\n"
        
        # Sugerencias específicas por asistencia
        if asistencia < 80:
            retroalimentacion += "📋 <strong>Sugerencias para mejorar la asistencia:</strong>\n"
            retroalimentacion += "• Implementar actividades más dinámicas e interactivas\n"
            retroalimentacion += "• Establecer un sistema de incentivos por participación\n"
            retroalimentacion += "• Comunicar claramente la importancia de la asistencia\n"
            retroalimentacion += "• Considerar clases híbridas o grabadas para casos especiales\n\n"
        
        retroalimentacion += "💬 <strong>Tipos de retroalimentación recomendados:</strong>\n"
        retroalimentacion += "• Retroalimentación inmediata en evaluaciones\n"
        retroalimentacion += "• Comentarios constructivos y específicos\n"
        retroalimentacion += "• Sugerencias de mejora concretas\n"
        retroalimentacion += "• Reconocimiento de logros y esfuerzos\n"
        
        return retroalimentacion
    
    def generar_estrategias_evaluacion(self, stats, asignatura):
        promedio = stats['promedio_general']
        
        estrategias = f"📚 <strong>Estrategias de Evaluación - {asignatura.asignatura.nombre}</strong>\n\n"
        
        estrategias += "🎯 <strong>1. Evaluación Continua:</strong>\n"
        estrategias += "• Pruebas cortas semanales (10-15 minutos)\n"
        estrategias += "• Trabajos prácticos individuales y grupales\n"
        estrategias += "• Participación activa en clase\n"
        estrategias += "• Portafolios de aprendizaje\n\n"
        
        estrategias += "🔄 <strong>2. Evaluación Formativa:</strong>\n"
        estrategias += "• Retroalimentación inmediata y constructiva\n"
        estrategias += "• Autoevaluación y coevaluación\n"
        estrategias += "• Evaluación entre pares\n"
        estrategias += "• Rúbricas detalladas y transparentes\n\n"
        
        estrategias += "📊 <strong>3. Evaluación Sumativa:</strong>\n"
        estrategias += "• Proyectos integradores\n"
        estrategias += "• Exámenes parciales y finales\n"
        estrategias += "• Presentaciones orales\n"
        estrategias += "• Casos de estudio\n\n"
        
        estrategias += "🛠️ <strong>4. Herramientas de Evaluación:</strong>\n"
        estrategias += "• Rúbricas con criterios claros\n"
        estrategias += "• Portafolios digitales\n"
        estrategias += "• Mapas conceptuales\n"
        estrategias += "• Diarios de aprendizaje\n\n"
        
        # Estrategias específicas según el rendimiento
        if promedio < 5.0:
            estrategias += "⚠️ <strong>Estrategias adicionales para bajo rendimiento:</strong>\n"
            estrategias += "• Evaluaciones más frecuentes y cortas\n"
            estrategias += "• Evaluaciones de recuperación\n"
            estrategias += "• Evaluaciones diferenciadas por nivel\n"
            estrategias += "• Más peso en evaluación formativa\n"
        
        return estrategias
    
    def generar_analisis_asistencia(self, stats, asignatura):
        asistencia = round(stats['asistencia_promedio'], 1)
        
        analisis = f"📈 <strong>Análisis de Asistencia - {asignatura.asignatura.nombre}</strong>\n\n"
        analisis += f"• <strong>Asistencia Promedio:</strong> {asistencia}%\n\n"
        
        if asistencia >= 90:
            analisis += "🎉 <strong>Excelente asistencia!</strong> Los estudiantes están muy comprometidos.\n\n"
            analisis += "💡 <strong>Sugerencias para mantener:</strong>\n"
            analisis += "• Continuar con actividades dinámicas\n"
            analisis += "• Reconocer el compromiso de los estudiantes\n"
            analisis += "• Mantener el nivel de exigencia\n"
        elif asistencia >= 80:
            analisis += "✅ <strong>Buena asistencia.</strong> Los estudiantes mantienen un buen compromiso.\n\n"
            analisis += "💡 <strong>Sugerencias para mejorar:</strong>\n"
            analisis += "• Implementar más actividades interactivas\n"
            analisis += "• Variar las metodologías de enseñanza\n"
            analisis += "• Fomentar la participación activa\n"
        elif asistencia >= 70:
            analisis += "⚠️ <strong>Asistencia regular.</strong> Hay espacio para mejorar.\n\n"
            analisis += "💡 <strong>Acciones recomendadas:</strong>\n"
            analisis += "• Implementar actividades más atractivas\n"
            analisis += "• Establecer sistema de incentivos\n"
            analisis += "• Comunicar la importancia de la asistencia\n"
            analisis += "• Considerar clases más dinámicas\n"
        else:
            analisis += "🔴 <strong>Asistencia baja.</strong> Se requieren acciones inmediatas.\n\n"
            analisis += "💡 <strong>Acciones urgentes:</strong>\n"
            analisis += "• Revisar la metodología de enseñanza\n"
            analisis += "• Implementar actividades más atractivas\n"
            analisis += "• Establecer comunicación directa con estudiantes\n"
            analisis += "• Considerar clases híbridas o grabadas\n"
            analisis += "• Evaluar si hay problemas externos afectando la asistencia\n"
        
        return analisis
    
    def generar_ayuda_general(self, asignatura):
        ayuda = f"🤖 <strong>Asistente IA - {asignatura.asignatura.nombre}</strong>\n\n"
        ayuda += "¡Hola! Soy tu asistente IA y puedo ayudarte con:\n\n"
        ayuda += "📊 <strong>Análisis y Reportes:</strong>\n"
        ayuda += "• Análisis de rendimiento general\n"
        ayuda += "• Estadísticas de asistencia\n"
        ayuda += "• Tendencias de evaluación\n\n"
        ayuda += "💡 <strong>Sugerencias y Recomendaciones:</strong>\n"
        ayuda += "• Estrategias de enseñanza\n"
        ayuda += "• Métodos de evaluación\n"
        ayuda += "• Retroalimentación efectiva\n"
        ayuda += "• Mejoras en la participación\n\n"
        ayuda += "🎯 <strong>Ejemplos de consultas:</strong>\n"
        ayuda += "• \"¿Cómo está el rendimiento de la clase?\"\n"
        ayuda += "• \"Necesito estrategias para mejorar la asistencia\"\n"
        ayuda += "• \"¿Qué métodos de evaluación recomiendas?\"\n"
        ayuda += "• \"Dame sugerencias de retroalimentación\"\n\n"
        ayuda += "¡Solo pregúntame lo que necesites! 😊"
        
        return ayuda
    
    def generar_respuesta_general(self, stats, asignatura):
        promedio = round(stats['promedio_general'], 1)
        asistencia = round(stats['asistencia_promedio'], 1)
        total_eval = stats['total_evaluaciones']
        
        respuesta = f"📋 <strong>Resumen General - {asignatura.asignatura.nombre}</strong>\n\n"
        respuesta += f"• <strong>Total de evaluaciones:</strong> {total_eval}\n"
        respuesta += f"• <strong>Promedio general:</strong> {promedio}\n"
        respuesta += f"• <strong>Asistencia promedio:</strong> {asistencia}%\n\n"
        
        respuesta += "💬 <strong>¿En qué aspecto específico necesitas ayuda?</strong>\n\n"
        respuesta += "Puedo asistirte con:\n"
        respuesta += "• 📊 Análisis detallado de rendimiento\n"
        respuesta += "• 💡 Sugerencias de retroalimentación\n"
        respuesta += "• 📚 Estrategias de evaluación\n"
        respuesta += "• 📈 Análisis de asistencia\n"
        respuesta += "• 🤖 Ayuda general y ejemplos\n\n"
        respuesta += "¡Solo dime qué te interesa analizar! 😊"
        
        return respuesta 