from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from ingredientes.models import Ingrediente
from fornadas.models import Fornada
from produtos.models import Produto
from django.db.models import F, Sum
from patrimonios.models import Patrimonio
from insumos.models import Insumo
from financeiro.models import Venda, Compra, Gasto, VendaItem
from clientes.models import Cliente
from receitas.models import Receita
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

@login_required
def dashboard(request):
    # Métricas Financeiras
    total_compras = Compra.objects.annotate(
        valor_total=F('quantidade_comprada') * F('valor_unitario')
    ).aggregate(total_compras=Sum('valor_total'))['total_compras'] or Decimal('0.00')

    total_vendas = Venda.objects.aggregate(total_vendas=Sum('valor_total'))['total_vendas'] or Decimal('0.00')
    if total_vendas == 0:
        total_vendas = Venda.objects.annotate(
            valor_total=F('items__quantidade') * F('items__produto__preco_venda')
        ).aggregate(total_vendas=Sum('valor_total'))['total_vendas'] or Decimal('0.00')

    total_gastos = Gasto.objects.aggregate(total_gastos=Sum('valor'))['total_gastos'] or Decimal('0.00')
    saldo_caixa = total_vendas - total_compras - total_gastos

    # Última atualização
    ultimas_data = []
    if Venda.objects.exists():
        ultimas_data.append(Venda.objects.latest('data_venda').data_venda)
    if Compra.objects.exists():
        ultimas_data.append(Compra.objects.latest('data_compra').data_compra)
    if Gasto.objects.exists():
        ultimas_data.append(Gasto.objects.latest('data').data)
    ultimo_update = max(ultimas_data) if ultimas_data else timezone.now()

    # Ingredientes e Insumos
    ingredientes_alerta = Ingrediente.objects.filter(quantidade_estoque__lte=F('quantidade_minima'))
    insumos_alerta = Insumo.objects.filter(quantidade_estoque__lte=F('quantidade_minima'))
    alertas_count = ingredientes_alerta.count() + insumos_alerta.count()
    total_ingredientes = Ingrediente.objects.count()
    total_insumos = Insumo.objects.count()

    # Receitas
    total_receitas = Receita.objects.count()
    receitas_ativas = total_receitas

    # Fornadas
    total_fornadas = Fornada.objects.count()
    fornadas_hoje = Fornada.objects.filter(data_producao__date=date.today()).count()

    # Produtos
    total_produtos = Produto.objects.count()
    produtos_em_estoque = Produto.objects.filter(quantidade_estoque__gt=0).count()
    total_produtos_vendidos = VendaItem.objects.aggregate(total=Sum('quantidade'))['total'] or 0

    # Clientes
    total_clientes = Cliente.objects.count()
    clientes_ativos = Cliente.objects.filter(ativo=True).count()

    # Patrimônios
    total_patrimonios = Patrimonio.objects.annotate(
        valor_total=F('quantidade') * F('valor_unitario')
    ).aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')
    patrimonios_ativos = Patrimonio.objects.count()

    # Atividades Recentes
    ultimas_vendas = Venda.objects.order_by('-data_venda')[:3]
    ultimas_compras = Compra.objects.order_by('-data_compra')[:3]
    ultimas_fornadas = Fornada.objects.order_by('-data_producao')[:3]

    context = {
        'saldo_caixa': saldo_caixa,
        'ultimo_update': ultimo_update,
        'alertas_count': alertas_count,
        'total_produtos_vendidos': total_produtos_vendidos,
        'total_ingredientes': total_ingredientes,
        'total_insumos': total_insumos,
        'receitas_ativas': receitas_ativas,
        'total_receitas': total_receitas,
        'total_fornadas': total_fornadas,
        'fornadas_hoje': fornadas_hoje,
        'total_produtos': total_produtos,
        'produtos_em_estoque': produtos_em_estoque,
        'total_clientes': total_clientes,
        'clientes_ativos': clientes_ativos,
        'total_vendas': total_vendas,
        'total_compras': total_compras,
        'total_patrimonios': total_patrimonios,
        'patrimonios_ativos': patrimonios_ativos,
        'ultimas_vendas': ultimas_vendas,
        'ultimas_compras': ultimas_compras,
        'ultimas_fornadas': ultimas_fornadas,
        'content_title': 'Dashboard ERP Padaria',
    }
    return render(request, 'core/index.html', context)

def is_gestor(user):
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.perfil == 'GESTOR'

@login_required
def listar_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'core/listar_usuarios.html', {
        'usuarios': usuarios,
        'content_title': 'Lista de Usuários',
    })

@login_required
def dashboard_estoques(request):
    context = {
        'ingredientes_count': Ingrediente.objects.count(),
        'patrimonios_count': Patrimonio.objects.count(),
        'insumos_count': Insumo.objects.count(),
        'alertas_count': Ingrediente.objects.filter(quantidade_estoque__lte=F('quantidade_minima')).count() +
                        Insumo.objects.filter(quantidade_estoque__lte=F('quantidade_minima')).count(),
    }
    return render(request, 'core/dashboard_estoques.html', context)