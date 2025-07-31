from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.utils import IntegrityError
from .models import Cliente, Radicacion, LogAccesoCliente, Notificacion
from .utils import crear_notificacion
from django.urls import path
from django.http import HttpResponseRedirect
from django.urls import reverse

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
        ciudad = request.POST.get('ciudad')
        estado_cliente = request.POST.get('estado_cliente', 'Activo')
        pais = request.POST.get('pais', 'Colombia')
        
        try:
            cliente = Cliente.objects.create(
                username=f"cliente_{cedula}",  # Username único basado en cédula
                first_name=first_name,
                last_name=last_name,
                email=email,
                cedula=cedula,
                numero_telefono=numero_telefono,
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
        except IntegrityError as e:
            error_msg = str(e)
            if 'email' in error_msg:
                messages.error(request, 'Ya existe un cliente registrado con este correo electrónico.')
            elif 'cedula' in error_msg:
                messages.error(request, 'Ya existe un cliente registrado con esta cédula.')
            else:
                messages.error(request, 'Error: datos duplicados. Verifique el correo y la cédula.')
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

def ver_radicaciones_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    radicaciones = Radicacion.objects.filter(cliente=cliente, is_deleted=False).order_by('-fecha_creacion')
    return render(request, 'clientes/radicaciones.html', {
        'cliente': cliente,
        'radicaciones': radicaciones
    })

def crear_radicacion(request, cliente_id):
    if request.method == 'POST':
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            numero_radicado = request.POST.get('numero_radicado')
            proceso_consultado = request.POST.get('proceso_consultado')

            if not numero_radicado:
                messages.error(request, 'Debe ingresar el número de radicado.')
                return render(request, 'clientes/crear_radicacion.html', {'cliente': cliente})

            # Solo validar duplicado específico para este cliente
            # (eliminamos la validación global para que diferentes clientes puedan tener el mismo número)
            if Radicacion.objects.filter(cliente=cliente, numero_radicado=numero_radicado, is_deleted=False).exists():
                messages.warning(request, 'Ya tiene registrado este número de radicado.')
                return render(request, 'clientes/crear_radicacion.html', {'cliente': cliente})

            # Crear la radicación
            Radicacion.objects.create(
                cliente=cliente,
                numero_radicado=numero_radicado,
                proceso_consultado=proceso_consultado,
                fecha_radicacion=timezone.now().date(),
                estado_radicado='Abierto',
            )
            messages.success(request, '¡Radicación creada con éxito!')
            return redirect('ver_radicaciones_cliente', cliente_id=cliente_id)

        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado.')
            return redirect('cliente_login')
        except IntegrityError as e:
            # Esta excepción solo se activará si el mismo cliente intenta registrar el mismo número dos veces
            messages.warning(request, 'Ya tiene registrado este número de radicado.')
            return render(request, 'clientes/crear_radicacion.html', {'cliente': cliente})
        except Exception as e:
            messages.error(request, f'Error al crear la radicación: {str(e)}')
            return render(request, 'clientes/crear_radicacion.html', {'cliente': cliente})

    # Para GET request, obtener el cliente y pasarlo al template
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        return render(request, 'clientes/crear_radicacion.html', {'cliente': cliente})
    except Cliente.DoesNotExist:
        messages.error(request, 'Cliente no encontrado.')
        return redirect('cliente_login')

def cliente_dashboard(request):
    if 'cliente_id' not in request.session:
        messages.error(request, 'Por favor inicie sesión para acceder al dashboard')
        return redirect('cliente_login')
    
    cliente_id = request.session['cliente_id']
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        radicaciones = Radicacion.objects.filter(cliente=cliente, is_deleted=False).order_by('-fecha_radicacion')
        radicaciones_borradas = Radicacion.objects.filter(cliente=cliente, is_deleted=True).order_by('-fecha_radicacion')  # <-- AGREGADO
        notificaciones = Notificacion.objects.filter(
            cliente=cliente,
            es_para_admin=False
        ).order_by('-fecha_creacion')[:5]
        
        context = {
            'cliente': cliente,
            'radicaciones': radicaciones,
            'radicaciones_borradas': radicaciones_borradas,  # <-- AGREGADO
            'notificaciones': notificaciones
        }
        return render(request, 'clientes/dashboard.html', context)
    except Cliente.DoesNotExist:
        messages.error(request, 'Cliente no encontrado')
        return redirect('cliente_login')

def dashboard_cliente(request):
    cliente = request.user
    radicaciones = Radicacion.objects.filter(cliente=cliente)
    return render(request, 'clientes/dashboard.html', {'radicaciones': radicaciones})

@login_required
def eliminar_radicacion(request, radicacion_id):
    radicacion = get_object_or_404(Radicacion, id=radicacion_id)
    radicacion.is_deleted = True  # Marcar como borrada
    radicacion.save()
    messages.success(request, 'Radicación marcada como borrada correctamente.')
    return redirect('cliente_dashboard')  # <--- SIEMPRE redirige al dashboard de clientes

def ver_radicacion_detalle(request, radicacion_id):
    radicacion = get_object_or_404(Radicacion, id=radicacion_id)
    return render(request, 'clientes/radicacion_detalle.html', {'radicacion': radicacion})

@login_required
def restaurar_radicacion(request, radicacion_id):
    radicacion = get_object_or_404(Radicacion, id=radicacion_id, is_deleted=True)
    radicacion.is_deleted = False
    radicacion.save()
    messages.success(request, 'Radicación restaurada correctamente.')
    return redirect('cliente_dashboard')

@login_required
def cambiar_estado_radicacion(request, radicacion_id):
    radicacion = get_object_or_404(Radicacion, id=radicacion_id)
    if radicacion.estado_radicado == 'Abierto':
        radicacion.estado_radicado = 'Cerrado'
    else:
        radicacion.estado_radicado = 'Abierto'
    radicacion.save()
    messages.success(request, f'El estado de la radicación cambió a {radicacion.estado_radicado}.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('cliente_dashboard')))

def cerrar_radicado(request, radicacion_id):
    radicacion = get_object_or_404(Radicacion, id=radicacion_id)
    if request.method == "POST":
        radicacion.estado_radicado = "Cerrado"
        radicacion.save()
        messages.success(request, "Radicación cerrada correctamente.")
    return redirect('dashboard_cliente')

def abrir_radicado(request, radicacion_id):
    radicacion = get_object_or_404(Radicacion, id=radicacion_id)
    if request.method == "POST":
        radicacion.estado_radicado = "Abierto"
        radicacion.save()
        messages.success(request, "Radicación abierta correctamente.")
    return redirect('dashboard_cliente')

urlpatterns = [
    # ... otras rutas ...
    path('radicaciones/<int:cliente_id>/', ver_radicaciones_cliente, name='ver_radicaciones_cliente'),
]
