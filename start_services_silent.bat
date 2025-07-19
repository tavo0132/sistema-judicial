@echo off
echo ========================================
echo   🚀 INICIO SILENCIOSO - SISTEMA JUDICIAL  
echo ========================================
echo.
echo Iniciando servicios en modo optimizado...
echo.

REM Verificar Redis/Memurai
tasklist /FI "IMAGENAME eq memurai.exe" 2>NUL | find /I /N "memurai.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ Redis/Memurai verificado
) else (
    echo ⚠️ Redis/Memurai no detectado - continuando...
)

REM Verificar entorno virtual
if exist "venv\Scripts\activate.bat" (
    echo ✅ Entorno virtual verificado
) else (
    echo ❌ Error: Entorno virtual no encontrado
    pause
    exit /b 1
)

echo.
echo 🔄 Iniciando servicios...

REM Iniciar Celery Beat
echo [1/3] Iniciando Celery Beat...
start /MIN "Celery Beat - Sistema Judicial" cmd /k "cd /d "%~dp0" && venv\Scripts\activate && echo Celery Beat iniciado... && python -m celery -A sistema_judicial beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"

REM Esperar un poco para que Beat se estabilice
timeout /t 3 /nobreak > nul

REM Iniciar Celery Worker  
echo [2/3] Iniciando Celery Worker...
start /MIN "Celery Worker - Sistema Judicial" cmd /k "cd /d "%~dp0" && venv\Scripts\activate && echo Celery Worker iniciado... && python -m celery -A sistema_judicial worker -l info"

REM Esperar un poco para que Worker se estabilice
timeout /t 3 /nobreak > nul

REM Iniciar Django Server
echo [3/3] Iniciando Django Server...
start /MIN "Django Server - Sistema Judicial" cmd /k "cd /d "%~dp0" && venv\Scripts\activate && echo Django Server iniciado en http://127.0.0.1:8000 && python manage.py runserver 127.0.0.1:8000"

REM Esperar para verificar que todo se inició
timeout /t 5 /nobreak > nul

echo.
echo ✅ Servicios iniciados en ventanas minimizadas
echo 📊 Verificando estado...

timeout /t 3 /nobreak > nul

REM Verificar que los servicios estén corriendo
set servicios_ok=0

tasklist /FI "WINDOWTITLE eq *Celery Beat*" 2>nul | find "cmd.exe" >nul
if %errorlevel% == 0 (
    echo ✅ Celery Beat: Corriendo
    set /a servicios_ok+=1
)

tasklist /FI "WINDOWTITLE eq *Celery Worker*" 2>nul | find "cmd.exe" >nul  
if %errorlevel% == 0 (
    echo ✅ Celery Worker: Corriendo
    set /a servicios_ok+=1
)

tasklist /FI "WINDOWTITLE eq *Django Server*" 2>nul | find "cmd.exe" >nul
if %errorlevel% == 0 (
    echo ✅ Django Server: Corriendo
    set /a servicios_ok+=1
)

echo.
if %servicios_ok% == 3 (
    echo 🎉 ¡TODOS LOS SERVICIOS INICIADOS CORRECTAMENTE!
    echo.
    echo 🌐 Sistema disponible en:
    echo    http://127.0.0.1:8000/administradores/dashboard/
    echo.
    echo 💡 Las ventanas están minimizadas para no molestar
    echo 💡 Puedes maximizarlas desde la barra de tareas si necesitas ver logs
) else (
    echo ⚠️ Algunos servicios pueden no haber iniciado correctamente
    echo 🔧 Revisa las ventanas minimizadas para más detalles
)

echo.
echo ========================================
echo        SISTEMA LISTO PARA OPERAR
echo ========================================
timeout /t 3 /nobreak > nul
