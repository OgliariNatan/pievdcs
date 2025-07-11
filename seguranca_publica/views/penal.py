from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import HttpResponse
from .permission_group import grupos_permitidos
from ..forms.penal import TipoAtendimentoForm, ModeloPenalForm
from ..models.penal import tipo_atendimento, ModeloPenal
from django.contrib import messages

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Penal'])
def penal(request):
    contexto = {
        'title': 'Policia Penal',
        'description': 'This page provides information about the penal system.',
        'encaminhamentos': 5,
        'alert': 2,
        'user' : request.user,
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