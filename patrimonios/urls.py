from django.urls import path
from . import views

app_name = 'patrimonios'

urlpatterns = [
    path('', views.lista_patrimonios, name='lista_patrimonios'),
    path('criar/', views.criar_patrimonio, name='criar_patrimonio'),
    path('<int:id>/', views.detalhar_patrimonio, name='detalhar_patrimonio'),
    path('editar/<int:id>/', views.editar_patrimonio, name='editar_patrimonio'),
    path('excluir/<int:id>/', views.excluir_patrimonio, name='excluir_patrimonio'),
    path('relatorio/', views.gerar_relatorio_patrimonios, name='gerar_relatorio_patrimonios'),
]