import json
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Notificacao, StatusNotificacaoUsuario, StatusNotificacao

class NotificacaoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Canal individual do usuário
        self.user_group_name = f'notificacoes_user_{self.user.id}'
        
        # Adicionar ao grupo do usuário
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        # Adicionar aos grupos do usuário
        user_groups = await self.get_user_groups()
        for group in user_groups:
            group_name = f'notificacoes_grupo_{group.id}'
            await self.channel_layer.group_add(
                group_name,
                self.channel_name
            )
        
        await self.accept()
        
        # Enviar notificações não lidas ao conectar
        await self.send_unread_notifications()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        
        # Remover dos grupos
        user_groups = await self.get_user_groups()
        for group in user_groups:
            group_name = f'notificacoes_grupo_{group.id}'
            await self.channel_layer.group_discard(
                group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'marcar_lida':
            await self.marcar_notificacao_lida(data.get('notificacao_id'))
        elif action == 'marcar_todas_lidas':
            await self.marcar_todas_lidas()
        elif action == 'arquivar':
            await self.arquivar_notificacao(data.get('notificacao_id'))
        elif action == 'obter_nao_lidas':
            await self.send_unread_notifications()
    
    async def nova_notificacao(self, event):
        """Recebe notificação do grupo e envia ao WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'nova_notificacao',
            'notificacao': event['notificacao']
        }))
    
    async def notificacao_atualizada(self, event):
        """Recebe atualização de notificação"""
        await self.send(text_data=json.dumps({
            'type': 'notificacao_atualizada',
            'notificacao': event['notificacao']
        }))
    
    @database_sync_to_async
    def get_user_groups(self):
        return list(self.user.groups.all())
    
    @database_sync_to_async
    def send_unread_notifications(self):
        notificacoes = StatusNotificacaoUsuario.objects.filter(
            usuario=self.user,
            status=StatusNotificacao.NAO_LIDA
        ).select_related('notificacao')
        
        notificacoes_data = []
        for status in notificacoes:
            notif = status.notificacao
            notificacoes_data.append({
                'id': notif.id,
                'titulo': notif.titulo,
                'mensagem': notif.mensagem,
                'tipo': notif.tipo,
                'prioridade': notif.prioridade,
                'data_criacao': notif.data_criacao.isoformat(),
                'url_acao': notif.url_acao,
                'status': status.status
            })
        
        self.send(text_data=json.dumps({
            'type': 'notificacoes_nao_lidas',
            'notificacoes': notificacoes_data,
            'total': len(notificacoes_data)
        }))
    
    @database_sync_to_async
    def marcar_notificacao_lida(self, notificacao_id):
        try:
            status = StatusNotificacaoUsuario.objects.get(
                notificacao_id=notificacao_id,
                usuario=self.user
            )
            status.marcar_como_lida()
            
            self.send(text_data=json.dumps({
                'type': 'notificacao_marcada_lida',
                'notificacao_id': notificacao_id
            }))
        except StatusNotificacaoUsuario.DoesNotExist:
            pass
    
    @database_sync_to_async
    def marcar_todas_lidas(self):
        StatusNotificacaoUsuario.objects.filter(
            usuario=self.user,
            status=StatusNotificacao.NAO_LIDA
        ).update(
            status=StatusNotificacao.LIDA,
            data_leitura=timezone.now()
        )
        
        self.send(text_data=json.dumps({
            'type': 'todas_marcadas_lidas'
        }))
    
    @database_sync_to_async
    def arquivar_notificacao(self, notificacao_id):
        try:
            status = StatusNotificacaoUsuario.objects.get(
                notificacao_id=notificacao_id,
                usuario=self.user
            )
            status.arquivar()
            
            self.send(text_data=json.dumps({
                'type': 'notificacao_arquivada',
                'notificacao_id': notificacao_id
            }))
        except StatusNotificacaoUsuario.DoesNotExist:
            pass