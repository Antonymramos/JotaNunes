from django.shortcuts import render, redirect, get_object_or_404
from .models import Fornada
from .forms import FornadaForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from receitas.models import Receita

@login_required
def listar_fornadas(request):
    fornadas = Fornada.objects.all()
    for fornada in fornadas:
        fornada.total_unidades = fornada.quantidade_produzida * (getattr(fornada.receita, 'rendimento', 0) if fornada.receita else 0)
    return render(request, 'fornadas/lista_fornadas.html', {'fornadas': fornadas, 'content_title': 'Lista de Fornadas'})

@login_required
def criar_fornada(request):
    if request.method == 'POST':
        form = FornadaForm(request.POST)
        if form.is_valid():
            try:
                instance = form.save()
                total_unidades = instance.quantidade_produzida * (getattr(instance.receita, 'rendimento', 0))
                messages.success(request, f"Fornada de {instance.receita.nome} criada com sucesso! {total_unidades} unidades adicionadas ao estoque de {instance.produto_gerado.nome if instance.produto_gerado else 'produto gerado'}.")
                return redirect('fornadas:lista_fornadas')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = FornadaForm()
    return render(request, 'fornadas/form_fornada.html', {'form': form, 'content_title': 'Criar Fornada'})

@login_required
def editar_fornada(request, pk):
    fornada = get_object_or_404(Fornada, pk=pk)
    if request.method == 'POST':
        form = FornadaForm(request.POST, instance=fornada)
        if form.is_valid():
            try:
                # Reverter o estoque anterior antes de salvar
                if fornada.produto_gerado:
                    quantidade_a_subtrair = fornada.quantidade_produzida * getattr(fornada.receita, 'rendimento', 0)
                    if fornada.produto_gerado.quantidade_estoque < quantidade_a_subtrair:
                        raise ValueError(f"Estoque insuficiente para {fornada.produto_gerado.nome}. Disponível: {fornada.produto_gerado.quantidade_estoque}, Necessário: {quantidade_a_subtrair}")
                    fornada.produto_gerado.quantidade_estoque -= quantidade_a_subtrair
                    fornada.produto_gerado.save()
                for item in fornada.receita.itens.all():
                    item.ingrediente.quantidade_estoque += item.peso_liquido * fornada.quantidade_produzida
                    item.ingrediente.save()

                # Salvar nova fornada
                instance = form.save()
                total_unidades = instance.quantidade_produzida * (getattr(instance.receita, 'rendimento', 0))
                messages.success(request, f"Fornada de {fornada.receita.nome} atualizada com sucesso! {total_unidades} unidades no estoque de {instance.produto_gerado.nome if instance.produto_gerado else 'produto gerado'}.")
                return redirect('fornadas:lista_fornadas')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = FornadaForm(instance=fornada)
    return render(request, 'fornadas/form_fornada.html', {'form': form, 'content_title': 'Editar Fornada'})

@login_required
def deletar_fornada(request, pk):
    fornada = get_object_or_404(Fornada, pk=pk)
    if request.method == 'POST':
        try:
            if fornada.produto_gerado:
                quantidade_a_subtrair = fornada.quantidade_produzida * getattr(fornada.receita, 'rendimento', 0)
                if fornada.produto_gerado.quantidade_estoque < quantidade_a_subtrair:
                    raise ValueError(f"Estoque insuficiente para {fornada.produto_gerado.nome}. Disponível: {fornada.produto_gerado.quantidade_estoque}, Necessário: {quantidade_a_subtrair}")
                fornada.produto_gerado.quantidade_estoque -= quantidade_a_subtrair
                fornada.produto_gerado.save()
            for item in fornada.receita.itens.all():
                item.ingrediente.quantidade_estoque += item.peso_liquido * fornada.quantidade_produzida
                item.ingrediente.save()
            fornada.delete()
            messages.success(request, f"Fornada de {fornada.receita.nome} deletada com sucesso! Estoque ajustado.")
            return redirect('fornadas:lista_fornadas')
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'fornadas/lista_fornadas.html', {'fornada': fornada, 'content_title': 'Confirmar Deleção'})
    return render(request, 'fornadas/lista_fornadas.html', {'fornada': fornada, 'content_title': 'Confirmar Deleção'})

def get_receita_quantidade(request, receita_id):
    try:
        receita = get_object_or_404(Receita, pk=receita_id)
        return JsonResponse({'quantidade_produzida': getattr(receita, 'rendimento', 0)})
    except Receita.DoesNotExist:
        return JsonResponse({'quantidade_produzida': 0}, status=404)