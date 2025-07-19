@echo off
echo ========================================
echo   🎯 ACCESO DIRECTO AL DASHBOARD
echo ========================================
echo.

REM Verificar si Django está corriendo
echo Verificando si el servidor Django está activo...
timeout /t 2 /nobreak > nul

tasklist /FI "WINDOWTITLE eq *Django Server*" 2>nul | find "cmd.exe" >nul
if %errorlevel% == 0 (
    echo ✅ Django Server está corriendo
    echo.
    echo 🌐 Abriendo dashboard en el navegador...
    start http://127.0.0.1:8000/administradores/dashboard/
    echo.
    echo 📋 URLs disponibles:
    echo    - Dashboard Admin: http://127.0.0.1:8000/administradores/dashboard/
    echo    - Aplicación: http://127.0.0.1:8000
    echo    - Admin Django: http://127.0.0.1:8000/admin
) else (
    echo ❌ Django Server no está corriendo
    echo.
    echo ¿Deseas iniciarlo ahora?
    echo [S] Sí, iniciar todos los servicios
    echo [N] No, salir
    echo.
    set /p decision="Elige una opción (S/N): "
    
    if /i "%decision%"=="S" (
        echo.
        echo 🚀 Iniciando servicios...
        call start_all_services.bat
        timeout /t 10 /nobreak > nul
        echo.
        echo 🌐 Abriendo dashboard...
        start http://127.0.0.1:8000/administradores/dashboard/
    ) else (
        echo.
        echo ❌ Saliendo sin iniciar servicios
    )
)

echo.
echo Presiona cualquier tecla para cerrar...
timeout /t 5 /nobreak > nul
