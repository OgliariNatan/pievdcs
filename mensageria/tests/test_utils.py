# mensageria/tests/test_utils.py
"""Testes das funções utilitárias do app mensageria."""

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from unittest.mock import patch, MagicMock

from mensageria.models import Notificacao, TipoNotificacao, PrioridadeNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo

User = get_user_model()


def criar_usuario(username):
    return User.objects.create_user(username=username, password='senha123')


@patch('mensageria.utils.get_channel_layer', return_value=None)
class EnviarNotificacaoUsuarioTest(TestCase):
    """Testes de enviar_notificacao_usuario (sem WebSocket real)."""

    def setUp(self):
        self.factory = RequestFactory()
        self.remetente = criar_usuario('rem')
        self.destinatario = criar_usuario('dest')

    def _request(self):
        request = self.factory.get('/')
        request.user = self.remetente
        return request

    def test_cria_notificacao_no_banco(self, mock_channel):
        enviar_notificacao_usuario(
            request=self._request(),
            usuario_destinatario=self.destinatario,
            titulo='Teste',
            mensagem='Mensagem de teste.',
        )
        self.assertEqual(Notificacao.objects.filter(destinatario_usuario=self.destinatario).count(), 1)

    def test_remetente_definido_pelo_request(self, mock_channel):
        enviar_notificacao_usuario(
            request=self._request(),
            usuario_destinatario=self.destinatario,
            titulo='Teste',
            mensagem='Mensagem.',
        )
        notif = Notificacao.objects.get(destinatario_usuario=self.destinatario)
        self.assertEqual(notif.remetente, self.remetente)

    def test_request_none_remetente_none(self, mock_channel):
        enviar_notificacao_usuario(
            request=None,
            usuario_destinatario=self.destinatario,
            titulo='Sistema',
            mensagem='Mensagem automática.',
        )
        notif = Notificacao.objects.get(destinatario_usuario=self.destinatario)
        self.assertIsNone(notif.remetente)


@patch('mensageria.utils.get_channel_layer', return_value=None)
class EnviarNotificacaoGrupoTest(TestCase):
    """Testes de enviar_notificacao_grupo."""

    def setUp(self):
        self.factory = RequestFactory()
        self.remetente = criar_usuario('rem_grupo')
        self.grupo, _ = Group.objects.get_or_create(name='Poder Judiciário')

    def _request(self):
        request = self.factory.get('/')
        request.user = self.remetente
        return request

    def test_cria_notificacao_para_grupo(self, mock_channel):
        enviar_notificacao_grupo(
            request=self._request(),
            grupo_destinatario=self.grupo,
            titulo='Descumprimento',
            mensagem='MP descumprida.',
            tipo=TipoNotificacao.MEDIDA_PROTETIVA,
            prioridade=PrioridadeNotificacao.URGENTE,
            importante=True,
        )
        notif = Notificacao.objects.get(destinatario_grupo=self.grupo)
        self.assertEqual(notif.titulo, 'Descumprimento')
        self.assertEqual(notif.prioridade, PrioridadeNotificacao.URGENTE)
        self.assertTrue(notif.importante)