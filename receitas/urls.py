from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'receitas'

urlpatterns = [
    path('', views.listar_receitas, name='listar_receitas'),
    path('<int:pk>/', views.detalhar_receita, name='detalhar_receita'),
    path('criar/', views.criar_receita, name='criar_receita'),
    path('editar/<int:pk>/', views.editar_receita, name='editar_receita'),
    path('deletar/<int:pk>/', views.deletar_receita, name='deletar_receita'),
    path('relatorio/<int:pk>/', views.gerar_relatorio_receita, name='gerar_relatorio_receita'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)