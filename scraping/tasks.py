from celery import shared_task

@shared_task
def ejecutar_scraping():
    # Lógica del scraping
    print("Ejecutando scraping automáticamente...")
    return "Scraping completado"