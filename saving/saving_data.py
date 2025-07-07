import json
import os
import django
import sys

# Configura el entorno de Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_judicial.settings')
django.setup()

from clientes.models import Radicacion, Cliente
from django.utils import timezone
from datetime import datetime

def guardar_datos_desde_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        datos = json.load(f)

    for item in datos:
        numero_radicado = item.get("numero_radicado")
        try:
            rad = Radicacion.objects.get(numero_radicado=numero_radicado)
        except Radicacion.DoesNotExist:
            print(f"Radicación {numero_radicado} no existe en la base de datos. Saltando...")
            continue

        if item.get("fecha_radicado"):
            try:
                fecha = datetime.strptime(item["fecha_radicado"], "%Y-%m-%d")
                rad.fecha_radicado = timezone.make_aware(fecha)
            except Exception:
                rad.fecha_radicado = None

        if item.get("fecha_ultima_actuacion"):
            try:
                fecha = datetime.strptime(item["fecha_ultima_actuacion"], "%Y-%m-%d")
                rad.fecha_ultima_actuacion = timezone.make_aware(fecha)
            except Exception:
                rad.fecha_ultima_actuacion = None

        if item.get("despacho_departamento"):
            rad.despacho_departamento = item["despacho_departamento"]

        if item.get("sujetos_procesales"):
            rad.sujetos_procesales = item["sujetos_procesales"]

        rad.save()
        print(f"Radicación {numero_radicado} actualizada correctamente.")

if __name__ == "__main__":
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scraping', 'resultados_scraping.json'))
    guardar_datos_desde_json(json_path)