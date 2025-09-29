from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Insumo
from .forms import InsumoForm

def lista_insumos(request):
    insumos = Insumo.objects.all()
    return render(request, 'insumos/lista_insumos.html', {'insumos': insumos})

def criar_insumo(request):
    if request.method == 'POST':
        form = InsumoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Insumo criado com sucesso!")
            return redirect('insumos:lista_insumos')
    else:
        form = InsumoForm()
    return render(request, 'insumos/criar_insumo.html', {'form': form})

def detalhar_insumo(request, id):
    insumo = get_object_or_404(Insumo, id=id)
    return render(request, 'insumos/detalhar_insumo.html', {'insumo': insumo})

def editar_insumo(request, id):
    insumo = get_object_or_404(Insumo, id=id)
    if request.method == 'POST':
        form = InsumoForm(request.POST, request.FILES, instance=insumo)
        if form.is_valid():
            form.save()
            messages.success(request, "Insumo editado com sucesso!")
            return redirect('insumos:lista_insumos')
    else:
        form = InsumoForm(instance=insumo)
    return render(request, 'insumos/editar_insumo.html', {'form': form})

def excluir_insumo(request, id):
    insumo = get_object_or_404(Insumo, id=id)
    if request.method == 'POST':
        insumo.delete()
        messages.success(request, "Insumo deletado com sucesso!")
        return redirect('insumos:lista_insumos')
    return render(request, 'insumos/lista_insumos.html')