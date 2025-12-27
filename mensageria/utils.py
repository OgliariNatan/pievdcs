from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from usuarios.models import CustomUser
from django.contrib.auth.models import Group as CustomGroup
from .models import Notificacao, PrioridadeNotificacao, TipoNotificacao
from django.utils import timezone

def enviar_notificacao_usuario(
    request,  # Adicionado para capturar o usuário logado
    usuario_destinatario,
    titulo,
    mensagem,
    tipo=TipoNotificacao.SISTEMA,
    prioridade=PrioridadeNotificacao.NORMAL,
    objeto_relacionado_tipo=None,
    objeto_relacionado_id=None,
    importante=False,
    data_expiracao=None
):
    """
    Envia notificação para um usuário específico
    O remetente é automaticamente definido como o usuário logado
    """
    # Captura o usuário logado do request
    remetente = request.user if request and hasattr(request, 'user') and request.user.is_authenticated else None
    
    # Criar notificação
    notificacao = Notificacao.objects.create(
        remetente=remetente,  # Usuário logado
        destinatario_usuario=usuario_destinatario,
        titulo=titulo,
        mensagem=mensagem,
        tipo=tipo,
        prioridade=prioridade,
        objeto_relacionado_tipo=objeto_relacionado_tipo,
        objeto_relacionado_id=objeto_relacionado_id,
        importante=importante,
        data_expiracao=data_expiracao
    )
    
    # Enviar via WebSocket
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f'notificacoes_user_{usuario_destinatario.id}',
            {
                'type': 'nova_notificacao',
                'notificacao': {
                    'id': notificacao.id,
                    'titulo': notificacao.titulo,
                    'mensagem': notificacao.mensagem,
                    'tipo': notificacao.tipo,
                    'prioridade': notificacao.prioridade,
                    'data_criacao': notificacao.data_criacao.isoformat(),
                    'url_acao': notificacao.get_url_acao(),  # Usa o método get_url_acao
                    'importante': notificacao.importante,
                    'icone': notificacao.get_icone_tipo(),
                    'cor': notificacao.get_cor_prioridade(),
                    'remetente': remetente.get_full_name() if remetente else 'Sistema'
                }
            }
        )
    
    return notificacao

def enviar_notificacao_grupo(
    request,  # Adicionado para capturar o usuário logado
    grupo_destinatario,
    titulo,
    mensagem,
    tipo=TipoNotificacao.SISTEMA,
    prioridade=PrioridadeNotificacao.NORMAL,
    objeto_relacionado_tipo=None,
    objeto_relacionado_id=None,
    importante=False,
    data_expiracao=None
):
    """
    Envia notificação para todos os usuários de um grupo
    O remetente é automaticamente definido como o usuário logado
    """
    # Captura o usuário logado do request
    remetente = request.user if request and hasattr(request, 'user') and request.user.is_authenticated else None
    
    # Criar notificação para o grupo
    notificacao = Notificacao.objects.create(
        remetente=remetente,  # Usuário logado
        destinatario_grupo=grupo_destinatario,
        titulo=titulo,
        mensagem=mensagem,
        tipo=tipo,
        prioridade=prioridade,
        objeto_relacionado_tipo=objeto_relacionado_tipo,
        objeto_relacionado_id=objeto_relacionado_id,
        importante=importante,
        data_expiracao=data_expiracao
    )
    
    # Enviar via WebSocket para o grupo
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f'notificacoes_grupo_{grupo_destinatario.id}',
            {
                'type': 'nova_notificacao',
                'notificacao': {
                    'id': notificacao.id,
                    'titulo': notificacao.titulo,
                    'mensagem': notificacao.mensagem,
                    'tipo': notificacao.tipo,
                    'prioridade': notificacao.prioridade,
                    'data_criacao': notificacao.data_criacao.isoformat(),
                    'url_acao': notificacao.get_url_acao(),  # Usa o método get_url_acao
                    'importante': notificacao.importante,
                    'icone': notificacao.get_icone_tipo(),
                    'cor': notificacao.get_cor_prioridade(),
                    'remetente': remetente.get_full_name() if remetente else 'Sistema'
                }
            }
        )
    
    return notificacao

def enviar_notificacao_multiplos_usuarios(
    request,  # Adicionado para capturar o usuário logado
    usuarios_destinatarios,
    titulo,
    mensagem,
    tipo=TipoNotificacao.SISTEMA,
    prioridade=PrioridadeNotificacao.NORMAL,
    importante=False
):
    """
    Envia notificação individual para múltiplos usuários
    O remetente é automaticamente definido como o usuário logado
    """
    notificacoes = []
    for usuario in usuarios_destinatarios:
        notif = enviar_notificacao_usuario(
            request=request,
            usuario_destinatario=usuario,
            titulo=titulo,
            mensagem=mensagem,
            tipo=tipo,
            prioridade=prioridade,
            importante=importante
        )
        notificacoes.append(notif)
    return notificacoes

def notificar_violencia_domestica_urgente(request, vitima_nome, localizacao, usuarios_responsaveis):
    """
    Função específica para notificação urgente de violência doméstica
    """
    titulo = f"⚠️ URGENTE: Caso de Violência Doméstica"
    mensagem = f"Nova ocorrência registrada\nVítima: {vitima_nome}\nLocal: {localizacao}\n\nAção imediata requerida."
    
    return enviar_notificacao_multiplos_usuarios(
        request=request,
        usuarios_destinatarios=usuarios_responsaveis,
        titulo=titulo,
        mensagem=mensagem,
        tipo=TipoNotificacao.VIOLENCIA_DOMESTICA,
        prioridade=PrioridadeNotificacao.URGENTE,
        importante=True
    )

def notificar_medida_protetiva_deferida(request, numero_processo, vitima_nome, grupo_destinatario, vitima_id=None):
    """
    Notifica quando uma medida protetiva é deferida
    """
    titulo = "✅ Medida Protetiva Deferida"
    mensagem = f"A medida protetiva do processo {numero_processo} foi DEFERIDA.\nVítima: {vitima_nome}"
    
    return enviar_notificacao_grupo(
        request=request,
        grupo_destinatario=grupo_destinatario,
        titulo=titulo,
        mensagem=mensagem,
        tipo=TipoNotificacao.MEDIDA_PROTETIVA,
        prioridade=PrioridadeNotificacao.ALTA,
        objeto_relacionado_tipo='FormularioMedidaProtetiva' if vitima_id else None,
        objeto_relacionado_id=vitima_id,
        importante=True
    )

def obter_resumo_notificacoes(usuario):
    """
    Obtém resumo de notificações para um usuário
    """
    total_nao_lidas = Notificacao.contar_nao_lidas_usuario(usuario)
    notificacoes_urgentes = Notificacao.get_nao_lidas_usuario(usuario).filter(
        prioridade=PrioridadeNotificacao.URGENTE
    ).count()
    
    notificacoes_importantes = Notificacao.get_nao_lidas_usuario(usuario).filter(
        importante=True
    ).count()
    
    return {
        'total_nao_lidas': total_nao_lidas,
        'urgentes': notificacoes_urgentes,
        'importantes': notificacoes_importantes,
        'tem_notificacoes': total_nao_lidas > 0
    }

def marcar_todas_como_lidas(usuario):
    """
    Marca todas as notificações de um usuário como lidas
    """
    # Notificações individuais
    Notificacao.objects.filter(
        destinatario_usuario=usuario,
        status='NAO_LIDA'
    ).update(
        status='LIDA',
        data_leitura=timezone.now()
    )
    
    # Notificações de grupo
    notificacoes_grupo = Notificacao.objects.filter(
        destinatario_grupo__in=usuario.groups.all()
    ).exclude(usuarios_que_leram=usuario)
    
    for notif in notificacoes_grupo:
        notif.marcar_lida_por_usuario(usuario)
    
    return True

# Funções alternativas para uso sem request (ex: tarefas agendadas, signals)
def enviar_notificacao_sistema(
    usuario_destinatario,
    titulo,
    mensagem,
    tipo=TipoNotificacao.SISTEMA,
    prioridade=PrioridadeNotificacao.NORMAL,
    **kwargs
):
    """
    Envia notificação do sistema (sem remetente)
    Para uso em tarefas automatizadas onde não há request
    """
    return enviar_notificacao_usuario(
        request=None,  # Sem request, remetente será None
        usuario_destinatario=usuario_destinatario,
        titulo=titulo,
        mensagem=mensagem,
        tipo=tipo,
        prioridade=prioridade,
        **kwargs
    )