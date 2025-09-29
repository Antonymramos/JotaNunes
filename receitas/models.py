from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import F, Sum
from decimal import Decimal
from ingredientes.models import Ingrediente

class Receita(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    profissional = models.CharField(max_length=100, blank=True, null=True)
    imagem = models.ImageField(upload_to='receitas/', blank=True, null=True)
    modo_preparo = models.TextField(blank=True, help_text="Digite cada passo do modo de preparo em uma nova linha.")
    rendimento = models.PositiveIntegerField(default=20, help_text="Número de porções")
    custo_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    custo_por_porcao = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.atualizar_custos()

    def atualizar_custos(self):
        total_insumos = self.itens.aggregate(total=Sum(F('peso_liquido') * F('valor_unitario')))['total'] or Decimal('0.00')
        self.custo_total = total_insumos
        self.custo_por_porcao = total_insumos / self.rendimento if self.rendimento > 0 else Decimal('0.00')
        super().save(update_fields=['custo_total', 'custo_por_porcao'])

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Receita"
        verbose_name_plural = "Receitas"

class ItemReceita(models.Model):
    receita = models.ForeignKey(Receita, related_name='itens', on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    unidade = models.CharField(max_length=20, choices=Ingrediente.UNIDADES)  # Assumindo que Ingrediente tem UNIDADES
    peso_bruto = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0)])
    peso_liquido = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    fator_correcao = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('1.000'), validators=[MinValueValidator(Decimal('0.001'))])
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Calcular peso_liquido ou fator_correcao com base nos valores fornecidos
        if self.peso_bruto and self.peso_liquido and self.peso_liquido > 0:
            # Calcular fator_correcao se peso_bruto e peso_liquido forem fornecidos
            self.fator_correcao = (self.peso_bruto / self.peso_liquido).quantize(Decimal('0.001'))
        elif self.peso_bruto and self.fator_correcao and self.fator_correcao > 0:
            # Calcular peso_liquido se peso_bruto e fator_correcao forem fornecidos
            self.peso_liquido = (self.peso_bruto / self.fator_correcao).quantize(Decimal('0.001'))
        elif self.peso_bruto and not self.peso_liquido:
            # Se apenas peso_bruto for fornecido, assumir peso_liquido = peso_bruto
            self.peso_liquido = self.peso_bruto.quantize(Decimal('0.001'))
            self.fator_correcao = Decimal('1.000')

        # Atualizar valor_unitario se não fornecido
        if self.ingrediente and not self.valor_unitario:
            self.valor_unitario = self.ingrediente.preco_unitario

        # Calcular valor_total
        if self.peso_liquido and self.valor_unitario:
            self.valor_total = (self.peso_liquido * self.valor_unitario).quantize(Decimal('0.01'))

        super().save(*args, **kwargs)
        self.receita.atualizar_custos()

    def __str__(self):
        return f"{self.ingrediente.nome} - {self.receita.nome}"

    class Meta:
        verbose_name = "Item de Receita"
        verbose_name_plural = "Itens de Receita"