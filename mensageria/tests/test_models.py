# mensageria/tests/test_models.py
"""Testes dos models do app mensageria."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import timedelta

from mensageria.models import (
    Notificacao,
    TipoNotificacao,
    PrioridadeNotificacao,
    StatusNotificacao,
)

User = get_user_model()


def criar_usuario(username='user_teste'):
    return User.objects.create_user(username=username, password='senha123')


def criar_notificacao(destinatario, **kwargs):
    """Cria notificação de teste para um usuário."""
    defaults = {
        'titulo': 'Notificação de teste',
        'mensagem': 'Mensagem de teste.',
        'tipo': TipoNotificacao.SISTEMA,
        'prioridade': PrioridadeNotificacao.NORMAL,
        'destinatario_usuario': destinatario,
    }
    defaults.update(kwargs)
    return Notificacao.objects.create(**defaults)


class NotificacaoModelTest(TestCase):
    """Testes do model Notificacao."""

    def setUp(self):
        self.user = criar_usuario('dest')
        self.remetente = criar_usuario('rem')

    def test_criacao_notificacao(self):
        """Notificação deve ser criada com campos obrigatórios."""
        notif = criar_notificacao(self.user, remetente=self.remetente)
        self.assertIsNotNone(notif.pk)
        self.assertEqual(notif.titulo, 'Notificação de teste')

    def test_str_notificacao(self):
        notif = criar_notificacao(self.user)
        self.assertIn('Notificação de teste', str(notif))

    def test_marcar_como_lida(self):
        """marcar_como_lida deve alterar o status."""
        notif = criar_notificacao(self.user)
        resultado = notif.marcar_como_lida()
        self.assertTrue(resultado)
        notif.refresh_from_db()
        self.assertEqual(notif.status, StatusNotificacao.LIDA)

    def test_arquivar(self):
        """arquivar deve alterar o status para ARQUIVADA."""
        notif = criar_notificacao(self.user)
        notif.arquivar()
        notif.refresh_from_db()
        self.assertEqual(notif.status, StatusNotificacao.ARQUIVADA)

    def test_marcar_lida_por_usuario_grupo(self):
        """marcar_lida_por_usuario deve criar StatusNotificacao."""
        grupo, _ = Group.objects.get_or_create(name='Grupo Teste')
        self.user.groups.add(grupo)
        notif = Notificacao.objects.create(
            titulo='Notif Grupo',
            mensagem='Teste.',
            tipo=TipoNotificacao.SISTEMA,
            prioridade=PrioridadeNotificacao.NORMAL,
            destinatario_grupo=grupo,
        )
        notif.marcar_lida_por_usuario(self.user)
        status = StatusNotificacao.objects.filter(notificacao=notif, usuario=self.user)
        self.assertTrue(status.exists())

    def test_esta_expirada_falso(self):
        """Notificação sem data de expiração não deve estar expirada."""
        notif = criar_notificacao(self.user)
        self.assertFalse(notif.esta_expirada())

    def test_esta_expirada_verdadeiro(self):
        """Notificação com data de expiração no passado deve estar expirada."""
        notif = criar_notificacao(
            self.user,
            data_expiracao=timezone.now() - timedelta(days=1),
        )
        self.assertTrue(notif.esta_expirada())

    def test_contar_nao_lidas(self):
        """contar_nao_lidas_usuario deve retornar contagem correta."""
        criar_notificacao(self.user)
        criar_notificacao(self.user)
        count = Notificacao.contar_nao_lidas_usuario(self.user)
        self.assertEqual(count, 2)

    def test_get_nao_lidas_exclui_lidas(self):
        """get_nao_lidas_usuario não deve retornar notificações lidas."""
        n1 = criar_notificacao(self.user)
        n2 = criar_notificacao(self.user)
        n1.marcar_como_lida()
        nao_lidas = Notificacao.get_nao_lidas_usuario(self.user)
        self.assertNotIn(n1, nao_lidas)
        self.assertIn(n2, nao_lidas)

    def test_notificacao_urgente_importante(self):
        """Notificação urgente com importante=True deve ter campos corretos."""
        notif = criar_notificacao(
            self.user,
            prioridade=PrioridadeNotificacao.URGENTE,
            importante=True,
        )
        self.assertEqual(notif.prioridade, PrioridadeNotificacao.URGENTE)
        self.assertTrue(notif.importante)

    def test_get_cor_prioridade_urgente(self):
        """get_cor_prioridade deve retornar vermelho para urgente."""
        notif = criar_notificacao(
            self.user,
            prioridade=PrioridadeNotificacao.URGENTE,
        )
        cor = notif.get_cor_prioridade()
        self.assertIn('red', cor.lower())