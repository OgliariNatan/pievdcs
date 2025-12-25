from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from .permission_group import grupos_permitidos
from django.template.loader import render_to_string
from django.db.models import Func, F, Value, CharField
from ..forms.penal import TipoAtendimentoForm, ModeloPenalForm
from ..models.penal import tipo_atendimento, ModeloPenal
from sistema_justica.models.base import Agressor_dados
from mensageria.models import Notificacao, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
from usuarios.models import CustomUser
from django.contrib.auth.models import Group as CustomGroup
from django.utils import timezone
from datetime import timedelta

""" Configuraçao de decoradores para debug """
import os
from dotenv import load_dotenv

var_debug = os.getenv('DEBUG', False) #Carrega apenas a variavel de debug

if var_debug == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo, calcula_tempo_fun
    checked_debug_decorador = calcula_tempo
    checked_debug_decorador_fun = calcula_tempo_fun
    
else:
    checked_debug_decorador = None
    checked_debug_decorador_fun = None

""" Fim da configuraçao de decoradores para debug """

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Penal'])
def penal(request):

    notificacao_nao_lida = Notificacao.contar_nao_lidas_usuario(request.user)


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
    atendimentos = ModeloPenal.objects.filter(usuario=request.user).order_by('-id')
    grupos = []
    for atendimento in atendimentos:
        grupos.append({
            'id': atendimento.id,
            'nome': f'Atendimento {atendimento.id} - {atendimento.data_atendimento:%d/%m/%Y %H:%M}',
            'qtd_agressores': atendimento.agressores_atendidos.count(),
            'participantes': atendimento.agressores_atendidos.all(),
        })

    contexto = {
        'title': 'Polícia Penal',
        'description': 'This page provides information about the penal system.',
        'encaminhamentos': 5,
        'alert': notificacao_nao_lida,
        'qtd_atendimentos': atendimentos_mes,
        'qtd_atendimentos_anterior': atendimentos_mes_anterior,
        'variacao_atendimentos': variacao,
        'tipo_atendimentos': tipo_atendimento.objects.count(),
        'grupos': grupos,
        'user': request.user,
    }
    return render(request, "penal.html", contexto)



@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def cadastro_tipo_atendimento_form(request):
    form = TipoAtendimentoForm()
    return render(request, 'parcial/cadastro_tipo_atendimento_form.html', {'form': form})

@checked_debug_decorador
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

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def cadastro_atendimento_penal_form(request):
    form = ModeloPenalForm()
    return render(request, 'parcial/cadastro_atendimento_penal_form.html', {'form': form})

@checked_debug_decorador
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


@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def buscar_atendimentos_por_cpf_ajax(request):
    """Busca quantidade de atendimentos por CPF via AJAX"""
    #print("Buscando atendimentos por CPF via AJAX...")
    cpf = request.GET.get('cpf', '').replace('.', '').replace('-', '').strip()
    if not cpf:
        return JsonResponse({'sucesso': False, 'erro': 'CPF não informado.'})
    
    try:
        # Remove pontos e traço do CPF no banco para comparar
        agressor = Agressor_dados.objects.annotate(
            cpf_limpo=Func(
                Func(
                    F('cpf'),
                    Value('.'),
                    Value(''),
                    function='replace'
                ),
                Value('-'),
                Value(''),
                function='replace',
                output_field=CharField()
            )
        ).get(cpf_limpo=cpf)
        
        # CORREÇÃO: Usar o relacionamento correto
        qtd = agressor.agressores_atendidos.count()
        
        return JsonResponse({
            'sucesso': True, 
            'qtd': qtd,
            'nome': agressor.nome,
            'cpf': agressor.cpf
        })
    except Agressor_dados.DoesNotExist:
        return JsonResponse({'sucesso': False, 'erro': 'CPF não encontrado.'})


@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def buscar_atendimentos_por_cpf_modal(request):
    """Busca atendimentos por CPF no modal"""
    print("Buscando atendimentos por CPF no modal...")
    resultado = ""
    
    if request.method == "POST":
        cpf = request.POST.get('cpf', '').replace('.', '').replace('-', '').strip()
        if not cpf:
            resultado = '<span class="text-red-600">CPF não informado.</span>'
        else:
            try:
                agressor = Agressor_dados.objects.annotate(
                    cpf_limpo=Func(
                        Func(
                            F('cpf'),
                            Value('.'),
                            Value(''),
                            function='replace'
                        ),
                        Value('-'),
                        Value(''),
                        function='replace',
                        output_field=CharField()
                    )
                ).get(cpf_limpo=cpf)
                
                # CORREÇÃO: Usar o relacionamento correto
                atendimentos = agressor.agressores_atendidos.all().order_by('-data_atendimento')
                qtd = atendimentos.count()
                
                if qtd > 0:
                    resultado = f'''
                    <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                        <span class="text-green-700 font-semibold">
                            Agressor: {agressor.nome}<br>
                            CPF: {agressor.cpf}<br>
                            Total de atendimentos: {qtd}
                        </span>
                        <div class="mt-2 text-sm text-green-600">
                            Último atendimento: {atendimentos.first().data_atendimento.strftime("%d/%m/%Y %H:%M")}
                        </div>
                    </div>
                    '''
                else:
                    resultado = f'''
                    <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <span class="text-yellow-700">
                            Agressor encontrado: {agressor.nome}<br>
                            CPF: {agressor.cpf}<br>
                            Nenhum atendimento registrado.
                        </span>
                    </div>
                    '''
                    
            except Agressor_dados.DoesNotExist:
                resultado = '<span class="text-red-600">CPF não encontrado na base de dados.</span>'
    
    html = render_to_string('parcial/modal_busca_cpf.html', {'resultado': resultado}, request)
    return HttpResponse(html)