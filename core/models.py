from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
       PERFIL_CHOICES = [
           ('GESTOR', 'Gestor'),
           ('OPERADOR', 'Operador'),
       ]
       user = models.OneToOneField(User, on_delete=models.CASCADE)
       perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES, default='OPERADOR')

       def __str__(self):
           return f"{self.user.username} - {self.perfil}"