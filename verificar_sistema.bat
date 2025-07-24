@echo off
echo ========================================
echo   VERIFICAR ESTADO DEL SISTEMA
echo ========================================
echo.

echo [1] Verificando Redis/Memurai...
tasklist /FI "IMAGENAME eq memurai.exe" 2>NUL | find /I /N "memurai.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✓ Redis/Memurai está corriendo
) else (
    echo ✗ Redis/Memurai NO está corriendo
    echo   → Ejecuta start_all_services.bat para iniciarlo
)

echo.
echo [2] Verificando procesos Python...
set PYTHON_COUNT=0
for /f %%i in ('tasklist /FI "IMAGENAME eq python.exe" ^| find /c "python.exe"') do set PYTHON_COUNT=%%i
echo Procesos Python corriendo: %PYTHON_COUNT%

echo.
echo [3] Verificando configuración de tareas programadas...
venv\Scripts\python.exe -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_judicial.settings')
django.setup()
from django_celery_beat.models import PeriodicTask
from administradores.models import ProgramacionMultiple

print('--- TAREAS EN CELERY BEAT ---')
tareas = PeriodicTask.objects.filter(enabled=True)
if tareas.exists():
    for t in tareas:
        print(f'✓ {t.name} - Última ejecución: {t.last_run_at}')
else:
    print('⚠ No hay tareas activas en Celery Beat')

print('\n--- HORARIOS PROGRAMADOS ---')
horarios = ProgramacionMultiple.objects.filter(activo=True)
if horarios.exists():
    for h in horarios:
        print(f'✓ Slot {h.slot} - {h.hora} - Activo: {h.activo}')
else:
    print('⚠ No hay horarios activos')
"

echo.
echo ========================================
echo   INSTRUCCIONES
echo ========================================
echo.
echo Si no hay tareas activas en Celery Beat:
echo   1. Ejecuta: start_all_services.bat
echo   2. Verifica que aparezcan 4 ventanas:
echo      - Redis/Memurai (verificación)
echo      - Celery Beat (programador)
echo      - Celery Worker (ejecutor)
echo      - Django Server (aplicación)
echo.
echo Si el problema persiste:
echo   1. Cierra todas las ventanas de servicios
echo   2. Ejecuta: stop_all_services.bat
echo   3. Espera 10 segundos
echo   4. Ejecuta: start_all_services.bat
echo.
pause
