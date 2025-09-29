from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from ingredientes.models import Ingrediente
from fornadas.models import Fornada
from produtos.models import Produto
from django.db.models import F, Sum
from patrimonios.models import Patrimonio
from insumos.models import Insumo
from financeiro.models import Venda, Compra, GastoFixo  # Assumindo que existem
from clientes.models import Cliente  # Assumindo que existe
from receitas.models import Receita  # Assumindo que existe
from django.utils import timezone
from datetime import date

@login_required
def dashboard(request):
    # Métricas Financeiras
    # Ajuste para Compra: Calcular valor_total como quantidade_comprada * valor_unitario
    total_compras = Compra.objects.annotate(
        valor_total=F('quantidade_comprada') * F('valor_unitario')
    ).aggregate(total_compras=Sum('valor_total'))['total_compras'] or 0

    # Ajuste para Venda: Assumindo que valor_total pode não existir (ajustar se necessário)
    total_vendas = Venda.objects.aggregate(total_vendas=Sum('valor_total'))['total_vendas'] or 0
    if total_vendas is None:  # Se valor_total não existir, calcular como em Compra
        total_vendas = Venda.objects.annotate(
            valor_total=F('quantidade_vendida') * F('valor_unitario')
        ).aggregate(total_vendas=Sum('valor_total'))['total_vendas'] or 0

    total_gastos = GastoFixo.objects.aggregate(total_gastos=Sum('valor'))['total_gastos'] or 0
    saldo_caixa = total_vendas - total_compras - total_gastos

    # Última atualização (data da última transação)
    ultimas_data = []
    if Venda.objects.exists():
        ultimas_data.append(Venda.objects.latest('data_venda').data_venda)
    if Compra.objects.exists():
        ultimas_data.append(Compra.objects.latest('data_compra').data_compra)
    if GastoFixo.objects.exists():
        ultimas_data.append(GastoFixo.objects.latest('data').data)
    ultimo_update = max(ultimas_data) if ultimas_data else None

    # Ingredientes
    ingredientes_alerta = Ingrediente.objects.filter(quantidade_estoque__lte=F('quantidade_minima'))
    total_ingredientes = Ingrediente.objects.count()
    ingredientes_alerta_count = ingredientes_alerta.count()

    # Receitas
    total_receitas = Receita.objects.count()
    receitas_ativas = total_receitas  # Assumindo que todas as receitas são ativas por padrão

    # Fornadas
    total_fornadas = Fornada.objects.count()
    fornadas_hoje = Fornada.objects.filter(data_producao__date=date.today()).count()

    # Produtos
    total_produtos = Produto.objects.count()
    produtos_em_estoque = Produto.objects.filter(quantidade_estoque__gt=0).count()
    total_produtos_vendidos = Venda.objects.aggregate(total=Sum('quantidade_vendida'))['total'] or 0

    # Clientes
    total_clientes = Cliente.objects.count()
    clientes_ativos = total_clientes  # Assumindo que todos os clientes são ativos por padrão

    # Patrimônios
    total_patrimonios = Patrimonio.objects.annotate(
        valor_total=F('quantidade') * F('valor_unitario')
    ).aggregate(total=Sum('valor_total'))['total'] or 0
    patrimonios_ativos = Patrimonio.objects.count()  # Assumindo que todos os patrimônios são ativos por padrão

    # Insumos
    total_insumos = Insumo.objects.count()
    insumos_em_uso = total_insumos  # Assumindo que todos os insumos estão em uso por padrão

    context = {
        'saldo_caixa': saldo_caixa,
        'ultimo_update': ultimo_update,
        'ingredientes_alerta_count': ingredientes_alerta_count,
        'total_produtos_vendidos': total_produtos_vendidos,
        'total_ingredientes': total_ingredientes,
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
        'total_insumos': total_insumos,
        'insumos_em_uso': insumos_em_uso,
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