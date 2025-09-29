from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from decimal import Decimal
from datetime import datetime
from ingredientes.models import Ingrediente
import logging
from django.db.models import F

# Configuração de logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Gera e envia a lista de compras de estoque em baixa por e-mail todo domingo entre 18h e 20h.'

    def handle(self, *args, **options):
        # Verifica se é domingo entre 18h e 20h (fuso horário America/Sao_Paulo)
        now = datetime.now()
        if now.weekday() != 6 or now.hour < 18 or now.hour >= 20:  # 6 = Domingo
            logger.info(f"Execução ignorada: Não é domingo entre 18h e 20h. Hora atual: {now}")
            return

        # Busca ingredientes com estoque baixo
        ingredientes_alerta = Ingrediente.objects.filter(quantidade_estoque__lte=F('quantidade_minima'))

        if not ingredientes_alerta.exists():
            logger.info("Nenhum ingrediente com estoque baixo encontrado.")
            subject = "Lista de Compras - Nenhum Item em Baixa"
            message = "Não há ingredientes com estoque abaixo do mínimo para reposição."
            email = EmailMessage(
                subject,
                message,
                '@gmail.com',
                ['@gmail.com'],
            )
            email.send()
            return

        # Calcula quantidades e custos
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

        # Gera o PDF
        buffer = BytesIO()
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
        buffer.seek(0)

        # Envia o e-mail com o PDF anexado
        subject = "Lista de Compras - Estoque em Baixa"
        message = "Segue anexada a lista de compras com ingredientes em estoque baixo."
        email = EmailMessage(
            subject,
            message,
            'vitorlemos231@gmail.com',
            ['vitorlemosdev@gmail.com'],
        )
        email.attach('lista_compras.pdf', buffer.read(), 'application/pdf')
        try:
            email.send()
            logger.info("E-mail com lista de compras enviado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {e}")
        finally:
            buffer.close()