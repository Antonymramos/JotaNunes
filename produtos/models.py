from django.db import models

class Produto(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    quantidade_estoque = models.PositiveIntegerField(default=0)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.nome} ({self.quantidade_estoque} unidades)"

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"