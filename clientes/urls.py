from django.urls import path
from .views import cadastrar_cliente, listar_clientes, visualizar_cliente, editar_cliente, excluir_cliente

app_name = 'clientes'
urlpatterns = [
    path('cadastrar/', cadastrar_cliente, name='cadastrar_cliente'),
    path('listar/', listar_clientes, name='listar_clientes'),
    path('visualizar/<int:id>/', visualizar_cliente, name='visualizar_cliente'),
    path('editar/<int:id>/', editar_cliente, name='editar_cliente'),
    path('excluir/<int:id>/', excluir_cliente, name='excluir_cliente'),
]