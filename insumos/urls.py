from django.urls import path
from . import views

app_name = 'insumos'

urlpatterns = [
    path('', views.lista_insumos, name='lista_insumos'),
    path('criar/', views.criar_insumo, name='criar_insumo'),
    path('detalhar/<int:id>/', views.detalhar_insumo, name='detalhar_insumo'),
    path('editar/<int:id>/', views.editar_insumo, name='editar_insumo'),
    path('excluir/<int:id>/', views.excluir_insumo, name='excluir_insumo'),
]