# municipio/models/secretaria_saude.py
# Modelos proxy para filtrar atendimentos da Secretaria da Saúde no admin

from django.db import models
from seguranca_publica.models.penal import ModeloPenal, tipo_atendimento
from sistema_justica.models.base import Municipio, Estado, Vitima_dados, Agressor_dados
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva


class UnidadesSaude(models.Model):
    """Modelo para representar as unidades de saúde do município."""
    nome = models.CharField(max_length=255)
    CNES = models.CharField(max_length=20, unique=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True)
    endereco = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.nome 

class FormularioSINAN(models.Model):
    """
    Formulário SINAN preenchido pela Secretaria da Saúde.
    Vítima e agressor são obtidos diretamente da MPU vinculada.
    """
    mpu = models.ForeignKey(
        FormularioMedidaProtetiva,
        on_delete=models.CASCADE,
        related_name='sinan_formularios',
        verbose_name='Medida Protetiva',
    )
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Município do Atendimento',
    )
    estado = models.ForeignKey(
        Estado,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Estado do Atendimento',
    )
    data_atendimento = models.DateField(verbose_name='Data do Atendimento')

    cartao_sus = models.CharField(max_length=20, blank=True, verbose_name='Cartão SUS')
    

    # --- Propriedades que lêem diretamente da MPU ---

    @property
    def vitima(self):
        """Retorna a vítima vinculada à MPU."""
        return self.mpu.vitima

    @property
    def agressor(self):
        """Retorna o agressor vinculado à MPU."""
        return self.mpu.agressor

    def __str__(self):
        nome_vitima = self.mpu.vitima.nome if self.mpu.vitima else 'N/I'
        return f'Formulário SINAN - {nome_vitima} - {self.data_atendimento}'

    class Meta:
        verbose_name = 'Formulário SINAN'
        verbose_name_plural = 'Formulários SINAN'
        ordering = ['-data_atendimento']


class SecSaudeAtendimentoManager(models.Manager):
    """Manager que filtra apenas atendimentos da Secretaria da Saúde."""
    def get_queryset(self):
        return super().get_queryset().filter(
            atendimento__instituicao_responsavel='Secretaria da Saúde'
        )


class SecSaudeTipoAtendimentoManager(models.Manager):
    """Manager que filtra apenas tipos de atendimento da Secretaria da Saúde."""
    def get_queryset(self):
        return super().get_queryset().filter(
            instituicao_responsavel='Secretaria da Saúde'
        )


class AtendimentoSecSaude(ModeloPenal):
    """Proxy model para atendimentos da Secretaria da Saúde."""
    objects = SecSaudeAtendimentoManager()

    class Meta:
        proxy = True
        verbose_name = 'Atendimento Secretaria da Saúde'
        verbose_name_plural = 'Atendimentos Secretaria da Saúde'


class TipoAtendimentoSecSaude(tipo_atendimento):
    """Proxy model para tipos de atendimento da Secretaria da Saúde."""
    objects = SecSaudeTipoAtendimentoManager()

    class Meta:
        proxy = True
        verbose_name = 'Tipo de Atendimento Sec. Saúde'
        verbose_name_plural = 'Tipos de Atendimento Sec. Saúde'