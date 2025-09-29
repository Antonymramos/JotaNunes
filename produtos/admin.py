from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade_estoque', 'preco_venda')
    search_fields = ('nome',)
    list_editable = ('quantidade_estoque', 'preco_venda')