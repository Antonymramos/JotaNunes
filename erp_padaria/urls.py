from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from django.conf.urls.static import static  # Import the static function
from django.conf import settings  # Import settings to access MEDIA_URL and MEDIA_ROOT

urlpatterns = [
    path('', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    path('ingredientes/', include('ingredientes.urls')),
    path('receitas/', include('receitas.urls')),
    path('fornadas/', include('fornadas.urls')),
    path('produtos/', include('produtos.urls')),
    path('clientes/', include('clientes.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('patrimonios/', include('patrimonios.urls')),
    path('insumos/', include('insumos.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)