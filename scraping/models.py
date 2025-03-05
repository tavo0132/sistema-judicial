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