from .models import Notificacion

def crear_notificacion(tipo, titulo, mensaje, cliente=None, es_para_admin=False, url_relacionada=None):
    """
    Función de utilidad para crear notificaciones en el sistema.
    
    Args:
        tipo (str): Tipo de notificación (debe ser uno de los definidos en TIPOS_NOTIFICACION)
        titulo (str): Título de la notificación
        mensaje (str): Mensaje detallado de la notificación
        cliente (Cliente, optional): Cliente relacionado con la notificación
        es_para_admin (bool, optional): Si la notificación es para administradores
        url_relacionada (str, optional): URL relacionada con la notificación
    """
    try:
        notificacion = Notificacion.objects.create(
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            cliente=cliente,
            es_para_admin=es_para_admin,
            url_relacionada=url_relacionada
        )
        return notificacion
    except Exception as e:
        print(f"Error al crear notificación: {str(e)}")
        return None 