# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import User, Group, Permission
from .forms import UsuarioForm, CargoForm

@login_required
@permission_required('auth.add_user', raise_exception=True)
def criar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso.')
            return redirect('usuarios:listar_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/criar_usuario.html', {'form': form})

@login_required
@permission_required('auth.change_user', raise_exception=True)
def editar_usuario(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário editado com sucesso.')
            return redirect('usuarios:listar_usuarios')
    else:
        form = UsuarioForm(instance=user)
    return render(request, 'usuarios/editar_usuario.html', {'form': form})

@login_required
@permission_required('auth.view_user', raise_exception=True)
def listar_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})

@login_required
@permission_required('auth.delete_user', raise_exception=True)
def deletar_usuario(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Usuário deletado com sucesso.')
        return redirect('usuarios:listar_usuarios')
    return render(request, 'usuarios/confirmar_delecao.html', {'user': user})

@login_required
@permission_required('auth.add_group', raise_exception=True)
def criar_cargo(request):
    if request.method == 'POST':
        form = CargoForm(request.POST)
        if form.is_valid():
            group = Group.objects.create(name=form.cleaned_data['nome'])
            cargo = Cargo.objects.create(nome=form.cleaned_data['nome'], grupo=group)
            permissoes = form.cleaned_data['permissoes']
            group.permissions.set(permissoes)
            messages.success(request, 'Cargo criado com sucesso.')
            return redirect('usuarios:listar_cargos')
    else:
        form = CargoForm()
    return render(request, 'usuarios/criar_cargo.html', {'form': form})

@login_required
@permission_required('auth.view_group', raise_exception=True)
def listar_cargos(request):
    cargos = Cargo.objects.all()
    return render(request, 'usuarios/listar_cargos.html', {'cargos': cargos})
  
# usuarios/views.py (adicione esta função)
@login_required
@permission_required('auth.delete_group', raise_exception=True)
def deletar_cargo(request, pk):
    cargo = get_object_or_404(Cargo, pk=pk)
    if request.method == 'POST':
        cargo.grupo.delete()  # Deleta o grupo associado
        cargo.delete()
        messages.success(request, f'Cargo "{cargo.nome}" deletado com sucesso.')
        return redirect('usuarios:listar_cargos')
    return render(request, 'usuarios/confirmar_delecao.html', {'cargo': cargo, 'content_title': 'Confirmar Deleção de Cargo'})