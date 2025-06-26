import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GEM.settings')
django.setup()

from Core.views.admin import get_eventos_calendario_admin

print("=== PROBANDO get_eventos_calendario_admin() ===")
eventos = get_eventos_calendario_admin()
print(f"Total eventos encontrados: {len(eventos)}")

for evento in eventos:
    print(f"- ID: {evento['id']}")
    print(f"  Título: {evento['title']}")
    print(f"  Fecha/Hora: {evento['start']}")
    print(f"  Tipo: {evento['extendedProps']['type']}")
    print(f"  Color: {evento['color']}")
    print("---")

# Buscar específicamente el evento "Evento Debug Modal"
evento_debug = None
for evento in eventos:
    if "Evento Debug Modal" in evento['title']:
        evento_debug = evento
        break

if evento_debug:
    print(f"\n✅ ENCONTRADO: {evento_debug['title']}")
    print(f"   Start: {evento_debug['start']}")
    print(f"   ID: {evento_debug['id']}")
else:
    print("\n❌ NO ENCONTRADO: Evento Debug Modal") 