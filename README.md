# 🏛️ Sistema Judicial - Automatización de Consultas

Sistema automatizado para consulta y monitoreo de procesos judiciales con notificaciones por correo electrónico.

## 🌟 Características Principales

- **Scraping Automatizado** de procesos judiciales
- **Programación Múltiple** (3 horarios independientes)
- **Notificaciones por Email** automáticas
- **Dashboard Administrativo** profesional
- **Autenticación Multi-rol** (Admin/Cliente)
- **Integración con Celery** para tareas asíncronas

## 🚀 Inicio Rápido

### Opción 1: Automático (Recomendado)
```bash
# Iniciar todos los servicios
start_all_services.bat

# Detener todos los servicios
stop_all_services.bat
```

### Opción 2: Manual
Ver `GUIA_DESPLIEGUE.md` para instrucciones detalladas.

## 📁 Estructura del Proyecto

```
sistema-judicial/
├── administradores/          # App de administración
│   ├── models.py            # Modelos (Admin, ProgramacionMultiple)
│   ├── views.py             # Vistas del dashboard
│   └── templates/           # Templates del dashboard
├── clientes/                # App de clientes
│   ├── models.py            # Modelo Cliente y Radicaciones
│   └── views.py             # Autenticación y vistas
├── scraping/                # Motor de scraping
│   ├── scraper_colombia.py  # Scraper principal
│   ├── tasks.py             # Tareas de Celery
│   └── resultados_scraping.json
├── notifications/           # Sistema de notificaciones
│   ├── email_sender.py      # Envío de correos
│   └── notifications_colombia.py
├── sistema_judicial/        # Configuración Django
│   ├── settings.py          # Configuración principal
│   ├── celery.py            # Configuración Celery
│   └── urls.py              # URLs principales
├── start_all_services.bat   # 🆕 Inicio automático
├── stop_all_services.bat    # 🆕 Detención automática
└── GUIA_DESPLIEGUE.md      # 🆕 Guía completa
```

## 🛠️ Tecnologías

- **Backend**: Django 5.2.3
- **Tareas Asíncronas**: Celery 5.5.3
- **Broker**: Redis/Memurai
- **Base de Datos**: MySQL
- **Scraping**: Selenium WebDriver
- **Frontend**: Bootstrap + HTML/CSS

## 📋 Requisitos

- Python 3.8+
- Redis/Memurai
- MySQL
- Google Chrome/Chromium
- Windows (archivos .bat incluidos)

## ⚙️ Configuración Inicial

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar base de datos**:
   ```bash
   python manage.py migrate
   ```

3. **Crear superusuario**:
   ```bash
   python manage.py createsuperuser
   ```

4. **Iniciar servicios**:
   ```bash
   start_all_services.bat
   ```

## 🎯 Funcionalidades

### Dashboard Administrativo
- **3 Slots de Programación** independientes
- **Activación/Desactivación** individual
- **Monitoreo en tiempo real** del estado
- **Interfaz profesional** con Bootstrap

### Sistema de Scraping
- **Scraping automático** de portales judiciales
- **Extracción de datos** de procesos
- **Detección de actualizaciones**
- **Persistencia en JSON**

### Notificaciones
- **Emails automáticos** con actualizaciones
- **Plantillas personalizables**
- **Integración con Gmail SMTP**

## 🔧 URLs Principales

- **Aplicación**: http://127.0.0.1:8000
- **Dashboard Admin**: http://127.0.0.1:8000/administradores/dashboard/
- **Admin Django**: http://127.0.0.1:8000/admin
- **Login Cliente**: http://127.0.0.1:8000/clientes/login/

## 📊 Monitoreo

### Logs de Celery
- **Beat**: Programación de tareas
- **Worker**: Ejecución de scraping

### Archivos de Datos
- **Resultados**: `scraping/resultados_scraping.json`
- **Logs**: `scraping/logs_scraper_colombia/`

## 🚨 Solución de Problemas

Ver `GUIA_DESPLIEGUE.md` sección "Solución de Problemas" para:
- Errores de Redis/Memurai
- Problemas de migraciones
- Conflictos de puertos
- Errores de dependencias

## 📈 Rendimiento

- **Scraping**: ~10-15 segundos por ejecución
- **Notificaciones**: Instantáneas
- **Concurrencia**: 16 workers simultáneos
- **Escalabilidad**: Configurable via `settings.py`

## 🔒 Seguridad

- **Autenticación**: Hash de contraseñas con Django
- **Roles**: Separación Admin/Cliente
- **Validación**: Formularios con CSRF protection
- **Logs**: Registro de accesos administrativos

## 🎨 Interfaz

- **Responsive Design** con Bootstrap
- **Estados visuales** (Activo/Inactivo)
- **Feedback en tiempo real**
- **Diseño profesional**

## 🔄 Workflow de Ejecución

1. **Programación**: Admin configura horarios en dashboard
2. **Celery Beat**: Programa tareas según configuración
3. **Celery Worker**: Ejecuta scraping automático
4. **Scraping**: Extrae datos de portales judiciales
5. **Notificación**: Envía emails con actualizaciones
6. **Persistencia**: Guarda resultados en JSON

## 📞 Soporte

Para soporte técnico consultar:
- `GUIA_DESPLIEGUE.md` - Guía completa
- Logs de Celery - Diagnóstico en tiempo real
- Django Admin - Gestión de base de datos

---

**Desarrollado con ❤️ para automatizar consultas judiciales**
