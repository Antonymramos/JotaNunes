from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cliente, Endereco
from .forms import ClienteForm, EnderecoForm, FiltroClienteForm
from django.utils import timezone
from django.forms import modelformset_factory

@login_required
def cadastrar_cliente(request):
    EnderecoFormSet = modelformset_factory(Endereco, form=EnderecoForm, extra=1, can_delete=True)
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        formset = EnderecoFormSet(request.POST, queryset=Endereco.objects.none())
        if form.is_valid() and formset.is_valid():
            cliente = form.save(commit=False)
            cliente.ultimo_contato = timezone.now()
            cliente.save()
            for endereco_form in formset:
                if endereco_form.cleaned_data and not endereco_form.cleaned_data.get('DELETE', False):
                    endereco = endereco_form.save(commit=False)
                    endereco.cliente = cliente
                    endereco.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('clientes:cadastrar_cliente')
    else:
        form = ClienteForm()
        formset = EnderecoFormSet(queryset=Endereco.objects.none())
    return render(request, 'clientes/cadastrar_cliente.html', {
        'form': form,
        'formset': formset,
        'content_title': 'Cadastrar Cliente',
        'intolerancias_comuns': ['Glúten', 'Lactose', 'Amendoim', 'Nozes', 'Ovos'],
    })

@login_required
def listar_clientes(request):
    form = FiltroClienteForm(request.GET or None)
    clientes = Cliente.objects.all()
    if form.is_valid():
        status = form.cleaned_data.get('status')
        if status == 'ativo':
            clientes = clientes.filter(ativo=True)
        elif status == 'inativo':
            clientes = clientes.filter(ativo=False)
    context = {
        'clientes': clientes,
        'content_title': 'Lista de Clientes',
        'filtro_form': form,
    }
    return render(request, 'clientes/listar_clientes.html', context)

@login_required
def visualizar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    numero_limpo = ''.join(filter(str.isdigit, str(cliente.numero or '')))
    endereco_principal = cliente.get_endereco_principal()  # Usa o método do modelo
    context = {
        'cliente': cliente,
        'numero_limpo': numero_limpo,
        'endereco_principal': endereco_principal,  # Adiciona o endereço principal ao contexto
        'content_title': 'Visualizar Cliente',
    }
    return render(request, 'clientes/visualizar_cliente.html', context)

@login_required
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    EnderecoFormSet = modelformset_factory(Endereco, form=EnderecoForm, extra=1, can_delete=True)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        formset = EnderecoFormSet(request.POST, queryset=cliente.enderecos.all())
        if form.is_valid() and formset.is_valid():
            form.save()
            for endereco_form in formset:
                if endereco_form.cleaned_data:
                    if endereco_form.cleaned_data.get('DELETE', False):
                        if endereco_form.instance.pk:
                            endereco_form.instance.delete()
                    else:
                        endereco = endereco_form.save(commit=False)
                        endereco.cliente = cliente
                        endereco.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('clientes:visualizar_cliente', id=cliente.id)
    else:
        form = ClienteForm(instance=cliente)
        formset = EnderecoFormSet(queryset=cliente.enderecos.all())
    return render(request, 'clientes/editar_cliente.html', {
        'form': form,
        'formset': formset,
        'content_title': 'Editar Cliente',
        'intolerancias_comuns': ['Glúten', 'Lactose', 'Amendoim', 'Nozes', 'Ovos'],
    })

@login_required
def excluir_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente excluído com sucesso!')
        return redirect('clientes:listar_clientes')
    return redirect('clientes:listar_clientes')