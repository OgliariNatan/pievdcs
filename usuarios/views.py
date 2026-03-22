# -*- coding: utf-8 -*-
"""
dir: usuarios/views.py
Views de configuração da conta do usuário.
"""
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .forms import ContaArquivosForm, ContaDadosForm, ContaSenhaForm


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
        form.save()
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
        usuario = form.save()
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
        form.save()
        return render(request, 'popup_arquivos.html', {
            'form': ContaArquivosForm(instance=request.user),
            'popup_id': 'popup-conta-arquivos',
            'sucesso': True,
        })

    return render(request, 'popup_arquivos.html', {
        'form': form,
        'popup_id': 'popup-conta-arquivos',
    }, status=400)