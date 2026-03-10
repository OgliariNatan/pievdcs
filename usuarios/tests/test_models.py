# usuarios/tests/test_models.py
"""Testes do model de usuário customizado."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Testes do CustomUser."""

    def test_criacao_usuario(self):
        """Usuário deve ser criado com username e senha."""
        user = User.objects.create_user(username='teste', password='senha123')
        self.assertEqual(user.username, 'teste')
        self.assertTrue(user.check_password('senha123'))
        self.assertFalse(user.is_staff)

    def test_criacao_superusuario(self):
        user = User.objects.create_superuser(username='admin', password='admin123')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_usuario_sem_grupo(self):
        """Usuário recém criado não deve ter grupos."""
        user = User.objects.create_user(username='semgrupo', password='senha123')
        self.assertEqual(user.groups.count(), 0)

    def test_usuario_com_grupo_policia_militar(self):
        grupo, _ = Group.objects.get_or_create(name='Polícia Militar')
        user = User.objects.create_user(username='pm', password='senha123')
        user.groups.add(grupo)
        self.assertTrue(user.groups.filter(name='Polícia Militar').exists())

    def test_usuario_com_multiplos_grupos(self):
        """Usuário pode pertencer a múltiplos grupos."""
        g1, _ = Group.objects.get_or_create(name='Polícia Militar')
        g2, _ = Group.objects.get_or_create(name='Poder Judiciário')
        user = User.objects.create_user(username='multi', password='senha123')
        user.groups.add(g1, g2)
        self.assertEqual(user.groups.count(), 2)