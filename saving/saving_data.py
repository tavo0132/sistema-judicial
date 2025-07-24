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
        rads = Radicacion.objects.filter(numero_radicado=numero_radicado)
        if not rads.exists():
            print(f"Radicación {numero_radicado} no existe en la base de datos. Saltando...")
            continue

        for rad in rads:
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
            print(f"Radicación {numero_radicado} actualizada correctamente para cliente {rad.cliente_id}.")

            # Notificar al cliente si tuvo actuación reciente
            try:
                from notifications.notifications_colombia import obtener_fecha_actuacion_reciente
                if item.get("tabla_actuaciones"):
                    fecha_reciente = obtener_fecha_actuacion_reciente(item["tabla_actuaciones"])
                    if fecha_reciente:
                        # Aquí deberías llamar a tu función de envío de correo, por ejemplo:
                        # enviar_correo_actuacion_reciente(rad.cliente, numero_radicado, fecha_reciente)
                        print(f"Notificación: Cliente {rad.cliente_id} - Radicado {numero_radicado} tuvo actuación reciente el {fecha_reciente}")
            except Exception as notif_ex:
                print(f"Error al notificar al cliente {rad.cliente_id}: {notif_ex}")

if __name__ == "__main__":
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scraping', 'resultados_scraping.json'))
    guardar_datos_desde_json(json_path)