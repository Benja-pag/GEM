#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para poblar el foro con temas y mensajes de ejemplo.
"""

import os
import sys
import django
import random

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.models import Foro, MensajeForo, Usuario

def poblar_foro():
    """
    Crea temas y mensajes de ejemplo en el foro.
    """
    print("🗑️ Limpiando datos del foro anterior...")
    Foro.objects.all().delete()
    MensajeForo.objects.all().delete()
    
    print("👥 Obteniendo usuarios (autores)...")
    autores = list(Usuario.objects.all())
    if not autores:
        print("❌ No hay usuarios en la base de datos. No se puede poblar el foro.")
        return
        
    print(f"✅ {len(autores)} usuarios encontrados.")

    temas_foro = [
        {
            "titulo": "¡Bienvenidos al nuevo foro del colegio!",
            "contenido": "Este es el primer tema en nuestro nuevo foro. Esperamos que sea un espacio para compartir ideas, resolver dudas y mantenernos todos conectados. ¡Participa y ayúdanos a construir una gran comunidad!",
            "respuestas": [
                "¡Qué buena iniciativa! Me parece genial tener un lugar para comunicarnos.",
                "Gracias por crear este espacio. Será muy útil para todos.",
                "¡Excelente! Ya tengo algunas ideas para proponer.",
            ]
        },
        {
            "titulo": "Dudas sobre las fechas de los próximos exámenes",
            "contenido": "¿Alguien sabe si ya están publicadas las fechas de los exámenes finales? No las encuentro en el calendario.",
            "respuestas": [
                "Creo que las publican la próxima semana. El año pasado fue así.",
                "Le pregunté a un profesor y me dijo que estaban por confirmarse.",
                "Estén atentos a la sección de noticias del panel, seguro lo anuncian ahí.",
            ]
        },
        {
            "titulo": "Organización del evento de fin de año",
            "contenido": "¡Hola a todos! Estamos buscando voluntarios para ayudar a organizar la fiesta de fin de año. Necesitamos gente para decoración, música y logística. ¿Quién se anota?",
            "respuestas": [
                "¡Yo me apunto para la decoración! Tengo algunas ideas.",
                "A mí me gustaría ayudar con la música, puedo hacer una playlist.",
                "Cuenten conmigo para lo que sea, me avisan dónde ayudar.",
                "¿Habrá un presupuesto para las actividades? Sería bueno saberlo.",
            ]
        },
    ]

    print("\n📝 Creando temas y mensajes en el foro...")
    for tema_data in temas_foro:
        autor_tema = random.choice(autores)
        
        tema = Foro.objects.create(
            titulo=tema_data["titulo"],
            asunto=tema_data["titulo"],
            contenido=tema_data["contenido"],
            autor=autor_tema
        )
        print(f"  -> Tema creado: '{tema.titulo}' por {autor_tema.nombre}")

        for respuesta_contenido in tema_data["respuestas"]:
            autor_respuesta = random.choice(autores)
            MensajeForo.objects.create(
                foro=tema,
                autor=autor_respuesta,
                contenido=respuesta_contenido
            )
            print(f"    - Respuesta añadida por {autor_respuesta.nombre}")
            
    print("\n🎉 ¡Foro poblado con éxito!")

if __name__ == '__main__':
    poblar_foro() 