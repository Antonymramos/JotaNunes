from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Receita, ItemReceita
from ingredientes.models import Ingrediente

class ReceitaForm(forms.ModelForm):
    modo_preparo = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control border py-2'}),
        required=False,
        help_text='Digite cada passo do modo de preparo em uma nova linha.'
    )
    imagem = forms.ImageField(
        required=False,
        help_text='Carregue uma foto do prato (opcional, máx. 2MB, JPG/PNG).'
    )
    rendimento = forms.IntegerField(
        min_value=1,
        initial=20,
        help_text='Número de porções produzidas pela receita.',
        widget=forms.NumberInput(attrs={'class': 'form-control border py-2'})
    )

    class Meta:
        model = Receita
        fields = ['nome', 'imagem', 'modo_preparo', 'rendimento']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control border py-2'}),
        }

    def clean_imagem(self):
        imagem = self.cleaned_data.get('imagem')
        if imagem:
            max_size = 2 * 1024 * 1024  # 2MB
            if imagem.size > max_size:
                raise ValidationError('A imagem excede o limite de 2MB.')
            if not imagem.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise ValidationError('Formato inválido. Use JPG ou PNG.')
        return imagem

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if not nome:
            raise ValidationError('O nome da receita é obrigatório.')
        return nome

class ItemReceitaForm(forms.ModelForm):
    valor_unitario = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label='Valor Unitário (R$)',
        help_text='Preenchido automaticamente com base no ingrediente ou editável manualmente.',
        widget=forms.NumberInput(attrs={'class': 'form-control border py-2', 'step': '0.01'})
    )
    fator_correcao = forms.DecimalField(
        max_digits=10,
        decimal_places=3,
        initial=Decimal('1.000'),
        label='Fator de Correção',
        help_text='Fator para ajustar peso bruto para líquido (ex.: 0.9 para 90% de aproveitamento). Calculado se peso líquido for fornecido.',
        widget=forms.NumberInput(attrs={'class': 'form-control border py-2', 'step': '0.001'})
    )
    peso_liquido = forms.DecimalField(
        max_digits=10,
        decimal_places=3,
        required=False,
        label='Peso Líquido (g)',
        help_text='Calculado com base no peso bruto e fator de correção, ou usado para calcular o fator.',
        widget=forms.NumberInput(attrs={'class': 'form-control border py-2', 'step': '0.001'})
    )
    peso_bruto = forms.DecimalField(
        max_digits=10,
        decimal_places=3,
        label='Peso Bruto (g)',
        help_text='Peso bruto do ingrediente (obrigatório).',
        widget=forms.NumberInput(attrs={'class': 'form-control border py-2', 'step': '0.001'})
    )

    class Meta:
        model = ItemReceita
        fields = ['ingrediente', 'unidade', 'peso_bruto', 'peso_liquido', 'fator_correcao', 'valor_unitario']
        widgets = {
            'ingrediente': forms.Select(attrs={'class': 'form-control border py-2'}),
            'unidade': forms.Select(attrs={'class': 'form-control border py-2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Preencher valor_unitario com base no ingrediente
        if self.instance.pk and self.instance.ingrediente_id:
            self.fields['valor_unitario'].initial = self.instance.ingrediente.preco_unitario
        elif self.data and self.data.get(f'{self.prefix}-ingrediente'):
            try:
                ingrediente = Ingrediente.objects.get(pk=self.data.get(f'{self.prefix}-ingrediente'))
                self.fields['valor_unitario'].initial = ingrediente.preco_unitario
            except Ingrediente.DoesNotExist:
                self.fields['valor_unitario'].initial = Decimal('0.00')

    def clean(self):
        cleaned_data = super().clean()
        peso_bruto = cleaned_data.get('peso_bruto')
        fator_correcao = cleaned_data.get('fator_correcao')
        peso_liquido = cleaned_data.get('peso_liquido')
        ingrediente = cleaned_data.get('ingrediente')

        # Validar ingrediente
        if not ingrediente:
            raise ValidationError({'ingrediente': 'O ingrediente é obrigatório.'})

        # Validar peso_bruto
        if peso_bruto is None or peso_bruto < 0:
            raise ValidationError({'peso_bruto': 'O peso bruto é obrigatório e deve ser maior ou igual a zero.'})

        # Calcular peso_liquido ou fator_correcao
        if peso_bruto > 0:
            if peso_liquido is not None and peso_liquido > 0:
                # Calcular fator_correcao se peso_bruto e peso_liquido forem fornecidos
                if peso_liquido == 0:
                    raise ValidationError({'peso_liquido': 'O peso líquido não pode ser zero.'})
                cleaned_data['fator_correcao'] = (peso_bruto / peso_liquido).quantize(Decimal('0.001'))
            elif fator_correcao is not None and fator_correcao > 0:
                # Calcular peso_liquido se peso_bruto e fator_correcao forem fornecidos
                cleaned_data['peso_liquido'] = (peso_bruto / fator_correcao).quantize(Decimal('0.001'))
            else:
                # Se apenas peso_bruto for fornecido, assumir peso_liquido = peso_bruto
                cleaned_data['peso_liquido'] = peso_bruto.quantize(Decimal('0.001'))
                cleaned_data['fator_correcao'] = Decimal('1.000')
        else:
            if peso_liquido is not None or fator_correcao is not None:
                raise ValidationError({
                    'peso_bruto': 'O peso bruto deve ser maior que zero quando peso líquido ou fator de correção são fornecidos.'
                })

        # Validar fator_correcao
        if cleaned_data.get('fator_correcao') <= 0:
            raise ValidationError({'fator_correcao': 'O fator de correção deve ser maior que zero.'})

        return cleaned_data

ItemReceitaFormSet = inlineformset_factory(
    Receita,
    ItemReceita,
    form=ItemReceitaForm,
    extra=1,
    can_delete=True,
    validate_max=True
)