from django.urls import path
from . import views

app_name = 'ingredientes'

urlpatterns = [
    path('', views.lista_ingredientes, name='lista_ingredientes'),
    path('detalhar/<int:id>/', views.detalhar_ingrediente, name='detalhar_ingrediente'),
    path('criar/', views.criar_ingrediente, name='criar_ingrediente'),
    path('editar/<int:pk>/', views.editar_ingrediente, name='editar_ingrediente'),
    path('excluir/<int:pk>/', views.excluir_ingrediente, name='excluir_ingrediente'),
    path('gerar_lista_compras/', views.gerar_lista_compras, name='gerar_lista_compras'),
    path('test-email/', views.test_email, name='test_email'),
]