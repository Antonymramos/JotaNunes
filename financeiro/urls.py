from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    path('', views.dashboard_financeiro, name='dashboard_financeiro'),
    path('vendas/criar/', views.criar_venda, name='criar_venda'),
    path('compras/criar/', views.criar_compra, name='criar_compra'),
    path('gastos-fixos/criar/', views.criar_gasto, name='criar_gasto'),
    path('historico-transacoes/', views.historico_transacoes, name='historico_transacoes'),
    path('gastos/editar/<int:pk>/', views.editar_gasto, name='editar_gasto'),
    path('gastos/deletar/<int:pk>/', views.deletar_gasto, name='deletar_gasto'),
    path('compras/detalhes/<int:pk>/', views.detalhes_compra, name='detalhes_compra'),
    path('vendas/detalhes/<int:pk>/', views.detalhes_venda, name='detalhes_venda'),
]