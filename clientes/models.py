from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from administradores.models import Administrador

class Cliente(models.Model):
    ESTADO_CHOICES = [
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    ]

    id_cliente = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    correo_electronico = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128)
    estado_cliente = models.CharField(max_length=20, default='Activo')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    numero_telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200, null=True, blank=True)
    ciudad = models.CharField(max_length=100)
    token_recuperacion = models.CharField(max_length=100, null=True, blank=True)
    id_administrador = models.ForeignKey(Administrador, on_delete=models.SET_NULL, null=True, db_column='id_administrador')

    class Meta:
        db_table = 'clientes'

    def set_password(self, raw_password):
        self.contrasena = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class Radicacion(models.Model):
    id_radicacion = models.BigAutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='id_cliente', null=True)
    numero_radicado = models.CharField(max_length=50, unique=True)
    fecha_radicado = models.DateField()
    fecha_ultima_actuacion = models.DateField(null=True, blank=True)
    despacho_departamento = models.CharField(max_length=200, null=True, blank=True)
    sujetos_procesales = models.TextField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    ESTADO_CHOICES = [
        ('Abierto', 'Abierto'),
        ('Cerrado', 'Cerrado'),
    ]
    estado_radicado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Abierto')
    
    PROCESO_CONSULTADO_CHOICES = [
        ('Si', 'Si'),
        ('No', 'No'),
    ]
    proceso_consultado = models.CharField(max_length=3, choices=PROCESO_CONSULTADO_CHOICES, default='No')

    class Meta:
        db_table = 'radicaciones'

    def __str__(self):
        return f"Radicado: {self.numero_radicado}"
