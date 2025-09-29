from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.functions import TruncDate
from decimal import Decimal
from .models import Venda, Compra, Gasto, VendaItem, FORMAS_PAGAMENTO
from .forms import VendaForm, CompraForm, GastoForm, VendaItemFormSet
from clientes.models import Cliente
from produtos.models import Produto

@login_required
def dashboard_financeiro(request):
    # Ajuste para o fuso horário local (-03)
    hoje = timezone.localtime(timezone.now()).date()

    # Cálculos financeiros
    total_vendas = Venda.objects.aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')
    total_compras = Compra.objects.aggregate(total=Sum(F('quantidade_comprada') * F('valor_unitario')))['total'] or Decimal('0.00')
    total_gastos = Gasto.objects.aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
    saldo_caixa = float(total_vendas - (total_compras + total_gastos))  # Convertido para float

    # Entradas e saídas do dia (usando intervalo aware para corrigir timezone)
    hoje_local = timezone.localtime(timezone.now())
    inicio_do_dia = timezone.make_aware(timezone.datetime.combine(hoje_local.date(), timezone.datetime.min.time()), timezone.get_current_timezone())
    fim_do_dia = timezone.make_aware(timezone.datetime.combine(hoje_local.date(), timezone.datetime.max.time()), timezone.get_current_timezone())

    entradas_dia = Venda.objects.filter(data_venda__range=(inicio_do_dia, fim_do_dia)).aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')
    saidas_dia = (Compra.objects.filter(data_compra__range=(inicio_do_dia, fim_do_dia)).aggregate(total=Sum(F('quantidade_comprada') * F('valor_unitario')))['total'] or Decimal('0.00')) + (Gasto.objects.filter(data__range=(inicio_do_dia, fim_do_dia)).aggregate(total=Sum('valor'))['total'] or Decimal('0.00'))
    saldo_dia = float(entradas_dia - saidas_dia)  # Convertido para float

    # Resumo de total vendido por categoria de pagamento (corrigido para dia atual)
    pagamentos_resumo = list(Venda.objects.filter(data_venda__range=(inicio_do_dia, fim_do_dia)).values('forma_pagamento').annotate(total=Sum('valor_total')).order_by('forma_pagamento'))
    for p in pagamentos_resumo:
        p['forma_pagamento_display'] = dict(FORMAS_PAGAMENTO).get(p['forma_pagamento'], p['forma_pagamento'] or 'Desconhecido')
        p['total'] = float(p['total'] or 0)  # Convertido para float

    # Tendência de saldo e gastos (7 dias) - CORRIGIDO PARA GRÁFICOS
    ultimos_7_dias = hoje_local - timezone.timedelta(days=6)
    local_tz = timezone.get_current_timezone()

    saldo_diario = []
    gastos_diarios = []
    data_atual = ultimos_7_dias.replace(hour=0, minute=0, second=0, microsecond=0)

    for _ in range(7):
        inicio_dia = timezone.make_aware(timezone.datetime.combine(data_atual.date(), timezone.datetime.min.time()), local_tz)
        fim_dia = timezone.make_aware(timezone.datetime.combine(data_atual.date(), timezone.datetime.max.time()), local_tz)
        
        vendas_dia_qs = Venda.objects.filter(data_venda__range=(inicio_dia, fim_dia)).aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')
        compras_dia_qs = Compra.objects.filter(data_compra__range=(inicio_dia, fim_dia)).aggregate(total=Sum(F('quantidade_comprada') * F('valor_unitario')))['total'] or Decimal('0.00')
        gastos_dia_qs = Gasto.objects.filter(data__range=(inicio_dia, fim_dia)).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        saldo_dia_calc = float(vendas_dia_qs - compras_dia_qs - gastos_dia_qs)  # Convertido para float
        gasto_dia_calc = float(gastos_dia_qs)  # Convertido para float
        
        saldo_diario.append({'data': data_atual.strftime('%d/%m'), 'saldo': saldo_dia_calc})
        gastos_diarios.append({'data': data_atual.strftime('%d/%m'), 'gasto': gasto_dia_calc})
        
        data_atual += timezone.timedelta(days=1)

    # Depuração aprimorada
    print(f"Data Atual (Local): {hoje}")
    print(f"Depuração do Gráfico: Total Vendas: {total_vendas}, Total Compras: {total_compras}, Total Gastos: {total_gastos}")
    print(f"Entradas Dia: {entradas_dia}, Saídas Dia: {saidas_dia}, Saldo Dia: {saldo_dia}")
    print(f"Pagamentos Resumo: {pagamentos_resumo}")
    print(f"Saldo Diário Corrigido: {saldo_diario}")
    print(f"Gastos Diários Corrigido: {gastos_diarios}")

    # Tendência comparativa com ontem
    ontem = hoje - timezone.timedelta(days=1)
    vendas_ontem = Venda.objects.filter(data_venda__date=ontem).aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')
    compras_ontem = Compra.objects.filter(data_compra__date=ontem).aggregate(total=Sum(F('quantidade_comprada') * F('valor_unitario')))['total'] or Decimal('0.00')
    gastos_ontem = Gasto.objects.filter(data__date=ontem).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
    saldo_ontem = float(vendas_ontem - (compras_ontem + gastos_ontem))  # Convertido para float
    tendencia_saldo = "up" if saldo_caixa > saldo_ontem else "down" if saldo_caixa < saldo_ontem else "stable"

    # Dados para tabelas
    compras = Compra.objects.all().order_by('-data_compra')[:5]
    compras_com_totais = [
        {
            'ingrediente': compra.ingrediente.nome,
            'quantidade': compra.quantidade_comprada,
            'valor_unitario': compra.valor_unitario,
            'total': float(compra.quantidade_comprada * compra.valor_unitario),  # Convertido para float
            'data': compra.data_compra,
            'pk': compra.pk
        }
        for compra in compras
    ]
    gastos = Gasto.objects.all().order_by('-data')[:5]

    context = {
        'total_vendas': float(total_vendas),  # Convertido para float
        'total_compras': float(total_compras),  # Convertido para float
        'total_gastos': float(total_gastos),  # Convertido para float
        'saldo_caixa': saldo_caixa,
        'compras_com_totais': compras_com_totais,
        'gastos': gastos,
        'tendencia_saldo': tendencia_saldo,
        'saldo_diario': saldo_diario,
        'gastos_diarios': gastos_diarios,
        'entradas_dia': float(entradas_dia),  # Convertido para float
        'saidas_dia': float(saidas_dia),  # Convertido para float
        'saldo_dia': saldo_dia,
        'pagamentos_resumo': pagamentos_resumo,
    }
    return render(request, 'financeiro/dashboard.html', context)

@login_required
def criar_venda(request):
    if request.method == 'POST':
        form = VendaForm(request.POST)
        formset = VendaItemFormSet(request.POST, prefix='items')
        if form.is_valid() and formset.is_valid():
            try:
                print("Dados enviados no POST:", dict(request.POST))  # Depuração
                print("Dados do formulário:", form.cleaned_data)  # Depuração
                print("Dados do formset:", [item.cleaned_data for item in formset if item.cleaned_data])  # Depuração
                
                # Salva a instância de Venda primeiro
                venda = form.save(commit=False)
                venda.save()  # Garante que a Venda tenha um pk
                print(f"Venda salva com pk: {venda.pk}")  # Depuração

                # Processa os itens do formset
                for item_form in formset:
                    if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                        item = item_form.save(commit=False)
                        item.venda = venda  # Associa a Venda já salva
                        item.save()
                        print(f"Item salvo: {item}")  # Depuração

                # Calcula o valor total após salvar todos os itens
                venda.calculate_total()
                venda.save(update_fields=['valor_total'])
                
                messages.success(request, f'Venda registrada com sucesso!')
                return redirect('financeiro:dashboard_financeiro')
            except ValueError as e:
                print(f"Erro ao salvar venda: {str(e)}")  # Depuração
                messages.error(request, f"Erro ao registrar venda: {str(e)}")
        else:
            print(f"Formulário inválido. Erros form: {form.errors}, Erros formset: {formset.errors}")  # Depuração
            messages.error(request, 'Erro ao processar o formulário. Verifique os dados inseridos.')
    else:
        form = VendaForm()
        formset = VendaItemFormSet(queryset=VendaItem.objects.none(), prefix='items')
    return render(request, 'financeiro/form_venda.html', {'form': form, 'formset': formset})

@login_required
def criar_compra(request):
    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Compra cadastrada com sucesso!")
                return redirect('financeiro:dashboard_financeiro')
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Erro ao salvar a compra: {str(e)}")
    else:
        form = CompraForm()
    return render(request, 'financeiro/form_compra.html', {'form': form})

@login_required
def criar_gasto(request):
    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Gasto "{form.cleaned_data["descricao"]}" registrado!')
            return redirect('financeiro:dashboard_financeiro')
    else:
        form = GastoForm()
    return render(request, 'financeiro/form_gasto.html', {'form': form})

@login_required
def historico_transacoes(request):
    vendas = Venda.objects.all().order_by('-data_venda')
    compras = Compra.objects.all().order_by('-data_compra')

    vendas_com_totais = [
        {
            'id': venda.id,
            'cliente': venda.cliente.nome if venda.cliente else 'Anônimo',
            'data': venda.data_venda,
            'total': venda.valor_total,
            'forma_pagamento': venda.get_forma_pagamento_display(),  # Adicionado
            'desconto': venda.desconto,  # Adicionado
            'items': [
                {
                    'produto': item.produto.nome,
                    'quantidade': item.quantidade,
                    'valor_unitario': item.produto.preco_venda,
                    'subtotal': item.subtotal
                } for item in venda.items.all()
            ]
        }
        for venda in vendas
    ]
    compras_com_totais = [
        {
            'ingrediente': compra.ingrediente.nome,
            'quantidade': compra.quantidade_comprada,
            'valor_unitario': compra.valor_unitario,
            'total': compra.quantidade_comprada * compra.valor_unitario,
            'data': compra.data_compra,
            'pk': compra.pk
        }
        for compra in compras
    ]

    # Calcular totais
    total_vendas = sum(venda['total'] for venda in vendas_com_totais) if vendas_com_totais else Decimal('0.00')
    total_compras = sum(compra['total'] for compra in compras_com_totais) if compras_com_totais else Decimal('0.00')

    return render(request, 'financeiro/historico_transacoes.html', {
        'vendas': vendas_com_totais,
        'compras': compras_com_totais,
        'total_vendas': total_vendas,
        'total_compras': total_compras,
    })
    
@login_required
def editar_gasto(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == 'POST':
        form = GastoForm(request.POST, instance=gasto)
        if form.is_valid():
            form.save()
            messages.success(request, f"Gasto '{gasto.descricao}' atualizado com sucesso!")
            return redirect('financeiro:dashboard_financeiro')
    else:
        form = GastoForm(instance=gasto)
    return render(request, 'financeiro/form_gasto.html', {'form': form, 'gasto': gasto})

@login_required
def deletar_gasto(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == 'POST':
        gasto.delete()
        messages.success(request, f"Gasto '{gasto.descricao}' deletado com sucesso!")
        return redirect('financeiro:dashboard_financeiro')
    return render(request, 'financeiro/confirmar_delecao.html', {'gasto': gasto})

@login_required
def detalhes_compra(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    context = {
        'compra': compra,
        'valor_total': compra.quantidade_comprada * compra.valor_unitario,
    }
    return render(request, 'financeiro/detalhes_compra.html', context)

@login_required
def detalhes_venda(request, pk):
    venda = get_object_or_404(Venda, pk=pk)
    context = {
        'venda': venda,
        'items': venda.items.all(),
        'total': venda.valor_total,
    }
    return render(request, 'financeiro/detalhes_venda.html', context)