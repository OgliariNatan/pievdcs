# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from mensageria.models import Notificacao, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
from sistema_justica.forms.cadastro_mpu import CadastroMedidaProtetiva
from usuarios.models import CustomUser
from django.contrib.auth.models import Group as CustomGroup
from MAIN.decoradores.calcula_tempo import calcula_tempo



@calcula_tempo
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública',])
def defensoria_publica(request):

    # Contar notificações não lidas do usuário
    notificacoes_nao_lidas = Notificacao.contar_nao_lidas_usuario(request.user)

    # Encaminhamentos mensais (exemplo - substituir com lógica real)
    encaminhamentos_mensais = Notificacao.objects.filter(
        destinatario_usuario=request.user,
        tipo='MEDIDA_PROTETIVA'
    ).count()

    contexto = {
        'title': 'Defensoria Pública',
        'description': 'Portal da Defensoria Pública - Sistema PIEVDCS',
        'encaminhamentos': encaminhamentos_mensais,
        'notificacoes': notificacoes_nao_lidas,
        'user': request.user,
    }
    return render(request, "defensoria_publica.html", contexto)

@calcula_tempo
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
        'encaminhamentos': encaminhamentos,
        'user': request.user,
    }
    return render(request, "encaminhamentos.html", context)

@calcula_tempo
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública',])
def listar_notificacoes(request):
    """Lista todas as notificações do usuário"""
    
    # Buscar notificações do usuário
    notificacoes = Notificacao.get_todas_usuario(request.user)
    
    context = {
        'title': 'Notificações - Defensoria Pública',
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

@calcula_tempo
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública', 'Ministério Público',])
def cadastro_mpu(request):
    mensagem_sucesso = None
    if request.method == "POST":
        form = CadastroMedidaProtetiva(request.POST)
        if form.is_valid():
            mpu = form.save()
            mensagem_sucesso = "Medida Protetiva cadastrada com sucesso!"
            
            # Enviar notificação para o Poder Judiciário
            try:
                grupo_judiciario = CustomGroup.objects.get(name='PJ')
                enviar_notificacao_grupo(
                    request=request,
                    grupo_destinatario=grupo_judiciario,
                    titulo="Nova Solicitação de Medida Protetiva",
                    mensagem=f"Defensoria Pública solicitou MPU - Protocolo #{mpu.ID}",
                    tipo='MEDIDA_PROTETIVA',
                    prioridade='ALTA',
                    objeto_relacionado_tipo='FormularioMedidaProtetiva',
                    objeto_relacionado_id=mpu.ID,
                    importante=True
                )
            except CustomGroup.DoesNotExist:
                pass 
            
            form = CadastroMedidaProtetiva()  # Limpa o formulário após sucesso
    else:
        form = CadastroMedidaProtetiva()
    
    contexto = {
        'form': form,
        'mensagem_sucesso': mensagem_sucesso,
    }
    return render(request, "parcial/cadastro_mpu.html", contexto)

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública', 'Ministério Público',])
def consulta_mpu(request):
    # Implementar a lógica de consulta de MPU aqui
    contexto = {
        'title': 'Consulta MPU',
        'description': 'Consulta de Medidas Protetivas de Urgência',
    }
    return render(request, "parcial/consulta_mpu.html", contexto)

def notificar_solicitacao_mpu(request, vitima, solicitante=None):
    """Envia notificação quando uma MPU é solicitada"""
    
    # Se não tiver solicitante, usa o usuário do request
    if not solicitante:
        solicitante = request.user if request else None
    
    # Buscar grupo do Poder Judiciário
    try:
        grupo_judiciario = CustomGroup.objects.get(name='PJ')
        
        # Enviar notificação para o grupo
        enviar_notificacao_grupo(
            request=request,
            grupo_destinatario=grupo_judiciario,
            titulo=f"Nova Solicitação de Medida Protetiva",
            mensagem=f"Defensoria Pública solicitou MPU para {vitima.nome}",
            tipo='MEDIDA_PROTETIVA',
            prioridade='ALTA',
            objeto_relacionado_tipo='Vitima_dados',
            objeto_relacionado_id=vitima.id,
            importante=True
        )
    except CustomGroup.DoesNotExist:
        pass