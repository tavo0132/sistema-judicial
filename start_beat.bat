@echo off
echo ========================================
echo Iniciando Celery Beat (Programador)
echo ========================================

echo Activando entorno virtual...
call C:\Users\Gustavo\Documents\Dev\Lenguajes\Python\Fullstack\sistema-judicial-master\venv\Scripts\activate.bat

echo.
echo Iniciando Celery Beat...
echo (Presiona Ctrl+C para detener)
celery -A sistema_judicial beat --loglevel=info
