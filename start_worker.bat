@echo off
echo ========================================
echo Iniciando Worker de Celery
echo ========================================

echo Activando entorno virtual...
call C:\Users\Gustavo\Documents\Dev\Lenguajes\Python\Fullstack\sistema-judicial-master\venv\Scripts\activate.bat

echo.
echo Iniciando worker de Celery...
echo (Presiona Ctrl+C para detener)
celery -A sistema_judicial worker --loglevel=info --pool=solo
