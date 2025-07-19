@echo off
echo ========================================
echo Iniciando Servidor Django
echo ========================================

echo Activando entorno virtual...
call C:\Users\Gustavo\Documents\Dev\Lenguajes\Python\Fullstack\sistema-judicial-master\venv\Scripts\activate.bat

echo.
echo Aplicando migraciones...
python manage.py migrate

echo.
echo Iniciando servidor Django...
echo (Presiona Ctrl+C para detener)
python manage.py runserver
