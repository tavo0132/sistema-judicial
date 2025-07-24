from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('iniciar-scraping/', views.iniciar_scraping, name='iniciar_scraping'),
    path('programar-consulta/', views.programar_consulta, name='programar_consulta'),
    path('cancelar-programacion/', views.cancelar_programacion, name='cancelar_programacion'),
    path('gestionar-slot/', views.gestionar_slot, name='gestionar_slot'),
    path('desactivar-todos-slots/', views.desactivar_todos_slots, name='desactivar_todos_slots'),
    path('radicaciones-duplicadas/', views.ver_radicaciones_duplicadas, name='ver_radicaciones_duplicadas'),
    # Nueva URL para cambiar estado de cliente
    path('cambiar-estado-cliente/<int:cliente_id>/', views.cambiar_estado_cliente, name='cambiar_estado_cliente'),
    # Nueva URL para eliminar cliente (soft delete)
    path('eliminar-cliente/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
    # Nueva URL para restaurar cliente eliminado
    path('restaurar-cliente/<int:cliente_id>/', views.restaurar_cliente, name='restaurar_cliente'),
    path('eliminar-todas-tareas-celery/', views.eliminar_todas_tareas_celery, name='eliminar_todas_tareas_celery'),
]