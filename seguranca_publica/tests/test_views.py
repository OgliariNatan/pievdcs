# seguranca_publica/tests/test_views.py
"""Testes das views do app seguranca_publica."""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Group

from django.contrib.auth import get_user_model
from .test_models import criar_vitima, criar_agressor, criar_medida_protetiva

User = get_user_model()


def criar_usuario_com_grupo(username, grupo_nome):
    """Cria usuário com grupo e retorna (user, client logado)."""
    user = User.objects.create_user(username=username, password='senha123')
    grupo, _ = Group.objects.get_or_create(name=grupo_nome)
    user.groups.add(grupo)
    client = Client()
    client.login(username=username, password='senha123')
    return user, client


class ViewsAcessoSemLoginTest(TestCase):
    """Rotas protegidas devem redirecionar para login quando não autenticado."""

    def test_penal_redireciona_sem_login(self):
        response = self.client.get(reverse('seguranca_publica:penal'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('seguranca_publica:penal')}")

    def test_militar_redireciona_sem_login(self):
        response = self.client.get(reverse('seguranca_publica:militar'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('seguranca_publica:militar')}")

    def test_civil_redireciona_sem_login(self):
        response = self.client.get(reverse('seguranca_publica:civil'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('seguranca_publica:civil')}")


class ViewsMilitarTest(TestCase):
    """Testes das views da Polícia Militar."""

    def setUp(self):
        self.user, self.client = criar_usuario_com_grupo('pm', 'Polícia Militar')
        self.medida = criar_medida_protetiva()

    def test_militar_status_200(self):
        response = self.client.get(reverse('seguranca_publica:militar'))
        self.assertEqual(response.status_code, 200)

    def test_cadastrar_atendimento_get(self):
        url = reverse('seguranca_publica:cadastrar_atendimento', args=[self.medida.ID])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_listar_atendimentos_status_200(self):
        url = reverse('seguranca_publica:listar_atendimentos', args=[self.medida.ID])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_acesso_negado_para_grupo_errado(self):
        """Usuário fora do grupo Polícia Militar não deve acessar."""
        user2, client2 = criar_usuario_com_grupo('civil_user', 'Polícia Civil')
        response = client2.get(reverse('seguranca_publica:militar'))
        self.assertEqual(response.status_code, 403)


class ViewsPenalTest(TestCase):
    """Testes das views da Polícia Penal."""

    def setUp(self):
        self.user, self.client = criar_usuario_com_grupo('penal', 'Polícia Penal')

    def test_penal_status_200(self):
        response = self.client.get(reverse('seguranca_publica:penal'))
        self.assertEqual(response.status_code, 200)