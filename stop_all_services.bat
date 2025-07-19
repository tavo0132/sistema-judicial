@echo off
echo ========================================
echo   SISTEMA JUDICIAL - DETENER SERVICIOS
echo ========================================
echo.

echo Deteniendo servicios del Sistema Judicial...
echo.

REM Detener procesos de Celery
echo [1/3] Deteniendo Celery Worker y Beat...
taskkill /F /FI "WINDOWTITLE eq Celery Worker*" 2>nul
taskkill /F /FI "WINDOWTITLE eq Celery Beat*" 2>nul
taskkill /F /IM python.exe /FI "COMMANDLINE eq *celery*" 2>nul

REM Detener servidor Django
echo [2/3] Deteniendo Servidor Django...
taskkill /F /FI "WINDOWTITLE eq Django Server*" 2>nul
taskkill /F /IM python.exe /FI "COMMANDLINE eq *runserver*" 2>nul

REM Limpiar procesos Python residuales relacionados con el proyecto
echo [3/3] Limpiando procesos residuales...
taskkill /F /IM python.exe /FI "COMMANDLINE eq *sistema_judicial*" 2>nul

echo.
echo ========================================
echo    ✓ SERVICIOS DETENIDOS
echo ========================================
echo.
echo Nota: Redis/Memurai no se detiene automáticamente
echo Si necesitas detenerlo, hazlo manualmente desde:
echo - Servicios de Windows, o
echo - Administrador de tareas
echo.
echo Presiona cualquier tecla para cerrar...
pause > nul
