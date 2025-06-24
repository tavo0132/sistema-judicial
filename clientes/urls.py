from django.urls import path
from . import views

urlpatterns = [
    # Por ahora solo definiremos la ruta del login
    path('login/', views.cliente_login, name='cliente_login'),
    path('dashboard/', views.cliente_dashboard, name='cliente_dashboard'),
    path('registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('editar/<int:id_cliente>/', views.editar_cliente, name='editar_cliente'),
    path('radicaciones/<int:id_cliente>/', views.ver_radicaciones_cliente, name='ver_radicaciones_cliente'),
    path('radicaciones/<int:cliente_id>/crear/', views.crear_radicacion, name='crear_radicacion'),
    path('radicaciones/eliminar/<int:radicacion_id>/', views.eliminar_radicacion, name='eliminar_radicacion'),
]