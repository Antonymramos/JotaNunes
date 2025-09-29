# financeiro/models.py (Código completo com atualizações: adicionados campos para formas de pagamento e descontos em Venda. Lógica de cálculo de total atualizada para considerar desconto.)

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from produtos.models import Produto
from ingredientes.models import Ingrediente
from clientes.models import Cliente
from decimal import Decimal

# Escolhas para o campo de categoria
CATEGORIAS_GASTO = (
    ('GASTOS_FIXOS', 'Gastos Fixos'),
    ('PAGAMENTO_FUNCIONARIOS', 'Pagamento de Funcionários'),
    ('OUTROS', 'Outros'),
)

# Formas de pagamento adicionadas
FORMAS_PAGAMENTO = (
    ('DINHEIRO', 'Dinheiro'),
    ('CARTAO_CREDITO', 'Cartão de Crédito'),
    ('CARTAO_DEBITO', 'Cartão de Débito'),
    ('PIX', 'PIX'),
    ('OUTRO', 'Outro'),
)

class Compra(models.Model):
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name='compras')
    quantidade_comprada = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    data_compra = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Atualiza o estoque do ingrediente ao salvar a compra."""
        ingrediente = self.ingrediente
        ingrediente.quantidade_estoque += self.quantidade_comprada
        ingrediente.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Compra de {self.quantidade_comprada} {self.ingrediente.unidade_medida} de {self.ingrediente.nome}"

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"

class Gasto(models.Model):
    descricao = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    data = models.DateTimeField(default=timezone.now)
    dia_pagamento = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(31)], help_text="Dia do mês para pagamento (1-31, usado para Gastos Fixos)")
    data_pagamento = models.DateField(null=True, blank=True, help_text="Data exata do pagamento (usado para Pagamento de Funcionários e Outros)")
    categoria = models.CharField(max_length=30, choices=CATEGORIAS_GASTO, default='OUTROS')

    def __str__(self):
        return f"{self.descricao} - R${self.valor} ({self.get_categoria_display()})"

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"

class Venda(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendas')
    data_venda = models.DateTimeField(default=timezone.now)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    forma_pagamento = models.CharField(max_length=20, choices=FORMAS_PAGAMENTO, default='DINHEIRO')  # Adicionado
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])  # Adicionado

    def calculate_total(self):
        """Calcula o valor total da venda somando os subtotais dos itens."""
        self.valor_total = sum(item.subtotal for item in self.items.all()) - self.desconto

    def save(self, *args, **kwargs):
        """Salva a venda e atualiza o campo ultimo_contato do cliente."""
        print(f"Salvando Venda, pk antes de salvar: {self.pk}")  # Depuração
        # Salva a instância de Venda primeiro para garantir que tenha um pk
        super().save(*args, **kwargs)
        print(f"Venda salva com pk: {self.pk}")  # Depuração
        # Atualiza o campo ultimo_contato do cliente, se aplicável
        if self.cliente:
            print(f"Atualizando ultimo_contato do cliente {self.cliente.nome}")  # Depuração
            self.cliente.ultimo_contato = self.data_venda
            self.cliente.save(update_fields=['ultimo_contato'])

    def __str__(self):
        return f"Venda {self.id} - {self.cliente or 'Anônimo'}"

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"

class VendaItem(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='items')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        """Calcula o subtotal e atualiza o estoque do produto."""
        print(f"Salvando VendaItem, venda pk: {self.venda.pk if self.venda else 'None'}, produto: {self.produto.nome}")  # Depuração
        self.subtotal = self.quantidade * self.produto.preco_venda
        if self.produto.quantidade_estoque >= self.quantidade:
            self.produto.quantidade_estoque -= self.quantidade
            self.produto.save()
        else:
            raise ValueError(f"Estoque insuficiente para {self.produto.nome}.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome}"

    class Meta:
        verbose_name = "Item da Venda"
        verbose_name_plural = "Itens da Venda"