from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Cliente, Radicacion, LogAccesoCliente
from .utils import crear_notificacion

# Create your views here.

def cliente_login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo_electronico')
        contrasena = request.POST.get('contrasena')
        try:
            cliente = Cliente.objects.get(correo_electronico=correo)
            if cliente.check_password(contrasena):
                # Actualiza la última sesión
                cliente.ultima_sesion = timezone.now()
                cliente.save()

                # Registra el log de acceso
                LogAccesoCliente.objects.create(
                    cliente=cliente,
                    ip=request.META.get('REMOTE_ADDR')
                )

                request.session['cliente_id'] = cliente.id_cliente
                return redirect('cliente_dashboard')
            else:
                messages.error(request, 'Contraseña incorrecta')
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado')
    
    return render(request, 'clientes/login.html')

def registrar_cliente(request):
    if request.method == 'POST':
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        cedula = request.POST.get('cedula')
        correo = request.POST.get('correo_electronico')
        contrasena = request.POST.get('contrasena')
        numero_telefono = request.POST.get('numero_telefono')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        estado_cliente = request.POST.get('estado_cliente', 'Activo')
        
        try:
            cliente = Cliente.objects.create(
                nombres=nombres,
                apellidos=apellidos,
                cedula=cedula,
                correo_electronico=correo,
                numero_telefono=numero_telefono,
                direccion=direccion,
                ciudad=ciudad,
                estado_cliente=estado_cliente,
                fecha_registro=timezone.now()
            )
            cliente.set_password(contrasena)
            cliente.save()

            # Crear notificación para el administrador
            crear_notificacion(
                tipo='nuevo_cliente',
                titulo='Nuevo Cliente Registrado',
                mensaje=f'Se ha registrado un nuevo cliente: {nombres} {apellidos}',
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
        cliente = Cliente.objects.get(id_cliente=id_cliente)
        if request.method == 'POST':
            cliente.nombres = request.POST.get('nombres')
            cliente.apellidos = request.POST.get('apellidos')
            cliente.cedula = request.POST.get('cedula')
            cliente.correo_electronico = request.POST.get('correo_electronico')
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
        cliente = Cliente.objects.get(id_cliente=id_cliente)
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
            cliente = Cliente.objects.get(id_cliente=cliente_id)
            numero_radicado = request.POST['numero_radicacion']
            proceso_consultado = request.POST.get('proceso_consultado', 'No')
            
            # Verificar si ya existe una radicación con ese número
            radicaciones_existentes = Radicacion.objects.filter(numero_radicado=numero_radicado).exclude(cliente=cliente)
            
            # Crear la nueva radicación
            radicacion = Radicacion.objects.create(
                cliente=cliente,
                numero_radicado=numero_radicado,
                fecha_radicado=timezone.now(),
                proceso_consultado=proceso_consultado,
                estado_radicado='Abierto'
            )

            # Crear notificación para el cliente
            crear_notificacion(
                tipo='nueva_radicacion',
                titulo='Nueva Radicación Creada',
                mensaje=f'Se ha creado una nueva radicación con número {numero_radicado}',
                cliente=cliente,
                url_relacionada=f'/clientes/radicaciones/{cliente_id}/'
            )

            # Si hay radicaciones existentes y el usuario es admin, mostrar mensaje informativo
            if radicaciones_existentes.exists() and request.session.get('admin_id'):
                otros_clientes = [f"{r.cliente.nombres} {r.cliente.apellidos}" for r in radicaciones_existentes]
                mensaje = f"Nota: El número de radicado {numero_radicado} también está registrado por: {', '.join(otros_clientes)}"
                
                # Crear notificación para el administrador
                crear_notificacion(
                    tipo='radicacion_duplicada',
                    titulo='Radicación Duplicada Detectada',
                    mensaje=mensaje,
                    es_para_admin=True,
                    url_relacionada=f'/administradores/radicaciones/'
                )
                
                messages.warning(request, mensaje)
            else:
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
        cliente = Cliente.objects.get(id_cliente=cliente_id)
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
