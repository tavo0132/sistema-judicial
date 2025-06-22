from django.db import models
from clientes.models import Radicacion

class ResultadoScraping(models.Model):
    radicacion = models.ForeignKey(Radicacion, on_delete=models.CASCADE)
    fecha_actuacion = models.DateField()
    descripcion = models.TextField()
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_actuacion']
        
    def __str__(self):
        return f"Actuación {self.fecha_actuacion} - {self.radicacion.numero_radicado}"

class Cliente(models.Model):
    # ...otros campos...
    password = models.CharField(max_length=128)
    # ...otros campos...

class Administrador(models.Model):
    id_administrador = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    numero_telefono = models.CharField(max_length=20, blank=True, null=True)
    correo_electronico = models.CharField(max_length=100, unique=True)
    contrasena_hash = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_sesion = models.DateTimeField(null=True, blank=True)  # <-- Nuevo campo

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class LogAccesoAdministrador(models.Model):
    administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)  # Opcional

    def __str__(self):
        return f"{self.administrador} - {self.fecha_hora}"