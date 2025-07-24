from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.utils import IntegrityError
from django.db.models import Q
from .models import Cliente, Radicacion, LogAccesoCliente, Notificacion
from .utils import crear_notificacion

# Create your views here.

def cliente_login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo_electronico')
        contrasena = request.POST.get('contrasena')
        try:
            # Solo permitir login a clientes NO eliminados
            cliente = Cliente.objects.get(email=correo, is_deleted=False)
            if cliente.estado_cliente == 'Inactivo':
                messages.error(request, 'Su usuario se encuentra Inactivo, para mayor información por favor ponerse en contacto con el Administrador del sistema')
            elif cliente.check_password(contrasena):
                # Actualiza la última sesión
                cliente.ultima_sesion = timezone.now()
                cliente.save()

                # Registra el log de acceso
                LogAccesoCliente.objects.create(
                    cliente=cliente,
                    ip=request.META.get('REMOTE_ADDR')
                )

                request.session['cliente_id'] = cliente.id
                return redirect('cliente_dashboard')
            else:
                messages.error(request, 'Contraseña incorrecta')
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado')
    
    return render(request, 'clientes/login.html')

def registrar_cliente(request):
    restaurar_cliente_id = request.POST.get('restaurar_cliente_id')
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

        # Si se está confirmando restauración
        if restaurar_cliente_id:
            cliente = Cliente.objects.get(id=restaurar_cliente_id)
            cliente.is_deleted = False
            cliente.deleted_at = None
            cliente.deleted_by_id = None
            cliente.first_name = first_name
            cliente.last_name = last_name
            cliente.cedula = cedula
            cliente.email = email
            cliente.numero_telefono = numero_telefono
            cliente.ciudad = ciudad
            cliente.estado_cliente = estado_cliente
            cliente.pais = pais
            cliente.fecha_registro = timezone.now()
            cliente.set_password(password)
            cliente.save()

            crear_notificacion(
                tipo='nuevo_cliente',
                titulo='Cliente restaurado',
                mensaje=f'Se ha restaurado y actualizado el cliente: {first_name} {last_name}',
                es_para_admin=True,
                url_relacionada='/administradores/clientes/'
            )
            messages.success(request, 'Cliente restaurado y actualizado exitosamente')
            return redirect('cliente_login')

        # Buscar si existe cliente eliminado con mismo correo/cédula
        cliente_eliminado = Cliente.objects.filter(
            (Q(email=email) | Q(cedula=cedula)),
            is_deleted=True
        ).first()
        if cliente_eliminado:
            # Mostrar opción de restaurar en la plantilla
            context = {
                'restaurar_cliente': cliente_eliminado,
                'datos_nuevos': {
                    'nombres': first_name,
                    'apellidos': last_name,
                    'cedula': cedula,
                    'correo_electronico': email,
                    'contrasena': password,
                    'numero_telefono': numero_telefono,
                    'ciudad': ciudad,
                    'estado_cliente': estado_cliente,
                    'pais': pais
                }
            }
            messages.warning(request, 'Ya existe un cliente eliminado con estos datos. ¿Desea restaurarlo y reemplazar la información?')
            return render(request, 'clientes/registrar.html', context)

        try:
            cliente = Cliente.objects.create(
                username=f"cliente_{cedula}",
                first_name=first_name,
                last_name=last_name,
                email=email,
                cedula=cedula,
                numero_telefono=numero_telefono,
                ciudad=ciudad,
                estado_cliente=estado_cliente,
                fecha_registro=timezone.now(),
                pais=pais
            )
            cliente.set_password(password)
            cliente.save()

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

            if not numero_radicado:
                messages.error(request, 'Debe ingresar el número de radicado.')
                return render(request, 'clientes/crear_radicacion.html', {'cliente': cliente})

            # Solo validar duplicado específico para este cliente
            # (eliminamos la validación global para que diferentes clientes puedan tener el mismo número)
            if Radicacion.objects.filter(cliente=cliente, numero_radicado=numero_radicado).exists():
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
            return redirect('ver_radicaciones_cliente', id_cliente=cliente_id)

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
        radicaciones = Radicacion.objects.filter(cliente=cliente).order_by('-fecha_radicacion')  # <--- CAMBIO AQUÍ
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

def dashboard_cliente(request):
    if request.user.is_authenticated:
        try:
            cliente = Cliente.objects.get(user=request.user)
            radicaciones = Radicacion.objects.filter(cliente=cliente).order_by('-fecha_creacion')
            return render(request, 'clientes/dashboard.html', {
                'cliente': cliente,
                'radicaciones': radicaciones
            })
        except Cliente.DoesNotExist:
            return redirect('clientes:registro')
    return redirect('clientes:login')

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
