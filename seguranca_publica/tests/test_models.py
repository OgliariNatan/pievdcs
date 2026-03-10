# seguranca_publica/tests/test_models.py
"""Testes dos models do app seguranca_publica."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch

from sistema_justica.models.base import Vitima_dados, Agressor_dados, Estado, Municipio
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from seguranca_publica.models.militar import (
    AtendimentosRedeCatarina,
    AnexoAtendimento,
)
from seguranca_publica.models.penal import TipoAtendimento, AtendimentoPenal

User = get_user_model()


def criar_usuario(username='teste', grupo_nome=None):
    """Cria usuário de teste com grupo opcional."""
    from django.contrib.auth.models import Group
    user = User.objects.create_user(username=username, password='senha123')
    if grupo_nome:
        grupo, _ = Group.objects.get_or_create(name=grupo_nome)
        user.groups.add(grupo)
    return user


def criar_vitima():
    """Cria vítima de teste."""
    estado, _ = Estado.objects.get_or_create(nome='Santa Catarina', sigla='SC')
    municipio, _ = Municipio.objects.get_or_create(
        nome='Florianópolis', estado=estado,
        defaults={'latitude': -27.5954, 'longitude': -48.548}
    )
    return Vitima_dados.objects.create(
        nome='Maria Silva',
        cpf='123.456.789-00',
        data_nascimento='1990-01-01',
        estado=estado,
        municipio=municipio,
    )


def criar_agressor():
    """Cria agressor de teste."""
    return Agressor_dados.objects.create(
        nome='João Silva',
        cpf='987.654.321-00',
        data_nascimento='1985-05-10',
    )


def criar_medida_protetiva(vitima=None, agressor=None):
    """Cria medida protetiva de teste."""
    vitima = vitima or criar_vitima()
    agressor = agressor or criar_agressor()
    return FormularioMedidaProtetiva.objects.create(
        vitima=vitima,
        agressor=agressor,
        possivel_causa='Briga doméstica',
        bairro_mp='Centro',
        rua_mp='Rua das Flores',
        n_casa_mp='100',
    )


class AtendimentosRedeCatarinaModelTest(TestCase):
    """Testes do model AtendimentosRedeCatarina."""

    def setUp(self):
        self.usuario = criar_usuario('pm_teste', 'Polícia Militar')
        self.medida = criar_medida_protetiva()

    def test_criacao_atendimento(self):
        """Atendimento deve ser criado com campos obrigatórios."""
        atendimento = AtendimentosRedeCatarina.objects.create(
            medida_protetiva=self.medida,
            responsavel=self.usuario,
            situacao_vitima='segura',
            descricao_atendimento='Atendimento de rotina.',
        )
        self.assertIsNotNone(atendimento.pk)
        self.assertEqual(atendimento.medida_protetiva, self.medida)

    def test_str_atendimento(self):
        """__str__ deve conter o ID do atendimento e da MP."""
        atendimento = AtendimentosRedeCatarina.objects.create(
            medida_protetiva=self.medida,
            responsavel=self.usuario,
            situacao_vitima='segura',
            descricao_atendimento='Teste.',
        )
        self.assertIn(str(self.medida.ID), str(atendimento))

    def test_notificacao_enviada_default_false(self):
        """notificacao_enviada deve iniciar como False."""
        atendimento = AtendimentosRedeCatarina.objects.create(
            medida_protetiva=self.medida,
            responsavel=self.usuario,
            situacao_vitima='segura',
            descricao_atendimento='Teste.',
        )
        self.assertFalse(atendimento.notificacao_enviada)

    def test_descumprimento_default_false(self):
        """vitima_relatou_descumprimento deve iniciar como False."""
        atendimento = AtendimentosRedeCatarina.objects.create(
            medida_protetiva=self.medida,
            responsavel=self.usuario,
            situacao_vitima='segura',
            descricao_atendimento='Teste.',
        )
        self.assertFalse(atendimento.vitima_relatou_descumprimento)

    def test_ordering_por_data_decrescente(self):
        """Atendimentos devem ser ordenados por data decrescente."""
        a1 = AtendimentosRedeCatarina.objects.create(
            medida_protetiva=self.medida,
            responsavel=self.usuario,
            situacao_vitima='segura',
            descricao_atendimento='Primeiro.',
        )
        a2 = AtendimentosRedeCatarina.objects.create(
            medida_protetiva=self.medida,
            responsavel=self.usuario,
            situacao_vitima='segura',
            descricao_atendimento='Segundo.',
        )
        atendimentos = list(AtendimentosRedeCatarina.objects.all())
        self.assertEqual(atendimentos[0], a2)


class TipoAtendimentoModelTest(TestCase):
    """Testes do model TipoAtendimento (Polícia Penal)."""

    def test_criacao_tipo_atendimento(self):
        """TipoAtendimento deve ser criado com nome."""
        tipo = TipoAtendimento.objects.create(nome='Acompanhamento psicológico')
        self.assertEqual(str(tipo), 'Acompanhamento psicológico')