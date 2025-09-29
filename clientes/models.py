from django.db import models
from django.core.validators import RegexValidator

class Endereco(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name='enderecos')
    cep = models.CharField(max_length=9, blank=True, null=True)
    endereco = models.CharField(max_length=100, blank=True, null=True)
    numero_endereco = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=50, blank=True, null=True)
    bairro = models.CharField(max_length=50, blank=True, null=True)
    cidade = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    is_principal = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_principal:
            Endereco.objects.filter(cliente=self.cliente, is_principal=True).exclude(id=self.id).update(is_principal=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.endereco}, {self.numero_endereco} - {self.bairro}"

class Cliente(models.Model):
    nome = models.CharField(max_length=100, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    idade = models.PositiveIntegerField(blank=True, null=True)
    cpf = models.CharField(
        max_length=14,
        validators=[RegexValidator(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', 'CPF deve estar no formato 000.000.000-00')],
        blank=True, null=True
    )
    email = models.EmailField(unique=False, blank=True, null=True)
    numero = models.CharField(max_length=15, blank=True, null=True)
    intolerancias = models.JSONField(default=list, blank=True)
    preferencias_alimentares = models.TextField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    ultimo_contato = models.DateTimeField(auto_now_add=True)
    apelido = models.CharField(max_length=50, blank=True, null=True, verbose_name="Apelido/Referência Pessoal")

    def save(self, *args, **kwargs):
        if self.data_nascimento:
            from datetime import date
            today = date.today()
            self.idade = today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))
        super().save(*args, **kwargs)

    def get_endereco_principal(self):
        return self.enderecos.filter(is_principal=True).first()

    def get_endereco_completo(self):
        endereco = self.get_endereco_principal()
        if endereco:
            parts = [part for part in [
                endereco.endereco,
                endereco.numero_endereco,
                endereco.complemento,
                endereco.bairro,
                endereco.cidade,
                endereco.estado
            ] if part]
            return ", ".join(parts)
        return "Sem endereço"

    def __str__(self):
        return self.nome or "Cliente sem nome"