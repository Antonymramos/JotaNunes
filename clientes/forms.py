from django import forms
from .models import Cliente, Endereco
from django.core.validators import RegexValidator

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['cep', 'endereco', 'numero_endereco', 'complemento', 'bairro', 'cidade', 'estado', 'is_principal']
        widgets = {
            'cep': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '9', 'placeholder': '00000-000'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'is_principal': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False

class ClienteForm(forms.ModelForm):
    intolerancias = forms.MultipleChoiceField(
        choices=[('Glúten', 'Glúten'), ('Lactose', 'Lactose'), ('Amendoim', 'Amendoim'), ('Nozes', 'Nozes'), ('Ovos', 'Ovos')],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    outra_intolerancia = forms.CharField(max_length=50, required=False, label="Outra Intolerância")
    data_nascimento = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )

    class Meta:
        model = Cliente
        fields = ['nome', 'data_nascimento', 'idade', 'cpf', 'email', 'numero', 'intolerancias', 'preferencias_alimentares', 'observacoes', 'ativo', 'apelido']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'apelido': forms.TextInput(attrs={'class': 'form-control'}),
            'idade': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'readonly': 'readonly'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'pattern': r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', 'placeholder': '000.000.000-00'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'preferencias_alimentares': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ativo': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()
        intolerancias = cleaned_data.get('intolerancias', [])
        outra_intolerancia = cleaned_data.get('outra_intolerancia')
        if outra_intolerancia and outra_intolerancia not in intolerancias:
            intolerancias.append(outra_intolerancia)
        cleaned_data['intolerancias'] = intolerancias
        return cleaned_data

class FiltroClienteForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'Todos'), ('ativo', 'Ativo'), ('inativo', 'Inativo')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )