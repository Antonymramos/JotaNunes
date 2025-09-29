from django import forms
from .models import Ingrediente

class IngredienteForm(forms.ModelForm):
    # Usar as mesmas escolhas definidas no modelo Ingrediente
    unidade_medida = forms.ChoiceField(choices=Ingrediente.UNIDADES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Ingrediente
        fields = ['nome', 'quantidade_estoque', 'unidade_medida', 'quantidade_minima', 'preco_unitario']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade_estoque': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantidade_minima': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'preco_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }