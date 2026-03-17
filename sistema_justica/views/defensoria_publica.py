# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Func, F, Value, CharField, Q
from datetime import date
from mensageria.models import Notificacao, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
from sistema_justica.forms.cadastro_mpu import CadastroMedidaProtetiva
from usuarios.models import CustomUser
from django.contrib.auth.models import Group as CustomGroup
from MAIN.decoradores.calcula_tempo import calcula_tempo


""" Configuraçao de decoradores para debug """
import os

var_debug = os.getenv('DEBUG')

if var_debug == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo, calcula_tempo_fun
    checked_debug_decorador = calcula_tempo
    checked_debug_decorador_fun = calcula_tempo_fun
    
    
else:
    checked_debug_decorador = lambda x: x  
    checked_debug_decorador_fun = lambda x: x  
""" Fim da configuraçao de decoradores para debug """



ANO_CORRENTE = date.today().year

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública',])
def defensoria_publica(request):

    # Contar notificações não lidas do usuário
    notificacoes_nao_lidas = Notificacao.contar_nao_lidas_usuario(request.user)
    encaminhamentos_nao_lidos = Notificacao.contar_encaminhamentos_nao_lidos(request.user)

    

    casos_ativos = 985

    contexto = {
        'title': 'Defensoria Pública',
        'ano_corrente': ANO_CORRENTE,
        'casos_ativos': casos_ativos,
        'description': 'Portal da Defensoria Pública - Sistema PIEVDCS',
        'encaminhamentos': encaminhamentos_nao_lidos,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'user': request.user,
    }
    return render(request, "defensoria_publica.html", contexto)

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública',])
def listar_encaminhamentos(request):
    """ Lista de encaminhamentos da defensoria pública """
    # Buscar todas as notificações do usuário
    encaminhamentos_query = Notificacao.get_todas_usuario(request.user)
    
    # Filtrar por tipo se especificado
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        encaminhamentos_query = encaminhamentos_query.filter(tipo=tipo_filtro)
    
    # Ordenar por data mais recente
    encaminhamentos = encaminhamentos_query.order_by('-data_criacao')[:20]  # Últimos 20 encaminhamentos
    
    context = {
        'title': 'Encaminhamentos - Defensoria Pública',
        'description': 'Lista de encaminhamentos e notificações',
        'ano_corrente': ANO_CORRENTE,
        'encaminhamentos': encaminhamentos,
        'user': request.user,
    }
    return render(request, "encaminhamentos.html", context)

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública',])
def listar_notificacoes(request):
    """Lista todas as notificações do usuário"""
    
    # Buscar notificações do usuário
    notificacoes = Notificacao.get_todas_usuario(request.user)
    
    
    context = {
        'title': 'Notificações - Defensoria Pública',
        'ano_corrente': ANO_CORRENTE,
        'notificacoes': notificacoes,
        'user': request.user,
    }
    return render(request, 'notificacoes.html', context)

@login_required(login_url=reverse_lazy('login'))
@require_POST
def marcar_notificacao_lida(request, notificacao_id):
    """Marca uma notificação como lida"""
    try:
        notificacao = Notificacao.objects.get(id=notificacao_id)
        
        # Verificar se é notificação individual ou de grupo
        if notificacao.destinatario_usuario == request.user:
            notificacao.marcar_como_lida()
        elif notificacao.destinatario_grupo and request.user.groups.filter(id=notificacao.destinatario_grupo.id).exists():
            notificacao.marcar_lida_por_usuario(request.user)
        else:
            return JsonResponse({'status': 'error', 'message': 'Sem permissão'}, status=403)
            
        return JsonResponse({'status': 'success'})
    except Notificacao.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notificação não encontrada'}, status=404)

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública', 'Ministério Público','Polícia Civil'])
def cadastro_mpu(request):
    """Cadastro de Medida Protetiva de Urgência."""
    if request.method == "POST":
        form = CadastroMedidaProtetiva(request.POST)
        if form.is_valid():
            mpu = form.save()
            urgencia = mpu.solicitada_mpu
            
            # Notificar Poder Judiciário
            try:
                
                grupo_judiciario = CustomGroup.objects.get(name='Poder Judiciário')
                enviar_notificacao_grupo(
                    request=request,
                    grupo_destinatario=grupo_judiciario,
                    titulo=f"Nova Solicitação de Medida Protetiva {'de Urgência' if urgencia else ''}",
                    mensagem=f"Solicitada Medida Protetiva {'de Urgência' if urgencia else ''} - Protocolo #{mpu.ID}",
                    tipo='MEDIDA_PROTETIVA',
                    prioridade='URGENTE',
                    objeto_relacionado_tipo='FormularioMedidaProtetiva',
                    objeto_relacionado_id=mpu.ID,
                    importante=True
                )
            except CustomGroup.DoesNotExist:
                pass

            # Retorna HTML vazio + header HTMX para fechar modal e exibir toast
            response = HttpResponse('<div id="modal-mpu"></div>')
            response['HX-Trigger'] = '{"mpuSalva": "Medida Protetiva #' + str(mpu.ID) + ' cadastrada com sucesso!"}'
            return response

        # Se formulário inválido, re-renderiza com erros no topo
        contexto = {'form': form}
        return render(request, "parcial/cadastro_mpu.html", contexto)

    form = CadastroMedidaProtetiva()
    return render(request, "parcial/cadastro_mpu.html", {'form': form})

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública', 'Ministério Público',])
def consulta_mpu(request):
    # Implementar a lógica de consulta de MPU aqui
    contexto = {
        'title': 'Consulta MPU',
        'description': 'Consulta de Medidas Protetivas de Urgência',
    }
    return render(request, "parcial/consulta_mpu.html", contexto)



@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública', 'Ministério Público'])
def consultar_mp(request):
    """
    Lista medidas protetivas com filtros para consulta do Ministério Público e Defensoria Pública (somente leitura).
    dir: sistema_justica/views/defensoria_publica.py
    """
    from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
    from sistema_justica.models.poder_judiciario import ComarcasPoderJudiciario

    filtro_status = request.GET.get('status', 'todas')
    filtro_ordenar = request.GET.get('ordenar', 'periodo_mp')
    filtro_busca = request.GET.get('busca', '').strip()
    filtro_comarca = request.GET.get('comarca', '')

    qs = FormularioMedidaProtetiva.objects.select_related(
        'vitima', 'agressor', 'comarca_competente'
    )

    hoje = date.today()

    # Filtro por status
    if filtro_status == 'ativas':
        qs = qs.filter(periodo_mp__gte=hoje)
    elif filtro_status == 'vencidas':
        qs = qs.filter(periodo_mp__lt=hoje)

    # Filtro por comarca
    if filtro_comarca:
        qs = qs.filter(comarca_competente_id=filtro_comarca)

    # Filtro por busca (nome ou CPF da vítima/agressor)
    if filtro_busca:
        qs = qs.filter(
            Q(vitima__nome__icontains=filtro_busca) |
            Q(vitima__cpf__icontains=filtro_busca) |
            Q(agressor__nome__icontains=filtro_busca) |
            Q(agressor__cpf__icontains=filtro_busca)
        )

    # Ordenação
    ordenacoes_permitidas = ['periodo_mp', '-periodo_mp', '-data_solicitacao']
    if filtro_ordenar not in ordenacoes_permitidas:
        filtro_ordenar = 'periodo_mp'
    qs = qs.order_by(filtro_ordenar)

    # Propriedades dinâmicas - ativos primeiro
    medidas = list(qs)
    for mp in medidas:
        mp.ativa = mp.periodo_mp >= hoje
        mp.dias_restantes = (mp.periodo_mp - hoje).days if mp.ativa else 0
    medidas.sort(key=lambda mp: (not mp.ativa,))

    comarcas = ComarcasPoderJudiciario.objects.order_by('nome')

    contexto = {
        'medidas': medidas,
        'filtro_status': filtro_status,
        'filtro_ordenar': filtro_ordenar,
        'filtro_busca': filtro_busca,
        'filtro_comarca': filtro_comarca,
        'comarcas': comarcas,
    }

    # Requisição HTMX com filtro → retorna só a tabela
    if request.headers.get('HX-Target') == 'tabela-mp-penal':
        return render(request, 'parcial/defensoria_publica/tabela_mp.html', contexto)

    return render(request, 'parcial/defensoria_publica/consultar_mp.html', contexto)
@csrf_protect
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública', 'Ministério Público'])
def editar_mpu(request, mpu_id):
    """
    Edita os campos de avaliação de violência psicológica de uma MPU existente.
    dir: sistema_justica/views/defensoria_publica.py
    """
    from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
    from sistema_justica.forms.editar_mpu import EditarFormularioMPU

    mpu = FormularioMedidaProtetiva.objects.select_related(
        'vitima', 'agressor', 'comarca_competente'
    ).get(ID=mpu_id)

    if request.method == 'POST':
        form = EditarFormularioMPU(request.POST, instance=mpu)
        if form.is_valid():
            form.save()
            response = HttpResponse('<div id="modal-editar-mpu"></div>')
            response['HX-Trigger'] = '{"mpuEditada": "MPU #' + str(mpu.ID) + ' atualizada com sucesso!"}'
            return response
        return render(request, 'parcial/defensoria_publica/editar_mpu.html', {
            'form': form, 'mpu': mpu
        })

    form = EditarFormularioMPU(instance=mpu)
    return render(request, 'parcial/defensoria_publica/editar_mpu.html', {
        'form': form, 'mpu': mpu
    })