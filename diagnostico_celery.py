import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_judicial.settings')
django.setup()

from django_celery_beat.models import PeriodicTask, CrontabSchedule
from administradores.models import ProgramacionMultiple

def verificar_sistema():
    print("="*60)
    print("   DIAGNÓSTICO DEL SISTEMA DE PROGRAMACIÓN")
    print("="*60)
    print()
    
    # 1. Verificar conexión a Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis/Memurai: CONECTADO")
    except Exception as e:
        print(f"✗ Redis/Memurai: ERROR - {e}")
    
    print()
    
    # 2. Verificar tareas periódicas en Celery Beat
    print("--- TAREAS PERIÓDICAS EN CELERY BEAT ---")
    tareas_activas = PeriodicTask.objects.filter(enabled=True)
    if tareas_activas.exists():
        for task in tareas_activas:
            print(f"Nombre: {task.name}")
            print(f"Task: {task.task}")
            if task.crontab:
                print(f"Horario: {task.crontab}")
            print(f"Última ejecución: {task.last_run_at}")
            print(f"Total ejecuciones: {task.total_run_count}")
            print("-" * 40)
    else:
        print("⚠ No hay tareas periódicas activas en Celery Beat")
    
    print()
    
    # 3. Verificar programaciones en nuestro modelo
    print("--- HORARIOS EN NUESTRO MODELO ---")
    programaciones = ProgramacionMultiple.objects.all()
    if programaciones.exists():
        for prog in programaciones:
            print(f"Slot: {prog.slot}")
            print(f"Hora: {prog.hora}")
            print(f"Activo: {prog.activo}")
            print(f"Fecha creación: {prog.fecha_creacion}")
            print("-" * 40)
    else:
        print("⚠ No hay horarios programados en el modelo")
    
    print()
    
    # 4. Verificar configuración de Celery
    print("--- CONFIGURACIÓN DE CELERY ---")
    from django.conf import settings
    print(f"CELERY_BROKER_URL: {getattr(settings, 'CELERY_BROKER_URL', 'NO CONFIGURADO')}")
    print(f"CELERY_TIMEZONE: {getattr(settings, 'CELERY_TIMEZONE', 'NO CONFIGURADO')}")
    print(f"CELERY_BEAT_SCHEDULER: {getattr(settings, 'CELERY_BEAT_SCHEDULER', 'NO CONFIGURADO')}")
    
    print()
    
    # 5. Verificar hora actual
    print("--- INFORMACIÓN DE TIEMPO ---")
    print(f"Hora actual del sistema: {datetime.now()}")
    print(f"Zona horaria configurada: {getattr(settings, 'TIME_ZONE', 'NO CONFIGURADO')}")
    
    print()
    print("="*60)
    print("   DIAGNÓSTICO COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    verificar_sistema()
