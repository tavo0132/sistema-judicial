from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from administradores.models import Administrador
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class Cliente(AbstractUser):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    id = models.BigAutoField(primary_key=True)
    cedula = models.CharField(max_length=20, unique=True)
    numero_telefono = models.CharField(max_length=15)
    ciudad = models.CharField(max_length=100)
    estado_cliente = models.CharField(max_length=20, default='Activo')
    fecha_registro = models.DateTimeField(default=timezone.now)
    ultima_sesion = models.DateTimeField(null=True, blank=True)  # <-- Nuevo campo
    pais = models.CharField(max_length=30, choices=[('Colombia', 'Colombia'), ('Ecuador', 'Ecuador')], default='Colombia')  # <-- Nuevo campo
    
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

class Radicacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    numero_radicado = models.CharField(max_length=50)  # Quitamos unique=True para permitir duplicados globales
    fecha_radicacion = models.DateField(blank=True, null=True)
    ultima_actuacion = models.DateField(blank=True, null=True)  # Nuevo campo
    estado_radicado = models.CharField(max_length=20, choices=[('Abierto', 'Abierto'), ('Cerrado', 'Cerrado')], default='Abierto')
    PROCESO_CONSULTADO_CHOICES = [
        ('Sí', 'Sí'),
        ('No', 'No'),
    ]
    proceso_consultado = models.CharField(max_length=5, choices=PROCESO_CONSULTADO_CHOICES, default='No')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    despacho_departamento = models.CharField(max_length=255, null=True, blank=True)
    sujetos_procesales = models.CharField(max_length=500, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    
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
