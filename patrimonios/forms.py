from django import forms
from .models import Patrimonio

class PatrimonioForm(forms.ModelForm):
    class Meta:
        model = Patrimonio
        fields = ['nome', 'descricao', 'quantidade', 'valor_unitario', 'condicao', 'data_aquisicao', 
                  'data_manutencao', 'status', 'fornecedor', 'nota_fiscal', 'arquivo_nota', 'categoria']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control border-0 rounded-pill', 'rows': 3}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'condicao': forms.TextInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'data_aquisicao': forms.DateInput(attrs={'class': 'form-control border-0 rounded-pill', 'type': 'date'}),
            'data_manutencao': forms.DateInput(attrs={'class': 'form-control border-0 rounded-pill', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control border-0 rounded-pill'}),
            'fornecedor': forms.TextInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'nota_fiscal': forms.TextInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'arquivo_nota': forms.ClearableFileInput(attrs={'class': 'form-control border-0 rounded-pill'}),
            'categoria': forms.Select(attrs={'class': 'form-control border-0 rounded-pill'}),
        }