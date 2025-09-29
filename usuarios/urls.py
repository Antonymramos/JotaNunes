# usuarios/urls.py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('criar/', views.criar_usuario, name='criar_usuario'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('listar/', views.listar_usuarios, name='listar_usuarios'),
    path('deletar/<int:pk>/', views.deletar_usuario, name='deletar_usuario'),
    path('cargos/criar/', views.criar_cargo, name='criar_cargo'),
    path('cargos/listar/', views.listar_cargos, name='listar_cargos'),
    path('cargos/deletar/<int:pk>/', views.deletar_cargo, name='deletar_cargo'),
]