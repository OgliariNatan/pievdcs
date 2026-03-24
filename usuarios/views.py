# -*- coding: utf-8 -*-
"""
dir: usuarios/views.py
Views de configuração da conta do usuário.
"""
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .forms import ContaArquivosForm, ContaDadosForm, ContaSenhaForm, CriarUsuarioForm
from .models import CustomUser


@login_required
def config_conta(request):
    """Exibe a página principal de configuração da conta."""
    return render(request, 'config_conta.html', {
        'title': 'Configurações da Conta',
        'description': 'Atualize dados cadastrais, senha e arquivos do usuário.',
    })


@login_required
def config_conta_dados_popup(request):
    """Exibe popup para edição dos dados cadastrais."""
    form = ContaDadosForm(instance=request.user)
    return render(request, 'popup_editar_dados.html', {
        'form': form,
        'popup_id': 'popup-conta-dados',
    })


@login_required
def config_conta_dados_submit(request):
    """Processa a atualização dos dados cadastrais."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    form = ContaDadosForm(request.POST, instance=request.user)

    if form.is_valid():
        usuario = form.save(commit=False)
        usuario.ultima_atualizacao_conta = timezone.now()
        usuario.save()
        return render(request, 'popup_editar_dados.html', {
            'form': ContaDadosForm(instance=request.user),
            'popup_id': 'popup-conta-dados',
            'sucesso': True,
        })

    return render(request, 'popup_editar_dados.html', {
        'form': form,
        'popup_id': 'popup-conta-dados',
    }, status=400)


@login_required
def config_conta_senha_popup(request):
    """Exibe popup para alteração de senha."""
    form = ContaSenhaForm(user=request.user)
    return render(request, 'popup_alterar_senha.html', {
        'form': form,
        'popup_id': 'popup-conta-senha',
    })


@login_required
def config_conta_senha_submit(request):
    """Processa a alteração de senha."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    form = ContaSenhaForm(user=request.user, data=request.POST)

    if form.is_valid():
        usuario = form.save(commit=False)
        usuario.ultima_atualizacao_conta = timezone.now()
        usuario.save()        
        update_session_auth_hash(request, usuario)

        return render(request, 'popup_alterar_senha.html', {
            'form': ContaSenhaForm(user=request.user),
            'popup_id': 'popup-conta-senha',
            'sucesso': True,
        })

    return render(request, 'popup_alterar_senha.html', {
        'form': form,
        'popup_id': 'popup-conta-senha',
    }, status=400)


@login_required
def config_conta_arquivos_popup(request):
    """Exibe popup para atualização dos arquivos do usuário."""
    form = ContaArquivosForm(instance=request.user)
    return render(request, 'popup_arquivos.html', {
        'form': form,
        'popup_id': 'popup-conta-arquivos',
    })


@login_required
def config_conta_arquivos_submit(request):
    """Processa a atualização da foto e do comprovante."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    form = ContaArquivosForm(request.POST, request.FILES, instance=request.user)

    if form.is_valid():
        usuario = form.save(commit=False)
        usuario.ultima_atualizacao_conta = timezone.now()
        usuario.save()
        return render(request, 'popup_arquivos.html', {
            'form': ContaArquivosForm(instance=request.user),
            'popup_id': 'popup-conta-arquivos',
            'sucesso': True,
        })

    return render(request, 'popup_arquivos.html', {
        'form': form,
        'popup_id': 'popup-conta-arquivos',
    }, status=400)

    

# ============================================================
# HELPERS — Gestão de usuários
# ============================================================    


def _pode_gerenciar(user):
    """Verifica se o usuário tem acesso à gestão de usuários."""
    return user.is_superuser or user.groups.filter(name='Administração').exists()


def _grupos_gerenciaveis(user):
    """
    Retorna os grupos que o usuário pode administrar.
    Superusuário: todos os seus grupos.
    Admin comum: seus grupos, exceto 'Administração'.
    """
    if user.is_superuser:
        return user.groups.all()
    return user.groups.exclude(name='Administração')


# ============================================================
# VIEWS — Gestão de usuários
# ============================================================
@login_required
def config_conta_gestao(request):
    """Seção de gestão de usuários — carregada via HTMX."""
    if not _pode_gerenciar(request.user):
        return HttpResponse(status=403)

    grupos = _grupos_gerenciaveis(request.user).prefetch_related('user_set')
    return render(request, 'secao_gestao_usuarios.html', {'grupos': grupos})


@login_required
def config_conta_gestao_buscar(request):
    """Busca usuário por nome, username ou CPF para associar a um grupo."""
    if not _pode_gerenciar(request.user):
        return HttpResponse(status=403)

    grupo_id = request.GET.get('grupo_id')
    grupo = get_object_or_404(Group, pk=grupo_id)

    # Segurança: grupo precisa ser gerenciável pelo usuário logado
    if grupo not in _grupos_gerenciaveis(request.user):
        return HttpResponse(status=403)

    q = request.GET.get('q', '').strip()
    usuarios = CustomUser.objects.none()

    if q:
        usuarios = (
            CustomUser.objects
            .filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(username__icontains=q) |
                Q(cpf__icontains=q)
            )
            .exclude(groups=grupo)   # não mostra quem já está no grupo
            .distinct()
            .only('pk', 'first_name', 'last_name', 'username', 'cpf')
            [:15]
        )

    return render(request, 'resultado_busca_usuario.html', {
        'usuarios': usuarios,
        'grupo': grupo,
        'q': q,
    })


@login_required
def config_conta_gestao_adicionar(request):
    """Adiciona um usuário existente a um grupo gerenciável."""
    if request.method != 'POST':
        return HttpResponse(status=405)
    if not _pode_gerenciar(request.user):
        return HttpResponse(status=403)

    grupo = get_object_or_404(Group, pk=request.POST.get('grupo_id'))
    if grupo not in _grupos_gerenciaveis(request.user):
        return HttpResponse(status=403)

    usuario = get_object_or_404(CustomUser, pk=request.POST.get('usuario_id'))
    usuario.groups.add(grupo)

    grupo.refresh_from_db()
    return render(request, '_membros_grupo.html', {'grupo': grupo})


@login_required
def config_conta_gestao_remover(request):
    """Remove um usuário de um grupo gerenciável."""
    if request.method != 'POST':
        return HttpResponse(status=405)
    if not _pode_gerenciar(request.user):
        return HttpResponse(status=403)

    grupo = get_object_or_404(Group, pk=request.POST.get('grupo_id'))
    if grupo not in _grupos_gerenciaveis(request.user):
        return HttpResponse(status=403)

    usuario = get_object_or_404(CustomUser, pk=request.POST.get('usuario_id'))

    # Impede que o usuário remova a si mesmo
    if usuario.pk == request.user.pk:
        return HttpResponse('<p class="text-red-500 px-4 py-2 text-sm">Você não pode remover a si mesmo.</p>', status=400)

    usuario.groups.remove(grupo)

    grupo.refresh_from_db()
    return render(request, '_membros_grupo.html', {'grupo': grupo})


@login_required
def config_conta_gestao_criar_popup(request):
    """Popup para criar novo usuário."""
    if not _pode_gerenciar(request.user):
        return HttpResponse(status=403)

    grupos_disponiveis = _grupos_gerenciaveis(request.user)
    grupo_id = request.GET.get('grupo_id')

    form = CriarUsuarioForm(grupos_disponiveis=grupos_disponiveis)

    # Pré-seleciona o grupo caso venha via querystring
    if grupo_id:
        try:
            grupo_pre = grupos_disponiveis.get(pk=grupo_id)
            form.fields['grupo'].initial = grupo_pre
        except Group.DoesNotExist:
            pass

    return render(request, 'popup_criar_usuario.html', {
        'form': form,
        'popup_id': 'popup-criar-usuario',
    })


@login_required
def config_conta_gestao_criar_submit(request):
    """Cria novo usuário e associa ao grupo selecionado."""
    if request.method != 'POST':
        return HttpResponse(status=405)
    if not _pode_gerenciar(request.user):
        return HttpResponse(status=403)

    grupos_disponiveis = _grupos_gerenciaveis(request.user)
    form = CriarUsuarioForm(request.POST, grupos_disponiveis=grupos_disponiveis)

    if form.is_valid():
        novo_usuario = form.save(commit=False)
        novo_usuario.save()
        novo_usuario.groups.add(form.cleaned_data['grupo'])

        # Sucesso: re-renderiza a seção inteira (fecha popup implicitamente)
        grupos = grupos_disponiveis.prefetch_related('user_set')
        return render(request, 'secao_gestao_usuarios.html', {
            'grupos': grupos,
            'sucesso_criacao': form.cleaned_data['grupo'].name,
        })

    # Erro: retorna o popup com os erros (retargeting via header HTMX)
    response = render(request, 'popup_criar_usuario.html', {
        'form': form,
        'popup_id': 'popup-criar-usuario',
    }, status=400)
    response['HX-Retarget'] = '#modal-gestao'
    response['HX-Reswap'] = 'innerHTML'
    return response