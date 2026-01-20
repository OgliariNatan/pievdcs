#-- coding: utf-8 --
"""
    Modelos de visualizações do sistema Penal
    dir: seguranca_publica/views/penal.py
    @author: OgliariNatan
"""
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
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

var_debug = os.getenv('DEBUG', False) #Carrega apenas a variavel de debug

if var_debug == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo, calcula_tempo_fun
    checked_debug_decorador = calcula_tempo
    checked_debug_decorador_fun = calcula_tempo_fun
    
else:
    checked_debug_decorador = lambda x: x
    checked_debug_decorador_fun = lambda x: x

""" Fim da configuraçao de decoradores para debug """

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Penal'])
def penal(request):

    try:
        notificacao_nao_lida = Notificacao.contar_nao_lidas_usuario(request.user)
    except Exception as e:
        if var_debug == 'True':
            print(f'Tipo de erro:{type(e).__name__}')
            print(f"Erro ao contar notificações não lidas: {e}")
        notificacao_nao_lida = 0

    now = timezone.now()
    first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(seconds=1)

    # Atendimentos deste mês

    try:
        atendimentos_mes = ModeloPenal.objects.filter(
            usuario=request.user,
            data_atendimento__gte=first_day_this_month,
            data_atendimento__lte=now
        ).count()

        # Atendimentos do mês anterior
        atendimentos_mes_anterior = ModeloPenal.objects.filter(
            #usuario=request.user,
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
            
    except Exception as e:
        if var_debug == 'True':
            print(f'Tipo de erro:{type(e).__name__}')
            print(f"Erro ao buscar atendimentos: {e}")
        atendimentos_mes = 0
        atendimentos_mes_anterior = 0
        variacao = 0
        grupos = []

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


@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Penal'])
def mostra_todos_grupos_penal(request):
    """
        Mostra todos os grupos de atendimentos registrados no sistema Penal
        Viualização CRÍTICA.
    """
    if not request.user.has_perm('seguranca_publica.view_modelopenal'):
        raise ValueError("Usuário não tem permissão para visualizar os atendimentos penais.")

    grupos = ModeloPenal.objects.select_related(
        'usuario',
        'atendimento'
    ).prefetch_related(
        'agressores_atendidos'
    ).order_by('-data_atendimento')

    qtd_de_grupos = grupos.count()

    quantidades_atendidos = sum([grupo.agressores_atendidos.count() for grupo in grupos])

    quantidades_atendidos_unicos = Agressor_dados.objects.filter(
        agressores_atendidos__in=grupos
    ).distinct().count()
    

    qtd_de_grupos_mes = grupos.filter(
        data_atendimento__month=timezone.now().month,
        data_atendimento__year=timezone.now().year
    ).count()


    contexto = {
        'title': 'Todos os Atendimentos - Polícia Penal',
        'description': 'Lista completa de todos os atendimentos registrados pela Polícia Penal.',
        'grupos': grupos,
        'qtd_de_grupos': qtd_de_grupos,
        'qtd_de_grupos_mes': qtd_de_grupos_mes,
        'agressores_totais': quantidades_atendidos,
        'agressores_unicos_totais': quantidades_atendidos_unicos,
        'user': request.user,
    }
    return render(request, "parcial/mostra_todos_grupos.html", contexto)



@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Penal'])
def edita_atendimento_pp(request, grupo_id):
    """
    Edita um atendimento penal específico via HTMX.
    """
    try:
        grupo = ModeloPenal.objects.prefetch_related('agressores_atendidos', 'usuario').get(id=grupo_id)
    except ModeloPenal.DoesNotExist:
        return HttpResponse(
            '<div class="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg text-center">'
            '<p class="text-sm text-red-700"><i class="fas fa-exclamation-triangle mr-2"></i>'
            'Atendimento não encontrado.</p></div>',
            status=404
        )

    if request.method == 'POST':
        form = ModeloPenalForm(request.POST, instance=grupo)
        if form.is_valid():
            atendimento = form.save(commit=False)
            atendimento.usuario = request.user
            atendimento.save()
            form.save_m2m()
            
            # Retornar script que fecha modal e mostra sucesso
            return HttpResponse(
                '<script>'
                'exibirPopupSucesso("✅ Atendimento atualizado com sucesso!", "sucesso");'
                'document.getElementById("modal-container").innerHTML = "";'
                'htmx.ajax("GET", "' + reverse('seguranca_publica:mostra_todos_grupos_penal') + '", '
                '{target: "#lista-grupos", swap: "innerHTML"});'
                '</script>'
            )
        else:
            # Re-renderizar modal com erros
            contexto = {
                'title': f'Editar Atendimento #{grupo_id}',
                'form': form,
                'grupo': grupo,
                'user': request.user,
            }
            return render(request, 'parcial/penal/edita_atendimento.html', contexto)
    
    else:  # GET request - renderizar modal
        form = ModeloPenalForm(instance=grupo)

    contexto = {
        'title': f'Editar Atendimento #{grupo_id}',
        'form': form,
        'grupo': grupo,
        'user': request.user,
    }
    return render(request, 'parcial/penal/edita_atendimento.html', contexto)