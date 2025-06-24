from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Cliente, Radicacion, LogAccesoCliente, Notificacion
from .utils import crear_notificacion

# Create your views here.

def cliente_login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo_electronico')
        contrasena = request.POST.get('contrasena')
        try:
            cliente = Cliente.objects.get(email=correo)  # Cambiado aquí
            if cliente.check_password(contrasena):
                # Actualiza la última sesión
                cliente.ultima_sesion = timezone.now()
                cliente.save()

                # Registra el log de acceso
                LogAccesoCliente.objects.create(
                    cliente=cliente,
                    ip=request.META.get('REMOTE_ADDR')
                )

                request.session['cliente_id'] = cliente.id  # Cambiado aquí
                return redirect('cliente_dashboard')
            else:
                messages.error(request, 'Contraseña incorrecta')
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado')
    
    return render(request, 'clientes/login.html')

def registrar_cliente(request):
    if request.method == 'POST':
        first_name = request.POST.get('nombres')
        last_name = request.POST.get('apellidos')
        cedula = request.POST.get('cedula')
        email = request.POST.get('correo_electronico')
        password = request.POST.get('contrasena')
        numero_telefono = request.POST.get('numero_telefono')
        direccion = request.POST.get('direccion')
        estado_cliente = request.POST.get('estado_cliente', 'Activo')
        pais = request.POST.get('pais', 'Colombia')
        
        try:
            cliente = Cliente.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                cedula=cedula,
                numero_telefono=numero_telefono,
                direccion=direccion,
                ciudad=ciudad,
                estado_cliente=estado_cliente,
                fecha_registro=timezone.now(),
                pais=pais  # <-- Nuevo campo
            )
            cliente.set_password(password)
            cliente.save()

            # Crear notificación para el administrador
            crear_notificacion(
                tipo='nuevo_cliente',
                titulo='Nuevo Cliente Registrado',
                mensaje=f'Se ha registrado un nuevo cliente: {first_name} {last_name}',
                es_para_admin=True,
                url_relacionada='/administradores/clientes/'
            )

            messages.success(request, 'Cliente registrado exitosamente')
            return redirect('cliente_login')
        except Exception as e:
            messages.error(request, f'Error al registrar cliente: {str(e)}')
    
    return render(request, 'clientes/registrar.html')

def editar_cliente(request, id_cliente):
    try:
        cliente = Cliente.objects.get(id=id_cliente)
        if request.method == 'POST':
            cliente.first_name = request.POST.get('nombres')
            cliente.last_name = request.POST.get('apellidos')
            cliente.cedula = request.POST.get('cedula')
            cliente.email = request.POST.get('correo_electronico')
            cliente.numero_telefono = request.POST.get('numero_telefono')
            cliente.direccion = request.POST.get('direccion')
            cliente.ciudad = request.POST.get('ciudad')
            cliente.estado_cliente = request.POST.get('estado_cliente')
            
            # Solo actualizar la contraseña si se proporciona una nueva
            nueva_contrasena = request.POST.get('contrasena')
            if nueva_contrasena:
                cliente.set_password(nueva_contrasena)
            
            cliente.save()

            # Crear notificación para el cliente
            crear_notificacion(
                tipo='actualizacion_cliente',
                titulo='Información Actualizada',
                mensaje='Tu información personal ha sido actualizada exitosamente.',
                cliente=cliente,
                url_relacionada=f'/clientes/dashboard/'
            )

            messages.success(request, 'Cliente actualizado exitosamente')
            return redirect('cliente_dashboard')
        
        return render(request, 'clientes/editar.html', {'cliente': cliente})
    except Cliente.DoesNotExist:
        messages.error(request, 'Cliente no encontrado')
        return redirect('cliente_login')

def ver_radicaciones_cliente(request, id_cliente):
    try:
        cliente = Cliente.objects.get(id=id_cliente)
        radicaciones = cliente.radicacion_set.all()
        return render(request, 'clientes/radicaciones.html', {
            'cliente': cliente,
            'radicaciones': radicaciones
        })
    except Cliente.DoesNotExist:
        messages.error(request, 'Cliente no encontrado')
        return redirect('admin_dashboard')

def crear_radicacion(request, cliente_id):
    if request.method == 'POST':
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            numero_radicado = request.POST.get('numero_radicado')
            proceso_consultado = request.POST.get('proceso_consultado')

            # Validar duplicado para este cliente
            if Radicacion.objects.filter(cliente=cliente, numero_radicado=numero_radicado).exists():
                messages.warning(request, 'Su proceso judicial ya ha sido registrado.')
                return redirect('ver_radicaciones_cliente', id_cliente=cliente_id)

            # Crear la radicación si no existe
            Radicacion.objects.create(
                cliente=cliente,
                numero_radicado=numero_radicado,
                proceso_consultado=proceso_consultado,
                # otros campos si aplica
            )
            messages.success(request, 'Radicación creada exitosamente.')
            return redirect('ver_radicaciones_cliente', id_cliente=cliente_id)

        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado.')
            return redirect('cliente_login')
        except Exception as e:
            messages.error(request, f'Error al crear la radicación: {str(e)}')
            return render(request, 'clientes/crear_radicacion.html')

    return render(request, 'clientes/crear_radicacion.html')

def cliente_dashboard(request):
    if 'cliente_id' not in request.session:
        messages.error(request, 'Por favor inicie sesión para acceder al dashboard')
        return redirect('cliente_login')
    
    cliente_id = request.session['cliente_id']
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        radicaciones = Radicacion.objects.filter(cliente=cliente).order_by('-fecha_radicado')
        notificaciones = Notificacion.objects.filter(
            cliente=cliente,
            es_para_admin=False
        ).order_by('-fecha_creacion')[:5]  # Últimas 5 notificaciones
        
        context = {
            'cliente': cliente,
            'radicaciones': radicaciones,
            'notificaciones': notificaciones
        }
        return render(request, 'clientes/dashboard.html', context)
    except Cliente.DoesNotExist:
        messages.error(request, 'Cliente no encontrado')
        return redirect('cliente_login')

@login_required
def eliminar_radicacion(request, radicacion_id):
    radicacion = get_object_or_404(Radicacion, id=radicacion_id)
    cliente_id = radicacion.cliente.id
    radicacion.delete()
    messages.success(request, 'Radicación eliminada correctamente.')
    # Redirige según el usuario
    if request.user.is_staff:
        return redirect('admin_dashboard')
    else:
        return redirect('ver_radicaciones_cliente', id_cliente=cliente_id)
