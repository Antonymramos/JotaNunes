from django.db import models
from django.core.validators import MinValueValidator
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal

class Ingrediente(models.Model):
    UNIDADES = (
        ('kg', 'Kilograma'),
        ('g', 'Grama'),
        ('l', 'Litro'),
        ('ml', 'Mililitro'),
        ('un', 'Unidade'),
    )
    nome = models.CharField(max_length=100, unique=True)
    quantidade_estoque = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    unidade_medida = models.CharField(max_length=10, choices=UNIDADES)
    quantidade_minima = models.DecimalField(max_digits=10, decimal_places=2, default=10.00, validators=[MinValueValidator(0)], help_text="Quantidade mínima para alerta")
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def atualizar_estoque(self, quantidade, operacao='adicionar'):
        if operacao == 'adicionar':
            self.quantidade_estoque += Decimal(quantidade)
        elif operacao == 'subtrair':
            if self.quantidade_estoque >= Decimal(quantidade):
                self.quantidade_estoque -= Decimal(quantidade)
            else:
                raise ValueError("Estoque insuficiente!")
        self.save()

    def save(self, *args, **kwargs):
        # Apenas envie e-mail se for um novo alerta
        if self.em_alerta and not hasattr(self, 'notified'):
            send_mail(
                'Alerta de Estoque Baixo',
                f'O estoque de {self.nome} está baixo ({self.quantidade_estoque} {self.unidade_medida}). Por favor, reabasteça!',
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=True,
            )
            self.notified = True
        super().save(*args, **kwargs)
        if hasattr(self, 'notified'):
            del self.notified

    @property
    def em_alerta(self):
        # Forçar conversão para Decimal para evitar problemas com CombinedExpression
        return Decimal(str(self.quantidade_estoque)) <= Decimal(str(self.quantidade_minima))

    def __str__(self):
        return f"{self.nome} ({self.quantidade_estoque} {self.unidade_medida})"

    class Meta:
        verbose_name = "Ingrediente"
        verbose_name_plural = "Ingredientes"