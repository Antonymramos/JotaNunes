# ingredientes/tasks.py
from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from .models import Ingrediente
from django.db.models import F
from decimal import Decimal
from datetime import datetime
import io

@shared_task
def enviar_lista_compras(destinatario):
    ingredientes_alerta = Ingrediente.objects.filter(quantidade_estoque__lte=F('quantidade_minima'))

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

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Lista de Compras - ERP Padaria", styles['Title'])
    elements.append(title)
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))

    data = [['Ingrediente', 'Estoque Atual', 'Quantidade Mínima', 'Quantidade a Comprar', 'Custo Estimado']]
    for item in ingredientes_com_calculo:
        ingrediente = item['ingrediente']
        data.append([
            ingrediente.nome,
            f"{ingrediente.quantidade_estoque} {ingrediente.unidade_medida}",
            f"{ingrediente.quantidade_minima} {ingrediente.unidade_medida}",
            f"{item['quantidade_a_comprar']} {ingrediente.unidade_medida}",
            f"R$ {item['custo_estimado']:.2f}"
        ])
    data.append(['', '', '', 'Total Estimado:', f"R$ {total_custo:.2f}"])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-2, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, -1), (-2, -1), colors.black),
        ('SPAN', (-1, -1), (-1, -1)),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    subject = 'Lista de Compras Semanal - ERP Padaria'
    body = f"Olá,\n\nSegue anexada a lista de compras semanal gerada pelo ERP Padaria.\nTotal estimado: R$ {total_custo:.2f}.\n\nAtenciosamente,\nEquipe ERP Padaria"
    email = EmailMessage(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [destinatario],
    )
    email.attach('lista_compras.pdf', pdf, 'application/pdf')
    email.send()

    return "E-mail enviado com sucesso!"