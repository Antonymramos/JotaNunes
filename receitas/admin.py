from django.contrib import admin
from .models import Receita, ItemReceita

@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'rendimento', 'custo_total', 'custo_por_porcao', 'profissional')
    list_filter = ('rendimento', 'custo_total')
    search_fields = ('nome', 'profissional')
    readonly_fields = ('custo_total', 'custo_por_porcao')

@admin.register(ItemReceita)
class ItemReceitaAdmin(admin.ModelAdmin):
    list_display = ('receita', 'ingrediente', 'peso_bruto', 'peso_liquido', 'valor_total')
    list_filter = ('receita', 'ingrediente')
    search_fields = ('ingrediente__nome',)