# sistema_justica/tests/test_models.py
"""Testes dos models do app sistema_justica."""

from django.test import TestCase
from django.core.exceptions import ValidationError

from sistema_justica.models.defensoria_publica import (
    FormularioMedidaProtetiva,
    default_periodo_mp,
    validador_eproc,
)
from sistema_justica.models.base import Vitima_dados, Agressor_dados
from datetime import date


def criar_vitima():
    return Vitima_dados.objects.create(
        nome='Maria Teste',
        cpf='111.222.333-44',
        data_nascimento='1992-03-15',
    )


def criar_agressor():
    return Agressor_dados.objects.create(
        nome='Carlos Teste',
        cpf='555.666.777-88',
        data_nascimento='1988-07-20',
    )


class DefaultPeriodoMpTest(TestCase):
    """Testes da função default_periodo_mp."""

    def test_retorna_data_futura(self):
        """Deve retornar data maior que hoje."""
        resultado = default_periodo_mp()
        self.assertGreater(resultado, date.today())

    def test_retorna_100_anos_no_futuro(self):
        """Deve retornar aproximadamente 100 anos no futuro."""
        from datetime import date
        from dateutil.relativedelta import relativedelta
        esperado = date.today() + relativedelta(years=100)
        resultado = default_periodo_mp()
        self.assertEqual(resultado.year, esperado.year)


class ValidadorEprocTest(TestCase):
    """Testes do validador de número eProc CNJ."""

    def test_eproc_valido(self):
        """20 dígitos numéricos devem passar sem erro."""
        try:
            validador_eproc('80000764420228240042')
        except ValidationError:
            self.fail('validador_eproc lançou ValidationError para valor válido.')

    def test_eproc_com_letras_invalido(self):
        """eProc com letras deve lançar ValidationError."""
        with self.assertRaises(ValidationError):
            validador_eproc('8000076442022824004A')

    def test_eproc_menos_de_20_digitos(self):
        """eProc com menos de 20 dígitos deve lançar ValidationError."""
        with self.assertRaises(ValidationError):
            validador_eproc('1234567890')

    def test_eproc_mais_de_20_digitos(self):
        """eProc com mais de 20 dígitos deve lançar ValidationError."""
        with self.assertRaises(ValidationError):
            validador_eproc('800007644202282400421')

    def test_eproc_com_pontuacao_invalido(self):
        """eProc no formato mascarado deve falhar (deve guardar só números)."""
        with self.assertRaises(ValidationError):
            validador_eproc('8000076-44.2022.8.24.0042')


class FormularioMedidaProtetivaModelTest(TestCase):
    """Testes do model FormularioMedidaProtetiva."""

    def setUp(self):
        self.vitima = criar_vitima()
        self.agressor = criar_agressor()

    def test_criacao_basica(self):
        """Model deve ser criado com campos mínimos."""
        mp = FormularioMedidaProtetiva.objects.create(
            vitima=self.vitima,
            agressor=self.agressor,
            possivel_causa='Violência física',
            bairro_mp='Centro',
            rua_mp='Rua A',
            n_casa_mp='1',
        )
        self.assertIsNotNone(mp.pk)

    def test_str_retorna_string(self):
        mp = FormularioMedidaProtetiva.objects.create(
            vitima=self.vitima,
            agressor=self.agressor,
            possivel_causa='Teste',
            bairro_mp='Bairro',
            rua_mp='Rua',
            n_casa_mp='1',
        )
        self.assertIsInstance(str(mp), str)

    def test_eproc_formatado_com_valor(self):
        """eproc_formatado deve retornar no padrão CNJ."""
        mp = FormularioMedidaProtetiva.objects.create(
            vitima=self.vitima,
            agressor=self.agressor,
            possivel_causa='Teste',
            bairro_mp='Bairro',
            rua_mp='Rua',
            n_casa_mp='1',
            eproc='80000764420228240042',
        )
        self.assertEqual(mp.eproc_formatado(), '8000076-44.2022.8.24.0042')

    def test_eproc_formatado_sem_valor(self):
        """eproc_formatado deve retornar '—' quando vazio."""
        mp = FormularioMedidaProtetiva.objects.create(
            vitima=self.vitima,
            agressor=self.agressor,
            possivel_causa='Teste',
            bairro_mp='Bairro',
            rua_mp='Rua',
            n_casa_mp='1',
        )
        self.assertEqual(mp.eproc_formatado(), '—')

    def test_periodo_mp_default(self):
        """periodo_mp deve ter valor padrão (~100 anos no futuro)."""
        mp = FormularioMedidaProtetiva.objects.create(
            vitima=self.vitima,
            agressor=self.agressor,
            possivel_causa='Teste',
            bairro_mp='Bairro',
            rua_mp='Rua',
            n_casa_mp='1',
        )
        self.assertGreater(mp.periodo_mp, date.today())