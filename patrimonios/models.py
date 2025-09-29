from django.db import models

class Patrimonio(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    condicao = models.CharField(max_length=50)
    data_aquisicao = models.DateField(blank=True, null=True, verbose_name="Data de Aquisição")
    data_manutencao = models.DateField(blank=True, null=True, verbose_name="Data de Manutenção")
    status = models.CharField(max_length=20, choices=[
        ('Em Uso na Produção', 'Em Uso na Produção'),
        ('Em Manutenção', 'Em Manutenção'),
        ('Desativado', 'Desativado'),
    ], default='Em Uso na Produção')
    fornecedor = models.CharField(max_length=100, blank=True, verbose_name="Fornecedor")
    nota_fiscal = models.CharField(max_length=50, blank=True, verbose_name="Número da Nota Fiscal")
    arquivo_nota = models.FileField(upload_to='notas_fiscais/', blank=True, null=True, verbose_name="Arquivo da Nota (PDF)")
    categoria = models.CharField(max_length=50, choices=[
        ('Equipamento de Produção', 'Equipamento de Produção'),
        ('Mobiliário', 'Mobiliário'),
        ('Utensílios', 'Utensílios'),
    ], default='Equipamento de Produção')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Patrimônios"