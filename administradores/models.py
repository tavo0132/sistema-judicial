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

class ConsultaProgramada(models.Model):
    hora = models.TimeField()
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.hora}"

class ProgramacionMultiple(models.Model):
    """
    Modelo para manejar múltiples horarios de programación
    """
    SLOTS = [
        ('slot1', 'Horario 1'),
        ('slot2', 'Horario 2'), 
        ('slot3', 'Horario 3'),
    ]
    
    slot = models.CharField(max_length=10, choices=SLOTS, unique=True)
    hora = models.TimeField()
    activo = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Programación Múltiple"
        verbose_name_plural = "Programaciones Múltiples"
        ordering = ['slot']
    
    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.get_slot_display()}: {self.hora} ({estado})"
    
    def get_task_name(self):
        """Genera un nombre único para la tarea de Celery"""
        return f"consulta-procesos-{self.slot}"
