from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import HttpResponse
from .permission_group import grupos_permitidos
from ..forms.penal import TipoAtendimentoForm, ModeloPenalForm
from ..models.penal import tipo_atendimento, ModeloPenal
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
# -*- coding: utf-8 -*-

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Penal'])
def penal(request):
    now = timezone.now()
    first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(seconds=1)

    # Atendimentos deste mês
    atendimentos_mes = ModeloPenal.objects.filter(
        usuario=request.user,
        data_atendimento__gte=first_day_this_month,
        data_atendimento__lte=now
    ).count()

    # Atendimentos do mês anterior
    atendimentos_mes_anterior = ModeloPenal.objects.filter(
        usuario=request.user,
        data_atendimento__gte=first_day_last_month,
        data_atendimento__lte=last_day_last_month
    ).count()

    # Cálculo da variação percentual
    if atendimentos_mes_anterior > 0:
        variacao = ((atendimentos_mes - atendimentos_mes_anterior) / atendimentos_mes_anterior) * 100
    else:
        variacao = 100 if atendimentos_mes > 0 else 0
    
    # Lista de atendimentos com participantes
    atendimentos = ModeloPenal.objects.filter(usuario=request.user).order_by('-data_atendimento')
    grupos = []
    for atendimento in atendimentos:
        grupos.append({
            'id': atendimento.id,
            'nome': f'Atendimento #{atendimento.id} - {atendimento.data_atendimento:%d/%m/%Y %H:%M}',
            'qtd_agressores': atendimento.agressores_atendidos.count(),
            'participantes': atendimento.agressores_atendidos.all(),
        })

    contexto = {
        'title': 'Policia Penal',
        'description': 'This page provides information about the penal system.',
        'encaminhamentos': 5,
        'alert': 2,
        'qtd_atendimentos': atendimentos_mes,
        'qtd_atendimentos_anterior': atendimentos_mes_anterior,
        'variacao_atendimentos': variacao,
        'tipo_atendimentos': tipo_atendimento.objects.count(),
        'grupos': grupos,
        'user': request.user,
    }
    return render(request, "penal.html", contexto)

@login_required(login_url=reverse_lazy('login'))
def cadastro_tipo_atendimento_form(request):
    form = TipoAtendimentoForm()
    return render(request, 'parcial/cadastro_tipo_atendimento_form.html', {'form': form})

@login_required(login_url=reverse_lazy('login'))
def cadastro_tipo_atendimento_submit(request):
    if request.method == 'POST':
        form = TipoAtendimentoForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("""
                <script>
                    exibirPopupSucesso('Tipo de atendimento cadastrado com sucesso!', 'sucesso');
                    setTimeout(() => {
                        document.querySelector('.fixed.inset-0').remove();
                    }, 500);
                </script>
            """)
        else:
            return render(request, 'parcial/cadastro_tipo_atendimento_form.html', {'form': form})
    return HttpResponse(status=405)

@login_required(login_url=reverse_lazy('login'))
def cadastro_atendimento_penal_form(request):
    form = ModeloPenalForm()
    return render(request, 'parcial/cadastro_atendimento_penal_form.html', {'form': form})

@login_required(login_url=reverse_lazy('login'))
def cadastro_atendimento_penal_submit(request):
    if request.method == 'POST':
        form = ModeloPenalForm(request.POST)
        if form.is_valid():
            atendimento = form.save(commit=False)
            atendimento.usuario = request.user
            atendimento.save()
            form.save_m2m()  # Salvar relações many-to-many
            return HttpResponse("""
                <script>
                    exibirPopupSucesso('Atendimento cadastrado com sucesso!', 'sucesso');
                    setTimeout(() => {
                        document.querySelector('.fixed.inset-0').remove();
                    }, 500);
                </script>
            """)
        else:
            return render(request, 'parcial/cadastro_atendimento_penal_form.html', {'form': form})
    return HttpResponse(status=405)