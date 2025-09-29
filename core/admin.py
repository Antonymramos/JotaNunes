from django.contrib import admin
from django.contrib.auth.models import User
from .models import Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'perfil')
    list_filter = ('perfil',)
    search_fields = ('user__username', 'user__email')
    # Remova readonly_fields ou não inclua 'user'
    fields = ('user', 'perfil')  # Inclua explicitamente os campos do formulário

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            # Filtra apenas usuários que não têm um perfil associado
            kwargs['queryset'] = User.objects.filter(perfil__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)