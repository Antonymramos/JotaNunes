from django.db import models, transaction
from receitas.models import Receita
from produtos.models import Produto
from ingredientes.models import Ingrediente
from decimal import Decimal

class Fornada(models.Model):
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name='fornadas')
    data_producao = models.DateTimeField(auto_now_add=True)
    quantidade_produzida = models.PositiveIntegerField(default=1, help_text="Número de execuções da receita")
    produto_gerado = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            quantidade_produzida_receita = getattr(self.receita, 'rendimento', 0)
            quantidade_total = self.quantidade_produzida * quantidade_produzida_receita
            for item in self.receita.itens.all():
                ingrediente = item.ingrediente
                quantidade_a_debitar = item.peso_liquido * self.quantidade_produzida
                if ingrediente.quantidade_estoque < Decimal(str(quantidade_a_debitar)):
                    raise ValueError(f"Estoque insuficiente para {ingrediente.nome}. Disponível: {ingrediente.quantidade_estoque} {ingrediente.unidade_medida}, Necessário: {quantidade_a_debitar} {ingrediente.unidade_medida}")
                ingrediente.quantidade_estoque -= Decimal(str(quantidade_a_debitar))
                ingrediente.save()
            super().save(*args, **kwargs)
            if not self.produto_gerado:
                # Criar ou obter o produto com base no nome da receita
                produto, created = Produto.objects.get_or_create(
                    nome=self.receita.nome,
                    defaults={
                        'quantidade_estoque': 0,  # Inicializa com 0 para evitar sobrescrever
                        'preco_venda': getattr(self.receita, 'custo_por_porcao', 0)
                    }
                )
                self.produto_gerado = produto
                super().save(update_fields=['produto_gerado'])
            # Incrementar o estoque do produto gerado
            self.produto_gerado.quantidade_estoque += quantidade_total
            self.produto_gerado.save()

    def __str__(self):
        quantidade_produzida_receita = getattr(self.receita, 'rendimento', 0)
        return f"Fornada de {self.receita.nome} ({self.quantidade_produzida} execuções = {self.quantidade_produzida * quantidade_produzida_receita} unidades)"

    class Meta:
        verbose_name = "Fornada"
        verbose_name_plural = "Fornadas"