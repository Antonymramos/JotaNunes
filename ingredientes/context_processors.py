from .models import Ingrediente
from django.db.models import F

def alerta_ingredientes(request):
    ingredientes_alerta_count = Ingrediente.objects.filter(quantidade_estoque__lte=F('quantidade_minima')).count()
    return {'ingredientes_alerta_count': ingredientes_alerta_count}