from django.contrib import admin
from .models import Cliente, Endereco

class EnderecoInline(admin.TabularInline):
    model = Endereco
    extra = 1
    fields = ['cep', 'endereco', 'numero_endereco', 'complemento', 'bairro', 'cidade', 'estado', 'is_principal']
    can_delete = True

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'apelido', 'data_nascimento', 'get_endereco_completo', 'get_bairro', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'apelido', 'enderecos__bairro']
    inlines = [EnderecoInline]

    def get_endereco_completo(self, obj):
        return obj.get_endereco_completo()
    get_endereco_completo.short_description = 'Endereço Completo'

    def get_bairro(self, obj):
        endereco = obj.get_endereco_principal()
        return endereco.bairro if endereco else "Sem bairro"
    get_bairro.short_description = 'Bairro'

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'endereco', 'numero_endereco', 'bairro', 'cidade', 'estado', 'is_principal']
    list_filter = ['cidade', 'estado', 'is_principal']
    search_fields = ['endereco', 'bairro', 'cidade', 'estado']