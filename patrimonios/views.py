from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Patrimonio
from .forms import PatrimonioForm
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime

def lista_patrimonios(request):
    patrimonios = Patrimonio.objects.all()
    return render(request, 'patrimonios/lista_patrimonios.html', {'patrimonios': patrimonios})

def criar_patrimonio(request):
    if request.method == 'POST':
        form = PatrimonioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Patrimônio criado com sucesso!")
            return redirect('patrimonios:lista_patrimonios')
    else:
        form = PatrimonioForm()
    return render(request, 'patrimonios/criar_patrimonio.html', {'form': form})

def detalhar_patrimonio(request, id):
    patrimonio = get_object_or_404(Patrimonio, id=id)
    content_title = f"Detalhes do Patrimônio: {patrimonio.nome}"
    return render(request, 'patrimonios/detalhar_patrimonio.html', {'patrimonio': patrimonio, 'content_title': content_title})

def editar_patrimonio(request, id):
    patrimonio = get_object_or_404(Patrimonio, id=id)
    if request.method == 'POST':
        form = PatrimonioForm(request.POST, instance=patrimonio)
        if form.is_valid():
            form.save()
            messages.success(request, "Patrimônio editado com sucesso!")
            return redirect('patrimonios:lista_patrimonios')
    else:
        form = PatrimonioForm(instance=patrimonio)
    return render(request, 'patrimonios/editar_patrimonio.html', {'form': form, 'patrimonio': patrimonio})

def excluir_patrimonio(request, id):
    patrimonio = get_object_or_404(Patrimonio, id=id)
    if request.method == 'POST':
        patrimonio.delete()
        messages.success(request, "Patrimônio deletado com sucesso!")
        return redirect('patrimonios:lista_patrimonios')
    return render(request, 'patrimonios/lista_patrimonios.html')

def gerar_relatorio_patrimonios(request):
    patrimonios = Patrimonio.objects.all()
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm, bottomMargin=2*cm)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.fontSize = 16
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    heading_style = styles['Heading3']
    heading_style.fontSize = 12
    
    # Title and metadata
    elements.append(Paragraph("Relatório de Patrimônios", title_style))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    elements.append(Spacer(1, 0.5*cm))
    
    if patrimonios:
        # Table data
        data = [['Nome', 'Valor Unitário (R$)', 'Valor Total (R$)', 'Condição']]
        for patrimonio in patrimonios:
            valor_total = patrimonio.quantidade * patrimonio.valor_unitario
            data.append([
                Paragraph(patrimonio.nome, normal_style),
                f"{patrimonio.valor_unitario:.2f}",
                f"{valor_total:.2f}",
                Paragraph(patrimonio.condicao, normal_style),
            ])
        
        # Table configuration (widths optimized for A4)
        col_widths = [8*cm, 3*cm, 3*cm, 4*cm]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left-align Nome
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),  # Left-align Condição
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEADING', (0, 0), (-1, -1), 10),
            ('WORDWRAP', (0, 1), (0, -1), 'CJK'),  # Enable word wrap for Nome
            ('WORDWRAP', (3, 1), (3, -1), 'CJK'),  # Enable word wrap for Condição
        ]))
        elements.append(table)
        
        # Summary
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph("<b>Resumo:</b>", heading_style))
        total_patrimonios = len(patrimonios)
        total_valor = sum(patrimonio.quantidade * patrimonio.valor_unitario for patrimonio in patrimonios)
        elements.append(Paragraph(f"Total de Patrimônios: {total_patrimonios}", normal_style))
        elements.append(Paragraph(f"Valor Total Estimado: R$ {total_valor:.2f}", normal_style))
    else:
        elements.append(Paragraph("Nenhum patrimônio cadastrado.", normal_style))
    
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_patrimonios.pdf"'
    return response