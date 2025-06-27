from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.conf import settings
import json
import requests
import os

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