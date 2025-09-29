from django.contrib import admin
from .models import Venda, Compra, Gasto, VendaItem

# Configurações personalizadas para os modelos (opcional)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'data_venda', 'valor_total')
    list_filter = ('data_venda',)
    search_fields = ('cliente__nome',)

class CompraAdmin(admin.ModelAdmin):
    list_display = ('ingrediente', 'quantidade_comprada', 'valor_unitario', 'data_compra')
    list_filter = ('data_compra',)
    search_fields = ('ingrediente__nome',)

class GastoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'data', 'categoria')
    list_filter = ('categoria', 'data')
    search_fields = ('descricao',)

class VendaItemAdmin(admin.ModelAdmin):
    list_display = ('venda', 'produto', 'quantidade', 'subtotal')
    search_fields = ('produto__nome',)

# Registro dos modelos
admin.site.register(Venda, VendaAdmin)
admin.site.register(Compra, CompraAdmin)
admin.site.register(Gasto, GastoAdmin)
admin.site.register(VendaItem, VendaItemAdmin)