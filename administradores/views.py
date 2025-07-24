# Vista para restaurar cliente eliminado (undo soft delete)
from django.utils import timezone
def restaurar_cliente(request, cliente_id):
    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, id=cliente_id)
        cliente.is_deleted = False
        cliente.deleted_at = None
        cliente.estado_cliente = 'Activo'
        cliente.save()
        messages.success(request, "El cliente ha sido restaurado correctamente.")
    return redirect('admin_dashboard')
# Vista para eliminar cliente (soft delete)
from django.utils import timezone
def eliminar_cliente(request, cliente_id):
    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, id=cliente_id)
        cliente.is_deleted = True
        cliente.deleted_at = timezone.now()
        cliente.estado_cliente = 'Inactivo'
        cliente.save()
        messages.success(request, "El cliente ha sido eliminado correctamente. Puedes restaurarlo si lo necesitas.")
    return redirect('admin_dashboard')
from django.shortcuts import get_object_or_404
# Vista para cambiar el estado del cliente (toggle Activo/Inactivo)
def cambiar_estado_cliente(request, cliente_id):
    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, id=cliente_id)
        nuevo_estado = 'Inactivo' if cliente.estado_cliente == 'Activo' else 'Activo'
        cliente.estado_cliente = nuevo_estado
        cliente.save()
        messages.success(request, f"El estado del cliente ha sido cambiado a {nuevo_estado}.")
    return redirect('admin_dashboard')
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Administrador, LogAccesoAdministrador, ConsultaProgramada, ProgramacionMultiple
from .forms import AdminLoginForm
from clientes.models import Cliente, Radicacion
from django.db.models import Count
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
import subprocess
import sys
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

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
    clientes = Cliente.objects.filter(is_deleted=False).order_by('-fecha_registro')
    clientes_eliminados = Cliente.objects.filter(is_deleted=True).order_by('-deleted_at')
    
    # Obtener las últimas 10 radicaciones
    ultimas_radicaciones = Radicacion.objects.all().order_by('-fecha_radicacion')[:10]
    
    # Obtener la última consulta programada local (para compatibilidad)
    ultima_consulta = ConsultaProgramada.objects.last()
    
    # Obtener o crear las 3 programaciones múltiples con valores por defecto
    slots_data = []
    default_hours = ['07:00', '14:00', '20:00']
    
    try:
        for i, (slot_key, slot_name) in enumerate(ProgramacionMultiple.SLOTS):
            try:
                programacion, created = ProgramacionMultiple.objects.get_or_create(
                    slot=slot_key,
                    defaults={
                        'hora': default_hours[i],
                        'activo': False
                    }
                )
                
                # Verificar si hay una tarea activa en Celery Beat para este slot
                tarea_celery_activa = False
                try:
                    tarea_celery = PeriodicTask.objects.get(
                        name=programacion.get_task_name(), 
                        enabled=True
                    )
                    tarea_celery_activa = True
                except PeriodicTask.DoesNotExist:
                    tarea_celery_activa = False
                
                slots_data.append({
                    'programacion': programacion,
                    'celery_activa': tarea_celery_activa,
                    'slot_number': i + 1
                })
            except Exception as slot_error:
                print(f"Error con slot {slot_key}: {slot_error}")
                
    except Exception as e:
        print(f"Error con ProgramacionMultiple: {e}")
        # Usar sistema antiguo como fallback
        # Verificar si hay una tarea activa en Celery Beat (sistema antiguo)
        tarea_activa = None
        try:
            tarea_celery = PeriodicTask.objects.get(name='consulta-procesos-programada', enabled=True)
            if tarea_celery.crontab:
                hour = tarea_celery.crontab.hour
                minute = tarea_celery.crontab.minute
                
                if hour != '*' and minute != '*':
                    try:
                        hora = f"{int(hour):02d}:{int(minute):02d}"
                        tarea_activa = {
                            'hora': hora,
                            'activa': True
                        }
                    except (ValueError, TypeError):
                        tarea_activa = None
        except PeriodicTask.DoesNotExist:
            tarea_activa = None
        
        context = {
            'clientes': clientes,
            'ultimas_radicaciones': ultimas_radicaciones,
            'ultima_consulta': ultima_consulta,
            'tarea_activa': tarea_activa,
        }
        return render(request, 'administradores/dashboard.html', context)
    
    context = {
        'clientes': clientes,
        'clientes_eliminados': clientes_eliminados,
        'ultimas_radicaciones': ultimas_radicaciones,
        'ultima_consulta': ultima_consulta,
        'slots_data': slots_data,
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
            try:
                # Parsear la hora (formato HH:MM)
                hora_parts = hora.split(':')
                hour = int(hora_parts[0])
                minute = int(hora_parts[1])
                
                # Crear o actualizar la programación en Celery Beat
                # Primero eliminar cualquier tarea existente con el mismo nombre
                try:
                    existing_task = PeriodicTask.objects.get(name='consulta-procesos-programada')
                    existing_task.delete()
                except PeriodicTask.DoesNotExist:
                    pass
                
                # Crear el crontab schedule
                schedule, created = CrontabSchedule.objects.get_or_create(
                    minute=minute,
                    hour=hour,
                    day_of_week='*',
                    day_of_month='*',
                    month_of_year='*',
                )
                
                # Crear la tarea periódica
                PeriodicTask.objects.create(
                    crontab=schedule,
                    name='consulta-procesos-programada',
                    task='scraping.tasks.ejecutar_scraping',
                    args=json.dumps([]),
                    kwargs=json.dumps({}),
                    enabled=True,
                )
                
                # Guardar también en el modelo local para mostrar en el dashboard
                ConsultaProgramada.objects.create(hora=hora)
                
                messages.success(request, f'Consulta programada exitosamente para las {hora} todos los días. La tarea se ejecutará automáticamente.')
                
            except Exception as e:
                messages.error(request, f'Error al programar la consulta: {str(e)}')
        else:
            messages.error(request, 'Debe ingresar una hora válida.')
    return redirect('admin_dashboard')

@admin_required
def cancelar_programacion(request):
    if request.method == 'POST':
        try:
            # Eliminar la tarea de Celery Beat
            existing_task = PeriodicTask.objects.get(name='consulta-procesos-programada')
            existing_task.delete()
            messages.success(request, 'Programación de consulta cancelada exitosamente.')
        except PeriodicTask.DoesNotExist:
            messages.warning(request, 'No hay ninguna consulta programada activa.')
        except Exception as e:
            messages.error(request, f'Error al cancelar la programación: {str(e)}')
    return redirect('admin_dashboard')

@admin_required
def gestionar_slot(request):
    """Vista para activar/desactivar y configurar slots individuales"""
    if request.method == 'POST':
        slot_id = request.POST.get('slot_id')
        accion = request.POST.get('accion')
        nueva_hora = request.POST.get('nueva_hora')
        
        try:
            programacion = ProgramacionMultiple.objects.get(slot=slot_id)
            
            if accion == 'activar':
                # Actualizar hora si se proporciona
                if nueva_hora:
                    programacion.hora = nueva_hora
                
                # Activar el slot
                programacion.activo = True
                programacion.save()
                
                # Crear/actualizar tarea en Celery Beat
                hora_parts = str(programacion.hora).split(':')
                hour = int(hora_parts[0])
                minute = int(hora_parts[1])
                
                # Eliminar tarea existente si existe
                try:
                    existing_task = PeriodicTask.objects.get(name=programacion.get_task_name())
                    existing_task.delete()
                except PeriodicTask.DoesNotExist:
                    pass
                
                # Crear nueva tarea
                schedule, created = CrontabSchedule.objects.get_or_create(
                    minute=minute,
                    hour=hour,
                    day_of_week='*',
                    day_of_month='*',
                    month_of_year='*',
                )
                
                PeriodicTask.objects.create(
                    crontab=schedule,
                    name=programacion.get_task_name(),
                    task='scraping.tasks.ejecutar_scraping',
                    args=json.dumps([]),
                    kwargs=json.dumps({}),
                    enabled=True,
                )
                
                messages.success(request, f'{programacion.get_slot_display()} activado exitosamente para las {programacion.hora}')
                
            elif accion == 'desactivar':
                # Desactivar el slot
                programacion.activo = False
                programacion.save()
                
                # Eliminar tarea de Celery Beat
                try:
                    existing_task = PeriodicTask.objects.get(name=programacion.get_task_name())
                    existing_task.delete()
                    messages.success(request, f'{programacion.get_slot_display()} desactivado exitosamente')
                except PeriodicTask.DoesNotExist:
                    messages.warning(request, f'{programacion.get_slot_display()} ya estaba desactivado')
                    
            elif accion == 'actualizar_hora':
                # Solo actualizar la hora sin cambiar el estado
                if nueva_hora:
                    programacion.hora = nueva_hora
                    programacion.save()
                    
                    # Si está activo, actualizar también en Celery
                    if programacion.activo:
                        hora_parts = str(programacion.hora).split(':')
                        hour = int(hora_parts[0])
                        minute = int(hora_parts[1])
                        
                        # Eliminar y recrear tarea
                        try:
                            existing_task = PeriodicTask.objects.get(name=programacion.get_task_name())
                            existing_task.delete()
                        except PeriodicTask.DoesNotExist:
                            pass
                        
                        schedule, created = CrontabSchedule.objects.get_or_create(
                            minute=minute,
                            hour=hour,
                            day_of_week='*',
                            day_of_month='*',
                            month_of_year='*',
                        )
                        
                        PeriodicTask.objects.create(
                            crontab=schedule,
                            name=programacion.get_task_name(),
                            task='scraping.tasks.ejecutar_scraping',
                            args=json.dumps([]),
                            kwargs=json.dumps({}),
                            enabled=True,
                        )
                    
                    messages.success(request, f'Hora del {programacion.get_slot_display()} actualizada a {programacion.hora}')
                    
        except ProgramacionMultiple.DoesNotExist:
            messages.error(request, 'Slot de programación no encontrado')
        except Exception as e:
            messages.error(request, f'Error al gestionar el slot: {str(e)}')
    
    return redirect('admin_dashboard')

@admin_required
def desactivar_todos_slots(request):
    """Vista para desactivar todos los slots de una vez"""
    if request.method == 'POST':
        try:
            slots_activos = ProgramacionMultiple.objects.filter(activo=True)
            count = 0
            
            for slot in slots_activos:
                # Desactivar en la base de datos
                slot.activo = False
                slot.save()
                
                # Eliminar de Celery Beat
                try:
                    existing_task = PeriodicTask.objects.get(name=slot.get_task_name())
                    existing_task.delete()
                    count += 1
                except PeriodicTask.DoesNotExist:
                    pass
            
            if count > 0:
                messages.success(request, f'{count} programación(es) desactivada(s) exitosamente')
            else:
                messages.info(request, 'No había programaciones activas')
                
        except Exception as e:
            messages.error(request, f'Error al desactivar programaciones: {str(e)}')
    
    return redirect('admin_dashboard')

@admin_required
def ver_radicaciones_duplicadas(request):
    """Vista para que los administradores vean radicaciones con números duplicados"""
    from django.db.models import Count
    
    # Obtener números de radicado que aparecen más de una vez
    duplicados = Radicacion.objects.values('numero_radicado').annotate(
        count=Count('numero_radicado')
    ).filter(count__gt=1).order_by('-count')
    
    # Para cada número duplicado, obtener las radicaciones
    radicaciones_duplicadas = []
    for duplicado in duplicados:
        numero = duplicado['numero_radicado']
        radicaciones = Radicacion.objects.filter(numero_radicado=numero).select_related('cliente')
        radicaciones_duplicadas.append({
            'numero_radicado': numero,
            'total_clientes': duplicado['count'],
            'radicaciones': radicaciones
        })
    
    context = {
        'radicaciones_duplicadas': radicaciones_duplicadas,
        'total_duplicados': len(radicaciones_duplicadas)
    }
    
    return render(request, 'administradores/radicaciones_duplicadas.html', context)
from django.contrib import messages
from django.shortcuts import redirect
from django_celery_beat.models import PeriodicTask

def eliminar_todas_tareas_celery(request):
    if request.method == "POST":
        try:
            PeriodicTask.objects.all().delete()
            messages.success(request, "¡Todas las tareas programadas de Celery han sido eliminadas correctamente!")
        except Exception as e:
            messages.error(request, f"Error al eliminar las tareas: {str(e)}")
    return redirect('admin_dashboard')
