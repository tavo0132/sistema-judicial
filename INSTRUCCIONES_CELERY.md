# INSTRUCCIONES PARA EJECUTAR EL SISTEMA JUDICIAL CON CELERY

## Servicios necesarios:
1. ✅ Redis/Memurai (ya está corriendo en puerto 6379)
2. ⏳ Worker de Celery
3. ⏳ Scheduler de Celery Beat
4. ⏳ Servidor Django

## Pasos a seguir:

### 1. Verificar configuración (OPCIONAL)
Ejecuta en PowerShell:
```
.\verificar_config.bat
```

### 2. Iniciar Worker de Celery (NUEVA VENTANA)
Abre una nueva ventana de PowerShell y ejecuta:
```
cd "C:\Users\Gustavo\Documents\Dev\Lenguajes\Python\Fullstack\sistema-judicial-master"
.\start_worker.bat
```

### 3. Iniciar Celery Beat (NUEVA VENTANA)
Abre otra nueva ventana de PowerShell y ejecuta:
```
cd "C:\Users\Gustavo\Documents\Dev\Lenguajes\Python\Fullstack\sistema-judicial-master"
.\start_beat.bat
```

### 4. Iniciar Django (NUEVA VENTANA)
Abre otra nueva ventana de PowerShell y ejecuta:
```
cd "C:\Users\Gustavo\Documents\Dev\Lenguajes\Python\Fullstack\sistema-judicial-master"
.\start_django.bat
```

## Tareas programadas configuradas:

- **Scraping diario**: Todos los días a las 7:00 AM (configuración por defecto)
- **Scraping cada 6 horas**: A las 00:00, 06:00, 12:00, 18:00 (como respaldo)
- **Tarea de prueba**: Cada 5 minutos (solo para verificar que funciona)

## Nueva funcionalidad de programación desde el Dashboard:

Ahora puedes programar consultas automáticas directamente desde el Dashboard de Administradores:

1. **Programar nueva consulta**: Selecciona una hora y la consulta se ejecutará automáticamente todos los días
2. **Ver consulta activa**: El dashboard muestra si hay una consulta programada y a qué hora
3. **Cancelar programación**: Puedes cancelar la programación automática cuando quieras

Esta programación usa Celery Beat y se guarda en la base de datos, por lo que persiste entre reinicios del sistema.

## Para probar manualmente:

### Ejecutar scraping inmediatamente:
```python
from scraping.tasks import ejecutar_scraping
result = ejecutar_scraping.delay()
print(f"Tarea enviada: {result.id}")
```

### Ejecutar tarea de prueba:
```python
from clientes.tasks import tarea_prueba
result = tarea_prueba.delay()
print(f"Tarea enviada: {result.id}")
```

## Notas importantes:

1. Deja todas las ventanas abiertas mientras uses el sistema
2. Si cierras alguna ventana, tendrás que reiniciar ese servicio
3. El scraping se ejecutará automáticamente según la programación
4. Puedes ver los logs en las ventanas de Worker y Beat
5. Para detener cualquier servicio, presiona Ctrl+C en su ventana

## Resolución de problemas:

- Si Redis no está disponible, reinicia Memurai
- Si hay errores de importación, verifica que el entorno virtual esté activado
- Si las tareas no se ejecutan, verifica que Worker y Beat estén corriendo
- Si Django no inicia, verifica la conexión a la base de datos
