# sistema_justica/tests/test_forms.py
"""Testes dos formulários do app sistema_justica."""

from django.test import TestCase
from sistema_justica.forms.utils import validar_eproc
from django import forms as django_forms


class ValidarEprocUtilsTest(TestCase):
    """Testes da função utilitária validar_eproc."""

    def test_retorna_none_para_vazio(self):
        """Valor None ou vazio deve retornar None sem erro."""
        self.assertIsNone(validar_eproc(None))
        self.assertIsNone(validar_eproc(''))

    def test_retorna_valor_valido(self):
        """20 dígitos devem ser retornados sem alteração."""
        resultado = validar_eproc('80000764420228240042')
        self.assertEqual(resultado, '80000764420228240042')

    def test_levanta_erro_com_letras(self):
        with self.assertRaises(django_forms.ValidationError):
            validar_eproc('8000076442022824004X')

    def test_levanta_erro_com_19_digitos(self):
        with self.assertRaises(django_forms.ValidationError) as ctx:
            validar_eproc('1234567890123456789')
        self.assertIn('20 dígitos', str(ctx.exception))

    def test_levanta_erro_com_21_digitos(self):
        with self.assertRaises(django_forms.ValidationError):
            validar_eproc('123456789012345678901')