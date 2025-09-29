from django.contrib import admin
from .models import Fornada

@admin.register(Fornada)
class FornadaAdmin(admin.ModelAdmin):
    list_display = ('receita', 'quantidade_produzida', 'produto_gerado', 'data_producao')
    list_filter = ('data_producao', 'receita')
    search_fields = ('receita__nome', 'produto_gerado__nome')
    readonly_fields = ('data_producao',)
    date_hierarchy = 'data_producao'