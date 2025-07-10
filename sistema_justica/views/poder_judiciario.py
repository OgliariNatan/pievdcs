# -*- coding: utf-8 -*-
import openai
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from ..forms.cadastros import CadastroVitimaForm, CadastroAgressorForm, CadastroMunicipioForm
from ..models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio, Estado
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string



@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Poder Judiciário',])
def poder_judiciario(request):
    contexto = {
        'title': 'Poder Judiciário',
        'description': 'This page provides information about the judicial power.',
        'encaminhamentos': 5,
        'notificacoes': 4,
        'user': request.user,

    }
    return render(request, "judiciario_IA.html", contexto)

@login_required(login_url=reverse_lazy('login'))
def cadastro_vitima_form(request):
    form = CadastroVitimaForm()
    return render(request, 'parcial/cadastro_vitima_form.html', {'form': form})

@login_required(login_url=reverse_lazy('login'))
def cadastro_vitima_submit(request):
    if request.method == 'POST':
        form = CadastroVitimaForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(
                """
                    <script>
                        exibirPopupSucesso('Vítima cadastrada com sucesso!', 'feminino');
                        document.getElementById('modal-vitima').innerHTML = '';
                    </script>
                """
            )
    else:
        return render(request, "parcial/cadastro_vitima_form.html", {"form": form})
    return HttpResponse(status=405)

@login_required(login_url=reverse_lazy('login'))
def cadastro_agressor_form(request):
    form = CadastroAgressorForm()
    return render(request, 'parcial/cadastro_agressor_form.html', {'form': form})

@login_required(login_url=reverse_lazy('login'))
def cadastro_agressor_submit(request):
    if request.method == 'POST':
        form = CadastroAgressorForm(request.POST)
        if form.is_valid():
            agressor = form.save()
            # Retorne um script para fechar o modal e recarregar o campo agressor do formulário de vítima
            return HttpResponse(
                """
                    <script>
                        exibirPopupSucesso('Agressor cadastrado com sucesso!', 'masculino');
                        document.getElementById('modal-agressor').innerHTML = '';
                        htmx.trigger(htmx.find('#id_agressor'), 'change');
                    </script>
                """
            )
        else:
            return render(request, 'parcial/cadastro_agressor_form.html', {'form': form})
    return HttpResponse(status=405)

@login_required(login_url=reverse_lazy('login'))
def cadastro_municipio_form(request):
    form = CadastroMunicipioForm()
    return render(request, 'parcial/cadastro_municipio_form.html', {'form': form})

@login_required(login_url=reverse_lazy('login'))
def cadastro_municipio_submit(request):
    if request.method == 'POST':
        form = CadastroMunicipioForm(request.POST)
        if form.is_valid():
            municipio = form.save()
            return HttpResponse("""
                <script>
                    document.getElementById('modal-municipio').innerHTML = '';
                    // Opcional: recarregar o campo municipio via HTMX
                    htmx.trigger(htmx.find('#id_municipio'), 'change');
                </script>
                <div class="alert alert-success">Município cadastrado com sucesso! Selecione-o na lista.</div>
            """)
        else:
            return render(request, 'parcial/cadastro_municipio_form.html', {'form': form})
    return HttpResponse(status=405)


@csrf_exempt
def chat_ia(request):
    if request.method == "POST":
        msg = request.POST.get("mensagem", "")
        resposta = f"Simulação de resposta jurídica para: '{msg}'"
        html = f"""
        <div class='flex justify-end'>
            <div class='bg-purple-600 text-white rounded-xl p-3 max-w-xs'>{msg}</div>
        </div>
        <div class='flex items-start gap-2'>
            <div class='w-7 h-7 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center'>
                <i class='fas fa-robot text-xs'></i>
            </div>
            <div class='bg-gray-100 rounded-xl p-3 max-w-xs'>{resposta}</div>
        </div>
        """
        return HttpResponse(html)
    
