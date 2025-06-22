import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_judicial.settings')
django.setup()

from administradores.models import Administrador

def crear_admin():
    try:
        # Datos del administrador
        admin_data = {
            'nombres': 'Admin',
            'apellidos': 'Principal',
            'cedula': '123456789',
            'correo_electronico': 'admin@ejemplo.com',
            'numero_telefono': '1234567890'
        }

        # Crear el administrador
        admin = Administrador(**admin_data)
        admin.set_password('admin123')  # Establecer la contraseña
        admin.save()

        print('Administrador creado exitosamente')
        print(f'Correo: {admin_data["correo_electronico"]}')
        print('Contraseña: admin123')

    except Exception as e:
        print(f'Error al crear el administrador: {str(e)}')

if __name__ == '__main__':
    crear_admin() 