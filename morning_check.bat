@echo off
color 0A
echo ========================================
echo   🌅 SISTEMA JUDICIAL - CHECK MATUTINO
echo ========================================
echo.
echo Verificando estado del sistema antes de las ejecuciones programadas...
echo Fecha/Hora actual: %date% %time%
echo.

REM Verificar si es muy temprano
for /f "tokens=1-2 delims=:" %%a in ('time /t') do (
    set hora=%%a
    set minuto=%%b
)
echo ⏰ Hora actual del sistema: %time:~0,5%
echo.

echo ========================================
echo   PASO 1: VERIFICACIÓN DE SERVICIOS
echo ========================================

REM Verificar Redis/Memurai
echo [1/6] 🔍 Verificando Redis/Memurai...
tasklist /FI "IMAGENAME eq memurai.exe" 2>NUL | find /I /N "memurai.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ Redis/Memurai está corriendo
) else (
    echo ❌ Redis/Memurai NO está corriendo
    echo 🚨 ACCIÓN REQUERIDA: Iniciar Redis/Memurai antes de continuar
    echo.
    echo Opciones para iniciar Redis/Memurai:
    echo   1. Como servicio: net start memurai
    echo   2. Ejecutable: "C:\Program Files\Memurai\memurai.exe"
    echo   3. Redis tradicional: redis-server
    echo.
    pause
)

echo.

REM Verificar MySQL
echo [2/6] 🔍 Verificando MySQL...
tasklist /FI "IMAGENAME eq mysqld.exe" 2>NUL | find /I /N "mysqld.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ MySQL está corriendo
) else (
    echo ⚠️  MySQL no detectado como proceso independiente
    echo    (Puede estar corriendo como servicio - verificar manualmente)
)

echo.

REM Verificar entorno virtual
echo [3/6] 🔍 Verificando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    echo ✅ Entorno virtual encontrado
) else (
    echo ❌ Entorno virtual no encontrado
    echo 🚨 ERROR CRÍTICO: No se puede continuar sin entorno virtual
    pause
    exit /b 1
)

echo.

REM Verificar archivos críticos
echo [4/6] 🔍 Verificando archivos del sistema...
if exist "manage.py" (
    echo ✅ manage.py encontrado
) else (
    echo ❌ manage.py no encontrado
)

if exist "sistema_judicial\celery.py" (
    echo ✅ celery.py encontrado
) else (
    echo ❌ celery.py no encontrado
)

if exist "start_all_services.bat" (
    echo ✅ start_all_services.bat encontrado
) else (
    echo ❌ start_all_services.bat no encontrado
)

echo.

echo ========================================
echo   PASO 2: VERIFICACIÓN DE HORARIOS
echo ========================================

echo [5/6] 📅 Verificando horarios programados en base de datos...
echo.

REM Activar entorno y verificar horarios
call venv\Scripts\activate
python -c "
import os, django, sys
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_judicial.settings')
django.setup()

from administradores.models import ProgramacionMultiple
from django_celery_beat.models import PeriodicTask
from datetime import datetime, time

print('📋 HORARIOS CONFIGURADOS:')
print('-' * 40)
slots = ProgramacionMultiple.objects.all().order_by('slot')

horarios_activos = 0
for slot in slots:
    estado_emoji = '🟢' if slot.activo else '🔴'
    print(f'{estado_emoji} {slot.get_slot_display()}: {slot.hora.strftime(\"%%H:%%M\")} - {\"ACTIVO\" if slot.activo else \"INACTIVO\"}')
    if slot.activo:
        horarios_activos += 1

print(f'\n📊 RESUMEN:')
print(f'   Total de slots: {slots.count()}')
print(f'   Slots activos: {horarios_activos}')
print(f'   Slots inactivos: {slots.count() - horarios_activos}')

print(f'\n🕐 PRÓXIMAS EJECUCIONES:')
print('-' * 40)
ahora = datetime.now().time()
for slot in slots.filter(activo=True):
    if slot.hora > ahora:
        diff_seconds = (datetime.combine(datetime.today(), slot.hora) - datetime.combine(datetime.today(), ahora)).seconds
        diff_minutes = diff_seconds // 60
        print(f'⏳ {slot.get_slot_display()}: en {diff_minutes} minutos ({slot.hora.strftime(\"%%H:%%M\")})')
    else:
        print(f'⏭️  {slot.get_slot_display()}: ya pasó para hoy ({slot.hora.strftime(\"%%H:%%M\")})')

print(f'\n🔧 TAREAS EN CELERY BEAT:')
print('-' * 40)
tareas = PeriodicTask.objects.filter(name__startswith='consulta-procesos-slot')
for tarea in tareas:
    estado_emoji = '🟢' if tarea.enabled else '🔴'
    cron = tarea.crontab
    print(f'{estado_emoji} {tarea.name}: {cron.hour:02d}:{cron.minute:02d} - {\"ACTIVA\" if tarea.enabled else \"INACTIVA\"}')
" 2>nul

if %errorlevel% neq 0 (
    echo ❌ Error al conectar con la base de datos
    echo 🚨 Verificar que MySQL esté corriendo y la configuración sea correcta
)

echo.

echo ========================================
echo   PASO 3: VERIFICACIÓN DE SERVICIOS ACTIVOS
echo ========================================

echo [6/6] 🔍 Verificando servicios de Celery y Django...

tasklist /FI "WINDOWTITLE eq Celery Beat*" 2>nul | find "cmd.exe" >nul
if %errorlevel% == 0 (
    echo ✅ Celery Beat YA está corriendo
    set celery_beat_running=1
) else (
    echo ⚠️  Celery Beat no está corriendo
    set celery_beat_running=0
)

tasklist /FI "WINDOWTITLE eq Celery Worker*" 2>nul | find "cmd.exe" >nul
if %errorlevel% == 0 (
    echo ✅ Celery Worker YA está corriendo
    set celery_worker_running=1
) else (
    echo ⚠️  Celery Worker no está corriendo
    set celery_worker_running=0
)

tasklist /FI "WINDOWTITLE eq Django Server*" 2>nul | find "cmd.exe" >nul
if %errorlevel% == 0 (
    echo ✅ Django Server YA está corriendo
    set django_running=1
) else (
    echo ⚠️  Django Server no está corriendo
    set django_running=0
)

echo.

echo ========================================
echo   DECISIÓN AUTOMÁTICA
echo ========================================

if %celery_beat_running%==1 if %celery_worker_running%==1 if %django_running%==1 (
    echo 🎉 ¡PERFECTO! Todos los servicios ya están corriendo
    echo 💚 El sistema está listo para las ejecuciones programadas
    echo.
    echo 🌐 URLs disponibles:
    echo    - Dashboard: http://127.0.0.1:8000/administradores/dashboard/
    echo    - Aplicación: http://127.0.0.1:8000
    echo.
) else (
    echo 🚨 ALGUNOS SERVICIOS NO ESTÁN CORRIENDO
    echo.
    echo ¿Deseas iniciar todos los servicios automáticamente?
    echo [S] Sí, iniciar todos los servicios
    echo [N] No, voy a iniciarlos manualmente
    echo [V] Solo verificar estado sin iniciar
    echo.
    set /p decision="Elige una opción (S/N/V): "
    
    if /i "%decision%"=="S" (
        echo.
        echo 🚀 Iniciando todos los servicios...
        call start_all_services.bat
    ) else if /i "%decision%"=="N" (
        echo.
        echo 📝 Para iniciar manualmente, ejecuta:
        echo    start_all_services.bat
    ) else (
        echo.
        echo 📊 Verificación completada sin iniciar servicios
    )
)

echo.
echo ========================================
echo   CHECKLIST FINAL - MAÑANA 19/07/2025
echo ========================================
echo.
echo ✅ Cosas que verificar antes de las 07:00:
echo    1. Redis/Memurai corriendo
echo    2. MySQL corriendo  
echo    3. Ejecutar: start_all_services.bat
echo    4. Verificar dashboard en: http://127.0.0.1:8000/administradores/dashboard/
echo    5. Confirmar que los 3 slots estén ACTIVOS
echo.
echo 🎯 Horarios programados para hoy:
echo    - Horario 1: 07:00 AM
echo    - Horario 2: 07:15 AM  
echo    - Horario 3: 07:30 AM
echo.
echo 📧 Verificar correos después de cada ejecución
echo 📂 Logs en: scraping\resultados_scraping.json
echo.
echo Presiona cualquier tecla para finalizar...
pause > nul
