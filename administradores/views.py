from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Administrador
from .forms import AdminLoginForm
from clientes.models import Cliente, Radicacion
from django.db.models import Count

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo_electronico']
            contrasena = form.cleaned_data['contrasena']
            try:
                admin = Administrador.objects.get(correo_electronico=correo)
                if admin.check_password(contrasena):
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
    ultimas_radicaciones = Radicacion.objects.all().order_by('-fecha_radicado')[:10]
    
    context = {
        'clientes': clientes,
        'ultimas_radicaciones': ultimas_radicaciones,
    }
    
    return render(request, 'administradores/dashboard.html', context)

def admin_logout(request):
    if 'admin_id' in request.session:
        del request.session['admin_id']
    return redirect('admin_login')
