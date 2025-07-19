@echo off
echo ========================================
echo Script de inicio del Sistema Judicial
echo ========================================

echo.
echo 1. Verificando entorno virtual...
call C:\Users\Gustavo\Documents\Dev\Lenguajes\Python\Fullstack\sistema-judicial-master\venv\Scripts\activate.bat

echo.
echo 2. Verificando configuracion de Django...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_judicial.settings'); import django; django.setup(); print('Django OK')"

echo.
echo 3. Verificando configuracion de Celery...
python -c "from sistema_judicial.celery import app; print('Celery OK')"

echo.
echo 4. Verificando conexion a Redis...
python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=0); print('Redis:', r.ping())"

echo.
echo ========================================
echo Configuracion verificada
echo ========================================
pause
