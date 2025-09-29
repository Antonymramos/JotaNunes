# usuarios/models.py
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import Permission

class Cargo(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    grupo = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='cargo')

    def __str__(self):
        return self.nome