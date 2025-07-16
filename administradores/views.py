from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Administrador, LogAccesoAdministrador, ConsultaProgramada
from .forms import AdminLoginForm
from clientes.models import Cliente, Radicacion
from django.db.models import Count
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
import subprocess
import sys

sys.path.append(r'C:\Users\Gustavo\Documents\Dev\Lenguajes\Python\Fullstack\sistema-judicial-master\scraping')
#from scraping.scraper_colombia import consultar_radicaciones

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo_electronico']
            contrasena = form.cleaned_data['contrasena']
            try:
                admin = Administrador.objects.get(correo_electronico=correo)
                if admin.check_password(contrasena):
                    # Actualiza la última sesión
                    admin.ultima_sesion = timezone.now()
                    admin.save()

                    # Registra el log de acceso
                    LogAccesoAdministrador.objects.create(
                        administrador=admin,
                        ip=request.META.get('REMOTE_ADDR')
                    )

                    request.session['admin_id'] = admin.id_administrador
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Contraseña incorrecta')
            except Administrador.DoesNotExist:
                messages.error(request, 'Administrador no encontrado')
    else:
        form = AdminLoginForm()
    
    return render(request, 'administradores/login.html', {'form': form})

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        admin_id = request.session.get('admin_id')
        if not admin_id:
            messages.error(request, 'Por favor inicie sesión como administrador')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_required
def admin_dashboard(request):
    if not request.session.get('admin_id'):
        return redirect('admin_login')
    
    # Obtener todos los clientes ordenados por fecha de registro
    clientes = Cliente.objects.all().order_by('-fecha_registro')
    
    # Obtener las últimas 10 radicaciones
    ultimas_radicaciones = Radicacion.objects.all().order_by('-fecha_radicacion')[:10]
    
    # Obtener la última consulta programada
    ultima_consulta = ConsultaProgramada.objects.last()
    
    context = {
        'clientes': clientes,
        'ultimas_radicaciones': ultimas_radicaciones,
        'ultima_consulta': ultima_consulta,
    }
    
    return render(request, 'administradores/dashboard.html', context)

def admin_logout(request):
    if 'admin_id' in request.session:
        del request.session['admin_id']
    return redirect('admin_login')

@staff_member_required
def iniciar_scraping(request):
    if request.method == "POST":
        try:
            # Ejecuta el script de scraping
            subprocess.run([
                sys.executable,
                r'C:\Users\Gustavo\Documents\Dev\Lenguajes\Python\Fullstack\sistema-judicial-master\scraping\scraper_colombia.py'
            ], check=True)

            # Ejecuta el script de guardado
            subprocess.run([
                sys.executable,
                r'C:\Users\Gustavo\Documents\Dev\Lenguajes\Python\Fullstack\sistema-judicial-master\saving\saving_data.py'
            ], check=True)

            messages.success(request, "Scraping y guardado finalizados correctamente.")
        except subprocess.CalledProcessError as e:
            messages.error(request, f"Ocurrió un error al ejecutar los scripts: {e}")
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')

def programar_consulta(request):
    if request.method == 'POST':
        hora = request.POST.get('hora_consulta')
        if hora:
            ConsultaProgramada.objects.create(hora=hora)
            messages.success(request, f'Consulta programada para las {hora}.')
        else:
            messages.error(request, 'Debe ingresar una hora válida.')
    return redirect('admin_dashboard')
