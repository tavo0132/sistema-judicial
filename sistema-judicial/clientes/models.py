from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from administradores.models import Administrador
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class Cliente(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    cedula = models.CharField(max_length=20, unique=True)
    numero_telefono = models.CharField(max_length=15)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    estado_cliente = models.CharField(max_length=20, default='Activo')
    fecha_registro = models.DateTimeField(default=timezone.now)
    ultima_sesion = models.DateTimeField(null=True, blank=True)  # <-- Nuevo campo
    
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
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='id_cliente')
    numero_radicado = models.CharField(max_length=50)
    fecha_radicado = models.DateTimeField(default=timezone.now)
    proceso_consultado = models.CharField(max_length=2, default='No')
    estado_radicado = models.CharField(max_length=20, default='Abierto')

    class Meta:
        db_table = 'radicaciones'

    def __str__(self):
        return f"Radicación {self.numero_radicado} - {self.cliente}"

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
