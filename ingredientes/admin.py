from django.contrib import admin
from .models import Ingrediente
from django.db import models

class EmAlertaFilter(admin.SimpleListFilter):
    title = 'em_alerta'
    parameter_name = 'em_alerta'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Sim'),
            ('no', 'Não'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(quantidade_estoque__lte=models.F('quantidade_minima'))
        if self.value() == 'no':
            return queryset.filter(quantidade_estoque__gt=models.F('quantidade_minima'))
        return queryset

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade_estoque', 'unidade_medida', 'em_alerta', 'preco_unitario')
    list_filter = ('unidade_medida', EmAlertaFilter)  # Use custom filter
    search_fields = ('nome',)
    list_editable = ('quantidade_estoque', 'preco_unitario')
    actions = ['enviar_alerta_estoque']

    def enviar_alerta_estoque(self, request, queryset):
        for ingrediente in queryset:
            if ingrediente.em_alerta:
                ingrediente.save()  # Dispara o envio de e-mail
        self.message_user(request, "Alertas de estoque baixo enviados para os ingredientes selecionados.")
    enviar_alerta_estoque.short_description = "Enviar alerta de estoque baixo"