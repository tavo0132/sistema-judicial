@echo off
echo ========================================
echo    SISTEMA JUDICIAL - INICIO COMPLETO
echo ========================================
echo.
echo Iniciando todos los servicios necesarios...
echo.

REM Verificar si Redis/Memurai está corriendo
echo [1/5] Verificando Redis/Memurai...
tasklist /FI "IMAGENAME eq memurai.exe" 2>NUL | find /I /N "memurai.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✓ Redis/Memurai ya está corriendo
) else (
    echo ⚠ Redis/Memurai no está corriendo
    echo   Por favor, inicia Redis/Memurai manualmente
    echo   Ubicación típica: C:\Program Files\Memurai\memurai.exe
    pause
)

echo.
echo [2/5] Verificando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    echo ✓ Entorno virtual encontrado
) else (
    echo ✗ Error: No se encontró el entorno virtual en 'venv'
    echo   Asegúrate de que el entorno virtual esté creado
    pause
    exit /b 1
)

echo.
echo [3/5] Iniciando Celery Beat (Programador)...
start "Celery Beat" cmd /k "cd /d "%~dp0" && venv\Scripts\activate && python -m celery -A sistema_judicial beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"

echo.
echo [4/5] Iniciando Celery Worker...
timeout /t 3 /nobreak > nul
start "Celery Worker" cmd /k "cd /d "%~dp0" && venv\Scripts\activate && python -m celery -A sistema_judicial worker -l info"

echo.
echo [5/5] Iniciando Servidor Django...
timeout /t 5 /nobreak > nul
start "Django Server" cmd /k "cd /d "%~dp0" && venv\Scripts\activate && python manage.py runserver 127.0.0.1:8000"

echo.
echo ========================================
echo    ✓ TODOS LOS SERVICIOS INICIADOS
echo ========================================
echo.
echo Los siguientes servicios están corriendo:
echo - Redis/Memurai (verificar manualmente)
echo - Celery Beat (Programador de tareas)
echo - Celery Worker (Ejecutor de tareas)
echo - Django Server (Aplicación web)
echo.
echo URLs de acceso:
echo - Aplicación: http://127.0.0.1:8000
echo - Admin Django: http://127.0.0.1:8000/admin
echo - Dashboard Admin: http://127.0.0.1:8000/administradores/dashboard/
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause > nul
