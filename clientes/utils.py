from .models import Notificacion

def crear_notificacion(tipo, titulo, mensaje, es_para_admin=False, cliente=None, url_relacionada=''):
    """
    Función de utilidad para crear notificaciones en el sistema.
    """
    return Notificacion.objects.create(
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        es_para_admin=es_para_admin,
        cliente=cliente,
        url_relacionada=url_relacionada
    ) 