from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Administrador(models.Model):
    id_administrador = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    numero_telefono = models.CharField(max_length=20, null=True, blank=True)
    correo_electronico = models.EmailField(max_length=100, unique=True)
    contrasena_hash = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'administradores'

    def set_password(self, raw_password):
        self.contrasena_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena_hash)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class LogAccesoAdministrador(models.Model):
    administrador = models.ForeignKey('Administrador', on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.administrador} - {self.fecha_hora}"
