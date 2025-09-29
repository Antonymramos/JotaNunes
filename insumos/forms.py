from django import forms
from .models import Insumo

class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ['nome', 'descricao', 'quantidade_estoque', 'quantidade_minima', 'unidade_medida', 
                  'preco_unitario', 'data_aquisicao', 'data_validade', 'status', 'fornecedor', 
                  'numero_nota', 'arquivo_nota', 'categoria']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control border-0 rounded-pill', 'rows': 3}),
            'quantidade_estoque': forms.NumberInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'quantidade_minima': forms.NumberInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'unidade_medida': forms.TextInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'preco_unitario': forms.NumberInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'data_aquisicao': forms.DateInput(attrs={'class': 'form-control border-0 rounded-pill', 'type': 'date'}),
            'data_validade': forms.DateInput(attrs={'class': 'form-control border-0 rounded-pill', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control border-0 rounded-pill'}),
            'fornecedor': forms.TextInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'numero_nota': forms.TextInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'arquivo_nota': forms.ClearableFileInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'categoria': forms.Select(attrs={'class': 'form-control border-0 rounded-pill'}),
        }