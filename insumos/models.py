from django.db import models

class Insumo(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Insumo")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    quantidade_estoque = models.PositiveIntegerField(verbose_name="Quantidade em Estoque")
    quantidade_minima = models.PositiveIntegerField(verbose_name="Quantidade Mínima")
    unidade_medida = models.CharField(max_length=50, verbose_name="Unidade de Medida")
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário")
    data_aquisicao = models.DateField(blank=True, null=True, verbose_name="Data de Aquisição")
    data_validade = models.DateField(blank=True, null=True, verbose_name="Data de Validade")
    status = models.CharField(max_length=20, choices=[
        ('Em Estoque', 'Em Estoque'),
        ('Em Uso', 'Em Uso'),
        ('Esgotado', 'Esgotado'),
    ], default='Em Estoque')
    fornecedor = models.CharField(max_length=100, blank=True, verbose_name="Fornecedor")
    numero_nota = models.CharField(max_length=50, blank=True, verbose_name="Número da Nota Fiscal")
    arquivo_nota = models.FileField(upload_to='notas_insumos/', blank=True, null=True, verbose_name="Arquivo da Nota (PDF)")
    categoria = models.CharField(max_length=50, choices=[
        ('Embalagem', 'Embalagem'),
        ('Pacote de Ingrediente', 'Pacote de Ingrediente'),
        ('Outros', 'Outros'),
    ], default='Embalagem')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Insumos"