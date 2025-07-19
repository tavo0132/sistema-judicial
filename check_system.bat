@echo off
echo ========================================
echo   SISTEMA JUDICIAL - VERIFICACIÓN
echo ========================================
echo.

echo Verificando estado del sistema...
echo.

REM Verificar Python
echo [1/7] Verificando Python...
python --version >nul 2>&1
if %errorlevel% == 0 (
    python --version
    echo ✓ Python instalado correctamente
) else (
    echo ✗ Python no encontrado o no está en PATH
)

echo.

REM Verificar entorno virtual
echo [2/7] Verificando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    echo ✓ Entorno virtual encontrado en 'venv'
) else (
    echo ✗ Entorno virtual no encontrado
    echo   Crear con: python -m venv venv
)

echo.

REM Verificar Redis/Memurai
echo [3/7] Verificando Redis/Memurai...
tasklist /FI "IMAGENAME eq memurai.exe" 2>NUL | find /I /N "memurai.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✓ Memurai está corriendo
) else (
    echo ⚠ Memurai no está corriendo
)

echo.

REM Verificar archivos clave
echo [4/7] Verificando archivos del proyecto...
if exist "manage.py" (
    echo ✓ manage.py encontrado
) else (
    echo ✗ manage.py no encontrado
)

if exist "requirements.txt" (
    echo ✓ requirements.txt encontrado
) else (
    echo ✗ requirements.txt no encontrado
)

if exist "sistema_judicial\settings.py" (
    echo ✓ settings.py encontrado
) else (
    echo ✗ settings.py no encontrado
)

echo.

REM Verificar servicios corriendo
echo [5/7] Verificando servicios activos...

tasklist /FI "WINDOWTITLE eq Celery Beat*" 2>nul | find "cmd.exe" >nul
if %errorlevel% == 0 (
    echo ✓ Celery Beat está corriendo
) else (
    echo ⚠ Celery Beat no está corriendo
)

tasklist /FI "WINDOWTITLE eq Celery Worker*" 2>nul | find "cmd.exe" >nul
if %errorlevel% == 0 (
    echo ✓ Celery Worker está corriendo
) else (
    echo ⚠ Celery Worker no está corriendo
)

tasklist /FI "WINDOWTITLE eq Django Server*" 2>nul | find "cmd.exe" >nul
if %errorlevel% == 0 (
    echo ✓ Django Server está corriendo
) else (
    echo ⚠ Django Server no está corriendo
)

echo.

REM Verificar conectividad
echo [6/7] Verificando conectividad...
ping -n 1 127.0.0.1 >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Conectividad local OK
) else (
    echo ✗ Problema de conectividad local
)

echo.

REM Verificar puertos
echo [7/7] Verificando puertos...
netstat -an | find "6379" >nul
if %errorlevel% == 0 (
    echo ✓ Puerto 6379 (Redis) en uso
) else (
    echo ⚠ Puerto 6379 (Redis) libre
)

netstat -an | find "8000" >nul
if %errorlevel% == 0 (
    echo ✓ Puerto 8000 (Django) en uso
) else (
    echo ⚠ Puerto 8000 (Django) libre
)

echo.
echo ========================================
echo        VERIFICACIÓN COMPLETADA
echo ========================================
echo.
echo URLs para verificar manualmente:
echo - http://127.0.0.1:8000 (Aplicación)
echo - http://127.0.0.1:8000/admin (Admin)
echo - http://127.0.0.1:8000/administradores/dashboard/ (Dashboard)
echo.
echo Presiona cualquier tecla para continuar...
pause > nul
