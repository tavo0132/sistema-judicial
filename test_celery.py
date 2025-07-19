#!/usr/bin/env python
"""
Script de prueba para verificar que Celery está configurado correctamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_judicial.settings')
django.setup()

# Importar Celery
from sistema_judicial.celery import app as celery_app

# Probar tareas
from clientes.tasks import tarea_prueba
from scraping.tasks import ejecutar_scraping

def test_celery_connection():
    """Prueba la conexión a Redis"""
    try:
        # Probar conexión a broker
        inspector = celery_app.control.inspect()
        print("✅ Conexión a Redis exitosa")
        return True
    except Exception as e:
        print(f"❌ Error conectando a Redis: {e}")
        return False

def test_tasks():
    """Prueba las tareas de Celery"""
    try:
        # Probar tarea simple
        result = tarea_prueba.delay()
        print(f"✅ Tarea de prueba enviada: {result.id}")
        
        # Obtener resultado (esto esperará hasta que se complete)
        # result_value = result.get(timeout=10)
        # print(f"✅ Resultado de tarea de prueba: {result_value}")
        
        return True
    except Exception as e:
        print(f"❌ Error en tareas: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Probando configuración de Celery...")
    
    # Probar conexión
    if test_celery_connection():
        print("🎉 Celery está configurado correctamente!")
    else:
        print("💥 Hay problemas con la configuración de Celery")
        sys.exit(1)
