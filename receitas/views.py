from io import BytesIO
from datetime import datetime
import logging

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.html import strip_tags

from .models import Receita, ItemReceita
from .forms import ReceitaForm, ItemReceitaFormSet
from fornadas.models import Fornada

logger = logging.getLogger(__name__)

@login_required
def listar_receitas(request):
    receitas = Receita.objects.all()
    logger.debug("Listando todas as receitas")
    return render(request, 'receitas/listar_receitas.html', {'receitas': receitas})

@login_required
def detalhar_receita(request, pk):
    receita = get_object_or_404(Receita, pk=pk)
    fornadas = Fornada.objects.filter(receita=receita)
    itens_com_custo = receita.itens.all().select_related('ingrediente')
    total_insumos = receita.custo_total or 0
    logger.debug("Detalhando receita %s com %d itens", receita.nome, itens_com_custo.count())
    return render(request, 'receitas/detalhar_receita.html', {
        'content_title': f'Visualizar Receita: {receita.nome}',
        'receita': receita,
        'itens_com_custo': itens_com_custo,
        'total_insumos': total_insumos,
        'fornadas': fornadas,
    })

@login_required
def criar_receita(request):
    if request.method == 'POST':
        logger.debug("Processando POST para criar receita: %s", request.POST.get('nome'))
        form = ReceitaForm(request.POST, request.FILES)
        formset = ItemReceitaFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            receita = form.save()
            formset.instance = receita
            formset.save()
            messages.success(request, f'Receita "{receita.nome}" criada com sucesso!')
            logger.info("Receita criada: %s (ID: %d)", receita.nome, receita.pk)
            return redirect('receitas:detalhar_receita', pk=receita.pk)
        else:
            logger.error("Erros no formulário: %s", form.errors)
            logger.error("Erros no formset: %s", formset.errors)
            messages.error(request, "Não foi possível salvar a receita. Corrija os erros abaixo.")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {form[field].label}: {error}")
            for i, formset_form in enumerate(formset):
                for field, errors in formset_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Erro no item {i + 1} ({formset_form[field].label}): {error}")
    else:
        logger.debug("Carregando formulário para nova receita")
        form = ReceitaForm()
        formset = ItemReceitaFormSet()
    return render(request, 'receitas/form_receita.html', {
        'form': form,
        'formset': formset,
        'content_title': 'Criar Receita'
    })

@login_required
def editar_receita(request, pk):
    receita = get_object_or_404(Receita, pk=pk)
    if request.method == 'POST':
        logger.debug("Processando POST para editar receita %s: %s", pk, request.POST.get('nome'))
        form = ReceitaForm(request.POST, request.FILES, instance=receita)
        formset = ItemReceitaFormSet(request.POST, request.FILES, instance=receita)
        if form.is_valid() and formset.is_valid():
            receita = form.save()
            formset.instance = receita
            formset.save()
            messages.success(request, f'Receita "{receita.nome}" atualizada com sucesso!')
            logger.info("Receita editada: %s (ID: %d)", receita.nome, receita.pk)
            return redirect('receitas:detalhar_receita', pk=receita.pk)
        else:
            logger.error("Erros no formulário: %s", form.errors)
            logger.error("Erros no formset: %s", formset.errors)
            messages.error(request, "Não foi possível salvar a receita. Corrija os erros abaixo.")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {form[field].label}: {error}")
            for i, formset_form in enumerate(formset):
                for field, errors in formset_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Erro no item {i + 1} ({formset_form[field].label}): {error}")
    else:
        logger.debug("Carregando formulário para edição da receita %s", pk)
        form = ReceitaForm(instance=receita)
        formset = ItemReceitaFormSet(instance=receita)
        logger.debug("Formset inicializado com %d itens", formset.queryset.count())
    return render(request, 'receitas/editar_receita.html', {
        'form': form,
        'formset': formset,
        'content_title': f'Editar Receita: {receita.nome}',
        'receita': receita
    })

@login_required
def deletar_receita(request, pk):
    receita = get_object_or_404(Receita, pk=pk)
    if request.method == 'POST':
        nome = receita.nome
        receita.delete()
        messages.success(request, f'Receita "{nome}" deletada com sucesso!')
        logger.info("Receita deletada: %s (ID: %d)", nome, pk)
        return redirect('receitas:listar_receitas')
    return render(request, 'receitas/confirmar_delecao.html', {'receita': receita, 'content_title': 'Confirmar Deleção'})

@login_required
def gerar_relatorio_receita(request, pk):
    receita = get_object_or_404(Receita, pk=pk)
    itens_com_custo = receita.itens.all().select_related('ingrediente')
    total_insumos = receita.custo_total or 0
    logger.debug("Gerando relatório para receita %s", receita.nome)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2*cm, leftMargin=1*cm, rightMargin=1*cm, bottomMargin=1*cm)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph(f"Relatório da Receita: {receita.nome}", styles['Title'])
    elements.append(title)
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    data_receita = [
        ['Profissional', receita.profissional if receita.profissional else 'Não informado'],
        ['Rendimento', f"{receita.rendimento} porções"],
    ]
    table_receita = Table(data_receita, colWidths=[4*cm, 12*cm])
    table_receita.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEADING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(table_receita)

    modo_preparo_text = receita.modo_preparo if receita.modo_preparo else 'Não informado'
    modo_preparo_text = strip_tags(modo_preparo_text)
    max_length = 2000
    if len(modo_preparo_text) > max_length:
        modo_preparo_text = modo_preparo_text[:max_length] + "... (texto truncado)"
    modo_preparo_lines = modo_preparo_text.split('\n')
    elements.append(Paragraph("<b>Modo de Preparo:</b>", styles['Heading3']))
    for line in modo_preparo_lines:
        if line.strip():
            elements.append(Paragraph(line.strip(), style=styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    data_itens = [['Ingrediente', 'Unidade', 'Peso Bruto', 'Peso Líquido', 'Valor Unitário (R$)', 'Custo Total (R$)']]
    for item in itens_com_custo:
        custo_total_item = (item.peso_liquido or 0) * (item.valor_unitario or 0)
        data_itens.append([
            Paragraph(item.ingrediente.nome, styles['Normal']),
            item.unidade,
            f"{item.peso_bruto or 0:.3f} g" if item.peso_bruto else '0 g',
            f"{item.peso_liquido or 0:.3f} g" if item.peso_liquido else '0 g',
            f"{item.valor_unitario or 0:.2f}",
            f"{custo_total_item:.2f}",
        ])
    data_itens.append(['', '', '', '', 'Total Insumos:', f"R$ {total_insumos:.2f}"])
    table_itens = Table(data_itens, colWidths=[7*cm, 2*cm, 2.5*cm, 2.5*cm, 3.2*cm, 3.2*cm])
    table_itens.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-2, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, -1), (-2, -1), colors.black),
        ('SPAN', (-1, -1), (-1, -1)),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 1), (0, -2), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEADING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(table_itens)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_receita_{receita.nome}.pdf"'
    return response