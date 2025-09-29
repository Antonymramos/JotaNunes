from django.contrib import admin
from .models import Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'perfil')
    list_filter = ('perfil',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)