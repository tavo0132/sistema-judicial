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
]