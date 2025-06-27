"""
Servicio para manejar las interacciones con la IA en el sistema GEM.
"""

import os
import json
import openai
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.core.cache import cache
from django.db.models import Avg
from django.core.exceptions import PermissionDenied
from django.conf import settings
from .ia_config import TEMPLATES, OPENAI_CONFIG, ERROR_MESSAGES
import logging

logger = logging.getLogger(__name__)

class IAService:
    """Servicio para manejar las interacciones con IA."""
    
    def __init__(self):
        """Inicializa el servicio de IA."""
        self.api_key = settings.OPENAI_API_KEY
        openai.api_key = self.api_key
        self._initialize_rate_limiter()

    def _initialize_rate_limiter(self):
        """Inicializa el control de límites de uso."""
        self.last_request_time = datetime.now()
        self.request_count = 0
        self.daily_request_count = 0

    def _check_rate_limits(self) -> bool:
        """Verifica los límites de uso."""
        now = datetime.now()
        
        # Reiniciar contadores diarios
        if (now - self.last_request_time).days > 0:
            self.daily_request_count = 0
            
        # Verificar límites
        if self.daily_request_count >= ia_config.MAX_REQUESTS_PER_DAY:
            raise Exception(ia_config.ERROR_MESSAGES["rate_limit"])
            
        if (now - self.last_request_time).seconds < 60 and self.request_count >= ia_config.MAX_REQUESTS_PER_MINUTE:
            raise Exception(ia_config.ERROR_MESSAGES["rate_limit"])
            
        return True

    def _validate_content(self, content: str) -> bool:
        """Valida el contenido generado."""
        # Verificar palabras prohibidas
        for palabra in ia_config.CONTENT_RESTRICTIONS["palabras_prohibidas"]:
            if palabra.lower() in content.lower():
                return False
                
        # Verificar temas sensibles
        for tema in ia_config.CONTENT_RESTRICTIONS["temas_sensibles"]:
            if tema.lower() in content.lower():
                return False
                
        # Verificar datos personales
        for dato in ia_config.CONTENT_RESTRICTIONS["datos_personales"]:
            if dato.lower() in content.lower():
                return False
                
        return True

    def _check_data_access(self, user_role: str, data_type: str, access_level: str) -> bool:
        """Verifica los permisos de acceso a datos."""
        if user_role not in ia_config.ACCESS_HIERARCHY:
            return False
            
        if data_type not in ia_config.DATA_VISIBILITY_RULES:
            return False
            
        allowed_roles = ia_config.DATA_VISIBILITY_RULES[data_type].get(access_level, [])
        return user_role in allowed_roles

    def _filter_sensitive_data(self, data: Dict, user_role: str) -> Dict:
        """Filtra datos sensibles según el rol del usuario."""
        if user_role not in ia_config.SENSITIVE_FIELDS:
            return {}
            
        filtered_data = data.copy()
        sensitive_fields = ia_config.SENSITIVE_FIELDS[user_role]
        
        for field in sensitive_fields:
            if field in filtered_data:
                del filtered_data[field]
                
        return filtered_data

    async def generate_response(self, template_name: str, user_role: str, user_id: Optional[int] = None, **kwargs) -> Dict:
        """Genera una respuesta usando la IA."""
        # Verificar límites de uso
        self._check_rate_limits()
        
        # Formatear el prompt
        prompt = self._format_prompt(template_name, **kwargs)
        
        try:
            # Llamar a la API de OpenAI
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un asistente educativo experto."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Procesar y validar la respuesta
            content = response.choices[0].message.content
            if not self._validate_content(content):
                raise Exception(ia_config.ERROR_MESSAGES["content_restricted"])
                
            # Estructurar la respuesta
            return self._process_response(template_name, content)
            
        except Exception as e:
            logger.error(f"Error al llamar a la API: {str(e)}")
            raise

    def _format_prompt(self, template_name: str, **kwargs) -> str:
        """Formatea el prompt según la plantilla."""
        if template_name not in ia_config.PROMPT_TEMPLATES:
            raise Exception("Plantilla no encontrada")
            
        template = ia_config.PROMPT_TEMPLATES[template_name]
        return template.format(**kwargs)

    def _process_response(self, template_name: str, content: str) -> Dict:
        """Procesa la respuesta de la IA."""
        # Estructurar la respuesta según el tipo
        if template_name.startswith('reporte'):
            return self._structure_text_response('reporte', content)
        elif template_name.startswith('sugerencias'):
            return self._structure_text_response('sugerencias', content)
        elif template_name.startswith('comunicado'):
            return self._structure_text_response('comunicado', content)
        else:
            return self._structure_text_response('analisis', content)

    def _structure_text_response(self, response_type: str, content: str) -> Dict:
        """Estructura el texto de respuesta según el tipo."""
        if response_type not in ia_config.RESPONSE_STRUCTURE:
            raise Exception("Tipo de respuesta no válido")
            
        # Aquí iría la lógica para estructurar la respuesta según el tipo
        # Por ahora, retornamos una estructura básica
        return {
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "type": response_type
        }

    def generar_reporte(self, tipo: str, curso_id: int, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un reporte usando IA."""
        try:
            template = TEMPLATES.get(f'reporte_{tipo}')
            if not template:
                raise ValueError(f"Tipo de reporte no válido: {tipo}")
            
            prompt = self._generar_prompt(template, contexto)
            response = self._llamar_api(prompt)
            
            return self._procesar_respuesta_reporte(response)
        except Exception as e:
            logger.error(f"Error al generar reporte: {str(e)}")
            raise
    
    def generar_sugerencias(self, tipo: str, curso_id: int, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Genera sugerencias usando IA."""
        try:
            template = TEMPLATES.get(f'sugerencias_{tipo}')
            if not template:
                raise ValueError(f"Tipo de sugerencias no válido: {tipo}")
            
            prompt = self._generar_prompt(template, contexto)
            response = self._llamar_api(prompt)
            
            return self._procesar_respuesta_sugerencias(response)
        except Exception as e:
            logger.error(f"Error al generar sugerencias: {str(e)}")
            raise
    
    def generar_comunicado(self, tipo: str, curso_id: int, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un comunicado usando IA."""
        try:
            template = TEMPLATES.get(f'comunicado_{tipo}')
            if not template:
                raise ValueError(f"Tipo de comunicado no válido: {tipo}")
            
            prompt = self._generar_prompt(template, contexto)
            response = self._llamar_api(prompt)
            
            return self._procesar_respuesta_comunicado(response)
        except Exception as e:
            logger.error(f"Error al generar comunicado: {str(e)}")
            raise
    
    def procesar_mensaje_chat(self, mensaje: str, curso_id: int, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un mensaje del chat usando IA."""
        try:
            template = TEMPLATES.get('chat')
            if not template:
                raise ValueError("Template de chat no encontrado")
            
            contexto_chat = {
                **contexto,
                'mensaje': mensaje
            }
            
            prompt = self._generar_prompt(template, contexto_chat)
            response = self._llamar_api(prompt)
            
            return {
                'respuesta': response.get('content', 'Lo siento, no pude procesar tu mensaje.')
            }
        except Exception as e:
            logger.error(f"Error al procesar mensaje de chat: {str(e)}")
            raise
    
    def exportar_reporte(self, reporte_id: str, formato: str) -> str:
        """Exporta un reporte en el formato especificado."""
        try:
            # Aquí iría la lógica para exportar el reporte
            # Por ahora retornamos una URL de ejemplo
            return f"/media/reportes/{reporte_id}.{formato}"
        except Exception as e:
            logger.error(f"Error al exportar reporte: {str(e)}")
            raise
    
    def aplicar_sugerencias(self, sugerencias_id: str, curso_id: int) -> bool:
        """Aplica las sugerencias al curso especificado."""
        try:
            # Aquí iría la lógica para aplicar las sugerencias
            # Por ahora solo retornamos True
            return True
        except Exception as e:
            logger.error(f"Error al aplicar sugerencias: {str(e)}")
            raise
    
    def enviar_comunicado(self, comunicado_id: str, destinatarios: List[str]) -> bool:
        """Envía el comunicado a los destinatarios especificados."""
        try:
            # Aquí iría la lógica para enviar el comunicado
            # Por ahora solo retornamos True
            return True
        except Exception as e:
            logger.error(f"Error al enviar comunicado: {str(e)}")
            raise
    
    def _generar_prompt(self, template: str, contexto: Dict[str, Any]) -> str:
        """Genera el prompt para la IA usando el template y contexto."""
        try:
            return template.format(**contexto)
        except KeyError as e:
            logger.error(f"Error al generar prompt: Falta la variable {str(e)}")
            raise ValueError(f"Falta información requerida: {str(e)}")
        except Exception as e:
            logger.error(f"Error al generar prompt: {str(e)}")
            raise
    
    def _llamar_api(self, prompt: str) -> Dict[str, Any]:
        """Realiza la llamada a la API de OpenAI."""
        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_CONFIG['model'],
                messages=[
                    {"role": "system", "content": "Eres un asistente educativo experto."},
                    {"role": "user", "content": prompt}
                ],
                temperature=OPENAI_CONFIG['temperature'],
                max_tokens=OPENAI_CONFIG['max_tokens']
            )
            
            return response.choices[0].message
        except Exception as e:
            logger.error(f"Error al llamar a la API: {str(e)}")
            raise
    
    def _procesar_respuesta_reporte(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa la respuesta de la IA para un reporte."""
        try:
            contenido = json.loads(response.get('content', '{}'))
            return {
                'titulo': contenido.get('titulo', 'Reporte'),
                'contenido': contenido.get('contenido', []),
                'recomendaciones': contenido.get('recomendaciones', [])
            }
        except json.JSONDecodeError:
            return {
                'titulo': 'Reporte',
                'contenido': [response.get('content', '')],
                'recomendaciones': []
            }
    
    def _procesar_respuesta_sugerencias(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa la respuesta de la IA para sugerencias."""
        try:
            contenido = json.loads(response.get('content', '{}'))
            return {
                'area': contenido.get('area', 'General'),
                'sugerencias': contenido.get('sugerencias', []),
                'recursos': contenido.get('recursos', [])
            }
        except json.JSONDecodeError:
            return {
                'area': 'General',
                'sugerencias': [{'titulo': 'Sugerencia', 'descripcion': response.get('content', '')}],
                'recursos': []
            }
    
    def _procesar_respuesta_comunicado(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa la respuesta de la IA para un comunicado."""
        try:
            contenido = json.loads(response.get('content', '{}'))
            return {
                'asunto': contenido.get('asunto', 'Comunicado'),
                'contenido': contenido.get('contenido', ''),
                'tipo': contenido.get('tipo', 'general')
            }
        except json.JSONDecodeError:
            return {
                'asunto': 'Comunicado',
                'contenido': response.get('content', ''),
                'tipo': 'general'
            } 