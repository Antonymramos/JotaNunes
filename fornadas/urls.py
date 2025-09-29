from django.urls import path
from . import views

app_name = 'fornadas'

urlpatterns = [
    path('', views.listar_fornadas, name='lista_fornadas'),
    path('criar/', views.criar_fornada, name='criar_fornada'),
    path('editar/<int:pk>/', views.editar_fornada, name='editar_fornada'),
    path('deletar/<int:pk>/', views.deletar_fornada, name='deletar_fornada'),
    path('api/receita-quantidade/<int:receita_id>/', views.get_receita_quantidade, name='get_receita_quantidade'),
]