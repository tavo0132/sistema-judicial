from .models import Notificacion, LogAccionCliente

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

def crear_log_accion_cliente(cliente, administrador, accion, ip=None, observaciones=''):
    """
    Función de utilidad para crear logs de acciones sobre clientes.
    No afecta la lógica existente del sistema.
    """
    return LogAccionCliente.objects.create(
        cliente=cliente,
        administrador=administrador,
        accion=accion,
        ip=ip,
        observaciones=observaciones,
        cliente_nombre_completo=f"{cliente.first_name} {cliente.last_name}",
        cliente_email=cliente.email,
        cliente_cedula=cliente.cedula
    ) 