# Sistema Judicial - Guía de Despliegue

## 📋 Requisitos Previos

### Software Necesario
- **Python 3.8+** instalado en el sistema
- **Redis/Memurai** como broker de mensajes
- **MySQL** como base de datos
- **Google Chrome** o **Chromium** para scraping

### Dependencias Python
Todas las dependencias están listadas en `requirements.txt`

---

## 🚀 Método 1: Inicio Automático (Recomendado)

### Paso Único
```bash
# Ejecutar el archivo de inicio automático
start_all_services.bat
```

Este comando iniciará automáticamente:
- ✅ Verificación de Redis/Memurai
- ✅ Celery Beat (Programador de tareas)
- ✅ Celery Worker (Ejecutor de tareas) 
- ✅ Servidor Django

### Para Detener Todos los Servicios
```bash
# Ejecutar el archivo de detención
stop_all_services.bat
```

---

## 🔧 Método 2: Inicio Manual Paso a Paso

### Paso 1: Preparar el Entorno
```bash
# Navegar al directorio del proyecto
cd "C:\Users\Gustavo\Documents\Dev\Lenguajes\Python\Fullstack\sistema-judicial-master"

# Activar entorno virtual
venv\Scripts\activate

# Verificar instalación de dependencias (si es necesario)
pip install -r requirements.txt
```

### Paso 2: Iniciar Redis/Memurai
```bash
# Opción A: Si Memurai está instalado como servicio
net start memurai

# Opción B: Ejecutar manualmente
# Navegar a la carpeta de instalación de Memurai
C:\Program Files\Memurai\memurai.exe

# Opción C: Si usas Redis tradicional
redis-server
```

### Paso 3: Verificar Base de Datos
```bash
# Aplicar migraciones si es necesario
python manage.py migrate

# Crear superusuario si es la primera vez
python manage.py createsuperuser
```

### Paso 4: Iniciar Celery Beat (Terminal 1)
```bash
# Activar entorno virtual
venv\Scripts\activate

# Iniciar el programador de tareas
python -m celery -A sistema_judicial beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Paso 5: Iniciar Celery Worker (Terminal 2)
```bash
# Activar entorno virtual
venv\Scripts\activate

# Iniciar el worker de tareas
python -m celery -A sistema_judicial worker -l info
```

### Paso 6: Iniciar Servidor Django (Terminal 3)
```bash
# Activar entorno virtual
venv\Scripts\activate

# Iniciar servidor de desarrollo
python manage.py runserver 127.0.0.1:8000
```

---

## 🌐 URLs de Acceso

Una vez iniciados todos los servicios:

- **Aplicación Principal**: http://127.0.0.1:8000
- **Admin Django**: http://127.0.0.1:8000/admin
- **Dashboard Administrador**: http://127.0.0.1:8000/administradores/dashboard/
- **Login Cliente**: http://127.0.0.1:8000/clientes/login/

---

## 🔍 Verificación de Servicios

### Verificar Redis/Memurai
```bash
# Conectar a Redis para verificar
redis-cli ping
# Respuesta esperada: PONG
```

### Verificar Celery
- **Beat**: Debe mostrar mensajes de programación de tareas
- **Worker**: Debe mostrar "ready" y estar esperando tareas

### Verificar Django
- Acceder a http://127.0.0.1:8000
- Debe mostrar la página principal sin errores

---

## 🛠️ Solución de Problemas

### Redis/Memurai no inicia
```bash
# Verificar si el puerto 6379 está libre
netstat -an | find "6379"

# Reiniciar servicio de Memurai
net stop memurai
net start memurai
```

### Error de Migraciones
```bash
# Aplicar migraciones pendientes
python manage.py makemigrations
python manage.py migrate

# Si hay problemas con administradores
python manage.py migrate administradores
```

### Error de Dependencias
```bash
# Reinstalar dependencias
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Puerto 8000 en uso
```bash
# Usar puerto alternativo
python manage.py runserver 127.0.0.1:8080

# O encontrar proceso que usa el puerto
netstat -ano | find "8000"
taskkill /PID [PID_NUMBER] /F
```

---

## 📊 Monitoreo en Producción

### Logs Importantes
- **Celery Beat**: Programación de tareas automáticas
- **Celery Worker**: Ejecución de scraping y notificaciones
- **Django**: Errores de aplicación web

### Archivos de Configuración Clave
- `settings.py`: Configuración principal
- `celery.py`: Configuración de Celery
- `requirements.txt`: Dependencias
- `start_all_services.bat`: Inicio automático

---

## ⚡ Consejos de Rendimiento

1. **Memoria RAM**: Mínimo 4GB recomendado
2. **Conexión a Internet**: Estable para scraping
3. **Espacio en Disco**: 1GB libre para logs y datos
4. **Antivirus**: Agregar excepción para la carpeta del proyecto

---

## 🔒 Seguridad

- Cambiar credenciales por defecto en producción
- Configurar firewall para puertos necesarios
- Mantener dependencias actualizadas
- Hacer backup regular de la base de datos

---

## 📞 Soporte

Para problemas técnicos:
1. Revisar logs de cada servicio
2. Verificar conectividad de Redis
3. Comprobar estado de base de datos
4. Validar configuración en `settings.py`
