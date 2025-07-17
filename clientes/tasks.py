from celery import shared_task

@shared_task
def tarea_prueba():
    print("Celery está funcionando correctamente.")
    return "OK"