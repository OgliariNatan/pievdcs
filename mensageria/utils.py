from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
#from django.contrib.auth.models import User, Group
from usuarios.models import CustomUser, CustomGroup
from .models import Notificacao, StatusNotificacaoUsuario, PrioridadeNotificacao, TipoNotificacao

def enviar_notificacao_usuario(
    usuario_destinatario,
    titulo,
    mensagem,
    tipo=TipoNotificacao.SISTEMA,
    prioridade=PrioridadeNotificacao.NORMAL,
    remetente=None,
    url_acao=None,
    objeto_relacionado_tipo=None,
    objeto_relacionado_id=None
):
    """
    Envia notificação para um usuário específico
    """
    # Criar notificação
    notificacao = Notificacao.objects.create(
        remetente=remetente,
        destinatario_usuario=usuario_destinatario,
        titulo=titulo,
        mensagem=mensagem,
        tipo=tipo,
        prioridade=prioridade,
        url_acao=url_acao,
        objeto_relacionado_tipo=objeto_relacionado_tipo,
        objeto_relacionado_id=objeto_relacionado_id
    )
    
    # Criar status para o usuário
    StatusNotificacaoUsuario.objects.create(
        notificacao=notificacao,
        usuario=usuario_destinatario
    )
    
    # Enviar via WebSocket
    channel_layer = get_channel_layer()
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
                'url_acao': notificacao.url_acao
            }
        }
    )
    
    return notificacao

def enviar_notificacao_grupo(
    grupo_destinatario,
    titulo,
    mensagem,
    tipo=TipoNotificacao.SISTEMA,
    prioridade=PrioridadeNotificacao.NORMAL,
    remetente=None,
    url_acao=None,
    objeto_relacionado_tipo=None,
    objeto_relacionado_id=None
):
    """
    Envia notificação para todos os usuários de um grupo
    """
    # Criar notificação
    notificacao = Notificacao.objects.create(
        remetente=remetente,
        destinatario_grupo=grupo_destinatario,
        titulo=titulo,
        mensagem=mensagem,
        tipo=tipo,
        prioridade=prioridade,
        url_acao=url_acao,
        objeto_relacionado_tipo=objeto_relacionado_tipo,
        objeto_relacionado_id=objeto_relacionado_id
    )
    
    # Obter usuários do grupo corretamente
    # CustomGroup tem um relacionamento reverso 'user_set' com CustomUser
    usuarios_grupo = grupo_destinatario.user_set.all()
    
    # Criar status para cada usuário do grupo
    for usuario in usuarios_grupo:
        StatusNotificacaoUsuario.objects.create(
            notificacao=notificacao,
            usuario=usuario
        )
    
    # Enviar via WebSocket para o grupo
    channel_layer = get_channel_layer()
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
                'url_acao': notificacao.url_acao
            }
        }
    )
    
    return notificacao

def enviar_notificacao_multiplos_usuarios(
    usuarios_destinatarios,
    titulo,
    mensagem,
    tipo=TipoNotificacao.SISTEMA,
    prioridade=PrioridadeNotificacao.NORMAL,
    remetente=None,
    url_acao=None
):
    """
    Envia notificação para múltiplos usuários
    """
    for usuario in usuarios_destinatarios:
        enviar_notificacao_usuario(
            usuario_destinatario=usuario,
            titulo=titulo,
            mensagem=mensagem,
            tipo=tipo,
            prioridade=prioridade,
            remetente=remetente,
            url_acao=url_acao
        )

def notificar_violencia_domestica_urgente(vitima_nome, localizacao, usuarios_responsaveis):
    """
    Exemplo de função específica para notificação urgente de violência doméstica
    """
    titulo = f"⚠️ URGENTE: Caso de Violência Doméstica"
    mensagem = f"Nova ocorrência registrada - Vítima: {vitima_nome} - Local: {localizacao}"
    
    enviar_notificacao_multiplos_usuarios(
        usuarios_destinatarios=usuarios_responsaveis,
        titulo=titulo,
        mensagem=mensagem,
        tipo=TipoNotificacao.VIOLENCIA_DOMESTICA,
        prioridade=PrioridadeNotificacao.URGENTE
    )