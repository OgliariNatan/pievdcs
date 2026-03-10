# seguranca_publica/tests/test_forms.py
"""Testes dos formulários do app seguranca_publica."""

from django.test import TestCase
from seguranca_publica.forms.militar import AtendimentoRedeCatarinaForm


class AtendimentoRedeCatarinaFormTest(TestCase):
    """Testes do formulário de atendimento da Rede Catarina."""

    def _dados_validos(self, **kwargs):
        base = {
            'situacao_vitima': 'segura',
            'descricao_atendimento': 'Atendimento de rotina sem intercorrências.',
            'agressor_presente': False,
            'vitima_relatou_descumprimento': False,
        }
        base.update(kwargs)
        return base

    def test_form_valido(self):
        form = AtendimentoRedeCatarinaForm(data=self._dados_validos())
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_sem_descricao_invalido(self):
        dados = self._dados_validos()
        dados.pop('descricao_atendimento')
        form = AtendimentoRedeCatarinaForm(data=dados)
        self.assertFalse(form.is_valid())
        self.assertIn('descricao_atendimento', form.errors)

    def test_form_sem_situacao_invalido(self):
        dados = self._dados_validos()
        dados.pop('situacao_vitima')
        form = AtendimentoRedeCatarinaForm(data=dados)
        self.assertFalse(form.is_valid())
        self.assertIn('situacao_vitima', form.errors)