from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'core'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('estoques/', views.dashboard_estoques, name='dashboard_estoques'),
    # Adicione se implementar:
    # path('usuarios/criar/', views.criar_usuario, name='criar_usuario'),
    # path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
]