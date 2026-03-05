# mensageria/consumers.py
# dir: mensageria/consumers.py
import json
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notificacao, StatusNotificacao


class NotificacaoConsumer(AsyncWebsocketConsumer):
    """Consumer WebSocket para notificações em tempo real"""

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        # Canal individual do usuário
        self.user_group_name = f'notificacoes_user_{self.user.id}'

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        # Adicionar aos grupos institucionais do usuário
        user_groups = await self.get_user_groups()
        for group in user_groups:
            group_name = f'notificacoes_grupo_{group.id}'
            await self.channel_layer.group_add(
                group_name,
                self.channel_name
            )

        await self.accept()
        await self.send_notification_count()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

        user_groups = await self.get_user_groups()
        for group in user_groups:
            group_name = f'notificacoes_grupo_{group.id}'
            await self.channel_layer.group_discard(
                group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Recebe mensagem do WebSocket e executa a ação correspondente"""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'erro', 'message': 'JSON inválido'
            }))
            return

        action = data.get('action')

        if action == 'marcar_lida':
            await self.marcar_notificacao_lida_response(data.get('notificacao_id'))
        elif action == 'marcar_todas_lidas':
            await self.marcar_todas_lidas_response()
        elif action == 'arquivar':
            await self.arquivar_notificacao_response(data.get('notificacao_id'))
        elif action == 'obter_nao_lidas':
            await self.send_unread_notifications()
        elif action == 'obter_contador':
            await self.send_notification_count()

    # ---- Handlers de grupo (DEVEM ser métodos da classe, não dentro de receive) ----

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

    # ---- Métodos auxiliares assíncronos ----

    @database_sync_to_async
    def get_user_groups(self):
        return list(self.user.groups.all())

    @database_sync_to_async
    def get_unread_notifications(self):
        """Obtém notificações não lidas do usuário"""
        notificacoes = Notificacao.get_nao_lidas_usuario(self.user)[:10]

        notificacoes_data = []
        for notif in notificacoes:
            status = notif.get_status_para_usuario(self.user)
            notificacoes_data.append({
                'id': notif.id,
                'titulo': notif.titulo,
                'mensagem': notif.mensagem,
                'tipo': notif.tipo,
                'prioridade': notif.prioridade,
                'data_criacao': notif.data_criacao.isoformat(),
                'url_acao': notif.get_url_acao(),
                'status': status,
                'importante': notif.importante,
                'icone': notif.get_icone_tipo(),
                'cor': notif.get_cor_prioridade(),
                'remetente': notif.remetente.get_full_name() if notif.remetente else 'Sistema'
            })
        return notificacoes_data

    async def send_unread_notifications(self):
        """Envia notificações não lidas para o WebSocket"""
        notificacoes_data = await self.get_unread_notifications()
        await self.send(text_data=json.dumps({
            'type': 'notificacoes_nao_lidas',
            'notificacoes': notificacoes_data,
            'total': len(notificacoes_data)
        }))

    @database_sync_to_async
    def get_notification_count(self):
        """Obtém contagem de notificações não lidas"""
        return Notificacao.contar_nao_lidas_usuario(self.user)

    async def send_notification_count(self):
        """Envia contagem de notificações não lidas"""
        count = await self.get_notification_count()
        await self.send(text_data=json.dumps({
            'type': 'contador_atualizado',
            'count': count
        }))

    @database_sync_to_async
    def marcar_notificacao_lida(self, notificacao_id):
        """Marca uma notificação como lida"""
        try:
            notificacao = Notificacao.objects.get(id=notificacao_id)
            if notificacao.destinatario_usuario == self.user:
                success = notificacao.marcar_como_lida()
            elif notificacao.destinatario_grupo and self.user.groups.filter(
                id=notificacao.destinatario_grupo.id
            ).exists():
                success = notificacao.marcar_lida_por_usuario(self.user)
            else:
                success = False

            if success:
                return {'success': True, 'notificacao_id': notificacao_id}
            return {'success': False, 'message': 'Não foi possível marcar como lida'}
        except Notificacao.DoesNotExist:
            return {'success': False, 'message': 'Notificação não encontrada'}

    async def marcar_notificacao_lida_response(self, notificacao_id):
        """Marca notificação como lida e envia resposta"""
        result = await self.marcar_notificacao_lida(notificacao_id)
        if result['success']:
            await self.send(text_data=json.dumps({
                'type': 'notificacao_marcada_lida',
                'notificacao_id': notificacao_id
            }))
            await self.send_notification_count()
        else:
            await self.send(text_data=json.dumps({
                'type': 'erro',
                'message': result.get('message', 'Erro ao marcar como lida')
            }))

    @database_sync_to_async
    def marcar_todas_lidas(self):
        """Marca todas as notificações como lidas"""
        from .utils import marcar_todas_como_lidas
        marcar_todas_como_lidas(self.user)
        return True

    async def marcar_todas_lidas_response(self):
        """Marca todas como lidas e envia resposta"""
        await self.marcar_todas_lidas()
        await self.send(text_data=json.dumps({
            'type': 'todas_marcadas_lidas'
        }))
        await self.send_notification_count()

    @database_sync_to_async
    def arquivar_notificacao(self, notificacao_id):
        """Arquiva uma notificação"""
        try:
            notificacao = Notificacao.objects.get(id=notificacao_id)
            if notificacao.destinatario_usuario == self.user:
                success = notificacao.arquivar()
            elif notificacao.destinatario_grupo and self.user.groups.filter(
                id=notificacao.destinatario_grupo.id
            ).exists():
                success = notificacao.arquivar_por_usuario(self.user)
            else:
                success = False

            if success:
                return {'success': True, 'notificacao_id': notificacao_id}
            return {'success': False, 'message': 'Não foi possível arquivar'}
        except Notificacao.DoesNotExist:
            return {'success': False, 'message': 'Notificação não encontrada'}

    async def arquivar_notificacao_response(self, notificacao_id):
        """Arquiva notificação e envia resposta"""
        result = await self.arquivar_notificacao(notificacao_id)
        if result['success']:
            await self.send(text_data=json.dumps({
                'type': 'notificacao_arquivada',
                'notificacao_id': notificacao_id
            }))
            await self.send_notification_count()
        else:
            await self.send(text_data=json.dumps({
                'type': 'erro',
                'message': result.get('message', 'Erro ao arquivar')
            }))