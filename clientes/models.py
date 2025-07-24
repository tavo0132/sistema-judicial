from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from administradores.models import Administrador
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class Cliente(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    cedula = models.CharField(max_length=20, unique=True)
    numero_telefono = models.CharField(max_length=15)
    ciudad = models.CharField(max_length=100)
    estado_cliente = models.CharField(max_length=20, default='Activo')
    fecha_registro = models.DateTimeField(default=timezone.now)
    ultima_sesion = models.DateTimeField(null=True, blank=True)  # <-- Nuevo campo
    pais = models.CharField(max_length=30, choices=[('Colombia', 'Colombia'), ('Ecuador', 'Ecuador')], default='Colombia')  # <-- Nuevo campo
    
    # Campos para soft delete - NO AFECTAN LA LÓGICA EXISTENTE
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de eliminación')
    deleted_by = models.ForeignKey('administradores.Administrador', on_delete=models.SET_NULL, null=True, blank=True, related_name='clientes_eliminados', verbose_name='Eliminado por')
    
    # Sobrescribir el campo email para hacerlo único
    email = models.EmailField(unique=True)
    
    # Configurar para usar email como campo de autenticación
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    # Agregamos related_name para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='cliente_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='cliente_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    class Meta:
        db_table = 'clientes'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    # Métodos para soft delete - NO AFECTAN LA LÓGICA EXISTENTE
    def soft_delete(self, admin_user=None):
        """Marca el cliente como eliminado sin borrarlo de la base de datos"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = admin_user
        self.is_active = False  # Desactivar usuario para que no pueda loguearse
        self.save()
    
    def restore(self):
        """Restaura un cliente eliminado"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.is_active = True  # Reactivar usuario
        self.save()
    
    @property
    def esta_eliminado(self):
        """Propiedad para verificar si el cliente está eliminado"""
        return self.is_deleted

class Radicacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    numero_radicado = models.CharField(max_length=50)  # Quitamos unique=True para permitir duplicados globales
    fecha_radicacion = models.DateField(blank=True, null=True)
    ultima_actuacion = models.DateField(blank=True, null=True)  # Nuevo campo
    estado_radicado = models.CharField(max_length=20, default='abierto')
    PROCESO_CONSULTADO_CHOICES = [
        ('Sí', 'Sí'),
        ('No', 'No'),
    ]
    proceso_consultado = models.CharField(max_length=5, choices=PROCESO_CONSULTADO_CHOICES, default='No')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    despacho_departamento = models.CharField(max_length=255, null=True, blank=True)
    sujetos_procesales = models.CharField(max_length=500, null=True, blank=True)
    
    class Meta:
        db_table = 'radicaciones'
        # Restricción única: un cliente no puede tener el mismo número de radicado dos veces
        # pero diferentes clientes sí pueden tener el mismo número
        unique_together = ('cliente', 'numero_radicado')

    def __str__(self):
        return f"{self.numero_radicado} - {self.cliente}"

class Notificacion(models.Model):
    tipo = models.CharField(max_length=50)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(default=timezone.now)
    es_para_admin = models.BooleanField(default=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    url_relacionada = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return f"{self.titulo} - {self.fecha_creacion}"

class LogAccesoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.cliente} - {self.fecha_hora}"

class LogAccionCliente(models.Model):
    """Log de acciones administrativas sobre clientes (eliminar/restaurar)"""
    ACCIONES_CHOICES = [
        ('eliminar', 'Eliminar Cliente'),
        ('restaurar', 'Restaurar Cliente'),
        ('editar', 'Editar Cliente'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='logs_acciones')
    administrador = models.ForeignKey('administradores.Administrador', on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=20, choices=ACCIONES_CHOICES)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    observaciones = models.TextField(blank=True, help_text='Detalles adicionales de la acción')
    
    # Datos del cliente al momento de la acción (para historial)
    cliente_nombre_completo = models.CharField(max_length=200)
    cliente_email = models.EmailField()
    cliente_cedula = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'logs_acciones_cliente'
        ordering = ['-fecha_hora']
        verbose_name = 'Log de Acción Cliente'
        verbose_name_plural = 'Logs de Acciones Cliente'
    
    def __str__(self):
        return f"{self.accion.title()} - {self.cliente_nombre_completo} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
