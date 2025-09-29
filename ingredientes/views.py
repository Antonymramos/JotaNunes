from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Ingrediente
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import F
from datetime import datetime
from decimal import Decimal
from .forms import IngredienteForm
from django.contrib import messages
from django.core.mail import send_mail
from reportlab.lib.units import cm

@login_required
def lista_ingredientes(request):
    ingredientes = Ingrediente.objects.all()
    ingredientes_alerta = Ingrediente.objects.filter(quantidade_estoque__lte=F('quantidade_minima'))
    return render(request, 'ingredientes/listar_ingredientes.html', {
        'ingredientes': ingredientes,
        'ingredientes_alerta': ingredientes_alerta,
        'content_title': 'Lista de Ingredientes',
    })

@login_required
def criar_ingrediente(request):
    if request.method == 'POST':
        form = IngredienteForm(request.POST)
        if form.is_valid():
            form.save()
            ingrediente = form.instance
            if ingrediente.em_alerta:
                messages.warning(request, f'Estoque baixo de {ingrediente.nome}! Quantidade: {ingrediente.quantidade_estoque} {ingrediente.unidade_medida}.')
            return redirect('ingredientes:lista_ingredientes')
    else:
        form = IngredienteForm()
    return render(request, 'ingredientes/form_ingrediente.html', {'form': form})
@login_required
def editar_ingrediente(request, pk):
    ingrediente = Ingrediente.objects.get(pk=pk)
    if request.method == 'POST':
        form = IngredienteForm(request.POST, instance=ingrediente)
        if form.is_valid():
            form.save()
            # Verificar alerta após salvar
            if ingrediente.em_alerta:
                messages.warning(request, f'Estoque baixo de {ingrediente.nome}! Quantidade: {ingrediente.quantidade_estoque} {ingrediente.unidade_medida}.')
            return redirect('ingredientes:lista_ingredientes')
    else:
        form = IngredienteForm(instance=ingrediente)
    return render(request, 'ingredientes/form_ingrediente.html', {'form': form})



@login_required
def gerar_lista_compras(request):
    ingredientes_alerta = Ingrediente.objects.filter(quantidade_estoque__lte=F('quantidade_minima'))

    nome_busca = request.GET.get('nome_busca', '')
    unidade_medida = request.GET.get('unidade_medida', '')
    custo_min = request.GET.get('custo_min', '')
    custo_max = request.GET.get('custo_max', '')

    if nome_busca:
        ingredientes_alerta = ingredientes_alerta.filter(nome__icontains=nome_busca)
    if unidade_medida:
        ingredientes_alerta = ingredientes_alerta.filter(unidade_medida=unidade_medida)
    if custo_min:
        ingredientes_alerta = ingredientes_alerta.filter(preco_unitario__gte=Decimal(custo_min))
    if custo_max:
        ingredientes_alerta = ingredientes_alerta.filter(preco_unitario__lte=Decimal(custo_max))

    ingredientes_com_calculo = []
    total_custo = Decimal('0.00')
    for ingrediente in ingredientes_alerta:
        quantidade_a_comprar = Decimal(str(ingrediente.quantidade_minima)) * Decimal('2')
        custo_estimado = (ingrediente.preco_unitario or Decimal('0.00')) * quantidade_a_comprar
        ingredientes_com_calculo.append({
            'ingrediente': ingrediente,
            'quantidade_a_comprar': quantidade_a_comprar,
            'custo_estimado': custo_estimado,
        })
        total_custo += custo_estimado

    if request.method == 'POST' and 'download_pdf' in request.POST:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="lista_compras.pdf"'
        doc = SimpleDocTemplate(response, pagesize=letter, topMargin=2*cm, leftMargin=1*cm, rightMargin=1*cm, bottomMargin=1*cm)
        elements = []

        styles = getSampleStyleSheet()
        title = Paragraph("Lista de Compras - ERP Padaria", styles['Title'])
        elements.append(title)
        generated_at = Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
        elements.append(generated_at)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Espaçamento adicional antes da tabela

        data = [['Ingrediente', 'Estoque Atual', 'Quantidade Mínima', 'Quantidade a Comprar', 'Custo Estimado']]
        for item in ingredientes_com_calculo:
            ingrediente = item['ingrediente']
            data.append([
                Paragraph(ingrediente.nome, style=styles['Normal']),
                Paragraph(f"{ingrediente.quantidade_estoque} {ingrediente.unidade_medida}", style=styles['Normal']),
                Paragraph(f"{ingrediente.quantidade_minima} {ingrediente.unidade_medida}", style=styles['Normal']),
                Paragraph(f"{item['quantidade_a_comprar']} {ingrediente.unidade_medida}", style=styles['Normal']),
                Paragraph(f"R$ {item['custo_estimado']:.2f}", style=styles['Normal'])
            ])
        data.append(['', '', '', 'Total Estimado:', f"R$ {total_custo:.2f}"])

        # Ajuste das larguras das colunas para caber na página (total ~17 cm com margens de 1 cm de cada lado) Ajustar no servido -------------------------------
        table = Table(data, colWidths=[6*cm, 2.85*cm, 3.7*cm, 4*cm, 2.85*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 12),  # Padding superior para cabeçalhos
            ('BACKGROUND', (0, -1), (-2, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, -1), (-2, -1), colors.black),
            ('SPAN', (-1, -1), (-1, -1)),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 1), (0, -2), 'LEFT'),  # Alinhamento à esquerda para a coluna de ingredientes
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEADING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(table)

        doc.build(elements)
        return response

    return render(request, 'ingredientes/lista_compras.html', {
        'ingredientes_com_calculo': ingredientes_com_calculo,
        'total_custo': total_custo,
        'nome_busca': nome_busca,
        'unidade_medida': unidade_medida,
        'custo_min': custo_min,
        'custo_max': custo_max,
        'content_title': 'Lista de Compras',
    })

@login_required
def excluir_ingrediente(request, pk):
    ingrediente = get_object_or_404(Ingrediente, pk=pk)
    if request.method == 'POST':
        ingrediente.delete()
        messages.success(request, 'Ingrediente excluído com sucesso!')
        return redirect('ingredientes:lista_ingredientes')
    return render(request, 'ingredientes/listar_ingredientes.html', {
        'ingrediente': ingrediente,
        'content_title': f'Excluir {ingrediente.nome}',
    })

@login_required
def detalhar_ingrediente(request, id):
    ingrediente = get_object_or_404(Ingrediente, id=id)
    return render(request, 'ingredientes/detalhar_ingrediente.html', {
        'ingrediente': ingrediente,
        'content_title': f'Detalhes de {ingrediente.nome}',
    })
    
def test_email(request):
    send_mail(
        'Teste de E-mail Django',
        'Olá! Este é um teste de e-mail enviado pelo Django.',
        'vitorlemos231@gmail.com',  # Remetente
        ['vitorlemosdev@gmail.com'],  # Substitua pelo e-mail de destino
        fail_silently=False,
    )
    return HttpResponse('E-mail enviado! Verifique sua caixa de entrada.')