# 🌅 Scripts de Gestión Matutina - Sistema Judicial

## 📁 Scripts Disponibles

### 1. `morning_check.bat` ⭐ **PRINCIPAL**
**Propósito**: Verificación completa del sistema antes de las ejecuciones programadas

**Funciones**:
- ✅ Verifica servicios (Redis, MySQL, entorno virtual)
- 📅 Muestra horarios programados desde base de datos
- ⏰ Calcula tiempo restante hasta próximas ejecuciones
- 🚀 Opción de inicio automático de servicios
- 📊 Reporte completo del estado del sistema

**Uso recomendado**: 
```bash
# Ejecutar CADA MAÑANA antes de las 07:00
morning_check.bat
```

---

### 2. `start_services_silent.bat`
**Propósito**: Inicio optimizado y silencioso de todos los servicios

**Funciones**:
- 🔇 Inicia servicios en ventanas minimizadas
- ⚡ Inicio más rápido y eficiente
- ✅ Verificación automática de éxito
- 💡 Menos intrusivo visualmente

**Uso**:
```bash
# Para inicio silencioso
start_services_silent.bat
```

---

### 3. `open_dashboard.bat`
**Propósito**: Acceso directo al dashboard administrativo

**Funciones**:
- 🌐 Abre automáticamente el dashboard en navegador
- 🔍 Verifica si Django está corriendo
- 🚀 Opción de iniciar servicios si no están activos
- ⚡ Acceso rápido para administración

**Uso**:
```bash
# Acceso directo al dashboard
open_dashboard.bat
```

---

## 🕐 Workflow Matutino Recomendado

### **06:50 AM - Preparación**
```bash
# 1. Ejecutar verificación completa
morning_check.bat
```

### **Según resultado del morning_check:**

#### ✅ **Si todo está bien**:
- El sistema mostrará "¡PERFECTO! Todos los servicios ya están corriendo"
- Acceder al dashboard: `open_dashboard.bat`
- Verificar que los 3 slots estén ACTIVOS

#### ⚠️ **Si faltan servicios**:
- El script preguntará si quieres iniciar servicios
- Elegir **[S]** para inicio automático
- Esperar confirmación de éxito

#### ❌ **Si hay problemas**:
- Seguir las instrucciones mostradas en pantalla
- Verificar Redis/Memurai manualmente
- Ejecutar `start_all_services.bat` como respaldo

---

## 📊 Lo que Verás en `morning_check.bat`

### **Sección 1: Verificación de Servicios**
```
✅ Redis/Memurai está corriendo
✅ MySQL está corriendo
✅ Entorno virtual encontrado
✅ Archivos del sistema encontrados
```

### **Sección 2: Horarios Programados**
```
📋 HORARIOS CONFIGURADOS:
🟢 Horario 1: 07:00 - ACTIVO
🟢 Horario 2: 07:15 - ACTIVO
🟢 Horario 3: 07:30 - ACTIVO

🕐 PRÓXIMAS EJECUCIONES:
⏳ Horario 1: en 8 minutos (07:00)
⏳ Horario 2: en 23 minutos (07:15)
⏳ Horario 3: en 38 minutos (07:30)
```

### **Sección 3: Estado de Servicios**
```
✅ Celery Beat YA está corriendo
✅ Celery Worker YA está corriendo
✅ Django Server YA está corriendo
```

---

## 🚨 Solución de Problemas Comunes

### **Redis/Memurai no está corriendo**
```bash
# Opciones para iniciar:
net start memurai                           # Como servicio
"C:\Program Files\Memurai\memurai.exe"     # Ejecutable directo
redis-server                               # Redis tradicional
```

### **Error de base de datos**
```bash
# Verificar estado de MySQL
net start mysql80  # o el nombre de tu servicio MySQL
```

### **Servicios no se inician**
```bash
# Usar inicio manual paso a paso
start_beat.bat      # Celery Beat
start_worker.bat    # Celery Worker  
start_django.bat    # Django Server
```

---

## 🎯 Horarios de Ejecución Programados

| Slot | Horario | Estado | Tarea Celery |
|------|---------|--------|--------------|
| Horario 1 | 07:00 AM | 🟢 Activo | consulta-procesos-slot1 |
| Horario 2 | 07:15 AM | 🟢 Activo | consulta-procesos-slot2 |
| Horario 3 | 07:30 AM | 🟢 Activo | consulta-procesos-slot3 |

---

## 📧 Verificación Post-Ejecución

Después de cada horario programado:

1. **Verificar correos electrónicos** (diana4401@gmail.com)
2. **Revisar archivo de resultados**: `scraping\resultados_scraping.json`
3. **Monitorear logs** en las ventanas de Celery Worker
4. **Confirmar en dashboard** que las ejecuciones fueron exitosas

---

## 💡 Consejos Importantes

- **⏰ Timing**: Ejecutar `morning_check.bat` 10-15 minutos antes del primer horario
- **🔄 Persistencia**: Los horarios están guardados en MySQL (permanentes)
- **👀 Monitoreo**: Mantener ventanas de Celery visibles durante ejecuciones
- **📱 Notificaciones**: Confirmar recepción de emails como validación

---

## 🆘 Contacto de Emergencia

Si hay problemas durante la madrugada:

1. **Verificar**: `check_system.bat`
2. **Reiniciar**: `stop_all_services.bat` → `start_all_services.bat`
3. **Acceso directo**: `open_dashboard.bat`
4. **Logs**: Revisar ventanas de Celery para errores específicos
