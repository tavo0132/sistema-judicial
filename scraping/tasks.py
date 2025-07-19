from celery import shared_task
import logging
from .scraper_colombia import main as scraper_main

# Configurar logging
logger = logging.getLogger(__name__)

@shared_task
def ejecutar_scraping():
    """
    Tarea que ejecuta el scraping automáticamente.
    """
    try:
        logger.info("Iniciando scraping automático...")
        print("Ejecutando scraping automáticamente...")
        
        # Ejecutar el scraping principal
        scraper_main()
        
        logger.info("Scraping completado exitosamente")
        return "Scraping completado exitosamente"
    except Exception as e:
        logger.error(f"Error durante el scraping: {str(e)}")
        return f"Error en scraping: {str(e)}"

@shared_task
def tarea_prueba():
    """
    Tarea de prueba para verificar que Celery funciona correctamente.
    """
    print("Celery está funcionando correctamente.")
    return "Tarea de prueba completada"