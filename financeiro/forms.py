# financeiro/forms.py (Código completo com atualizações: adicionados campos para forma_pagamento e desconto em VendaForm. Validações mantidas.)

from django import forms
from django.forms import modelformset_factory
from .models import Venda, Compra, Gasto, VendaItem
from produtos.models import Produto
from ingredientes.models import Ingrediente
from clientes.models import Cliente  # Alterado para importar do app clientes
from django.core.exceptions import ValidationError

class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['cliente', 'forma_pagamento', 'desconto']  # Campos adicionados
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'desconto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'required': False}),
        }

    def clean_cliente(self):
        cliente = self.cleaned_data['cliente']
        if not cliente:
            raise ValidationError("O cliente é obrigatório.")
        return cliente

    def clean_desconto(self):
        desconto = self.cleaned_data['desconto']
        if desconto < 0:
            raise ValidationError("O desconto não pode ser negativo.")
        return desconto

VendaItemFormSet = modelformset_factory(
    VendaItem,
    fields=['produto', 'quantidade'],
    extra=1,
    widgets={
        'produto': forms.Select(attrs={'class': 'form-select', 'required': True}),
        'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'required': True}),
    },
    can_delete=True
)

class CompraForm(forms.ModelForm):
    unidade_medida = forms.ChoiceField(
        label='Unidade de Medida',
        choices=Ingrediente.UNIDADES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': True})
    )

    class Meta:
        model = Compra
        fields = ['ingrediente', 'quantidade_comprada', 'valor_unitario', 'unidade_medida']
        widgets = {
            'ingrediente': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'quantidade_comprada': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01', 'required': True}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.ingrediente_id:
            self.fields['unidade_medida'].initial = self.instance.ingrediente.unidade_medida
            self.fields['unidade_medida'].widget.attrs['disabled'] = True
        elif 'ingrediente' in self.data:
            try:
                ingrediente_id = int(self.data.get('ingrediente'))
                ingrediente = Ingrediente.objects.get(id=ingrediente_id)
                self.fields['unidade_medida'].initial = ingrediente.unidade_medida
                self.fields['unidade_medida'].widget.attrs['disabled'] = True
            except (ValueError, Ingrediente.DoesNotExist):
                pass

    def clean(self):
        cleaned_data = super().clean()
        ingrediente = cleaned_data.get('ingrediente')
        unidade_medida = cleaned_data.get('unidade_medida')
        if ingrediente and unidade_medida and unidade_medida != ingrediente.unidade_medida:
            raise forms.ValidationError("A unidade de medida não corresponde ao ingrediente.")
        return cleaned_data

    def clean_quantidade_comprada(self):
        quantidade = self.cleaned_data['quantidade_comprada']
        if quantidade <= 0:
            raise forms.ValidationError("A quantidade deve ser maior que zero.")
        return quantidade

    def clean_valor_unitario(self):
        valor = self.cleaned_data['valor_unitario']
        if valor < 0:
            raise forms.ValidationError("O valor unitário não pode ser negativo.")
        return valor

class GastoForm(forms.ModelForm):
    data_pagamento = forms.DateField(
        label='Data do Pagamento',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': False}),
        required=False
    )

    class Meta:
        model = Gasto
        fields = ['descricao', 'valor', 'dia_pagamento', 'data_pagamento', 'categoria']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'maxlength': '100'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}),
            'dia_pagamento': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '31', 'required': False}),
            'categoria': forms.Select(attrs={'class': 'form-select', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get('categoria') == 'PAGAMENTO_FUNCIONARIOS' or \
           (self.data.get('categoria') == 'PAGAMENTO_FUNCIONARIOS'):
            self.fields['descricao'].label = 'Nome do Funcionário'

    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        dia_pagamento = cleaned_data.get('dia_pagamento')
        data_pagamento = cleaned_data.get('data_pagamento')

        if categoria == 'GASTOS_FIXOS':
            if not dia_pagamento:
                raise ValidationError("O dia de pagamento é obrigatório para Gastos Fixos.")
            if data_pagamento:
                raise ValidationError("Data de pagamento não deve ser preenchida para Gastos Fixos.")
        else:
            if not data_pagamento:
                raise ValidationError("A data de pagamento é obrigatória para esta categoria.")
            if dia_pagamento:
                raise ValidationError("Dia de pagamento não deve ser preenchido para esta categoria.")

        return cleaned_data

    def clean_valor(self):
        valor = self.cleaned_data['valor']
        if valor <= 0:
            raise ValidationError("O valor deve ser maior que zero.")
        return valor

    def clean_dia_pagamento(self):
        dia = self.cleaned_data.get('dia_pagamento')
        categoria = self.cleaned_data.get('categoria')
        if categoria == 'GASTOS_FIXOS' and dia and (dia < 1 or dia > 31):
            raise ValidationError("O dia de pagamento deve estar entre 1 e 31.")
        return dia