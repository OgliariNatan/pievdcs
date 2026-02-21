# municipio/models/cras.py
# Modelos proxy para filtrar atendimentos do CRAS no admin

from django.db import models
from seguranca_publica.models.penal import ModeloPenal, tipo_atendimento


class CRASAtendimentoManager(models.Manager):
    """Manager que filtra apenas atendimentos do CRAS."""
    def get_queryset(self):
        return super().get_queryset().filter(
            atendimento__instituicao_responsavel='CRAS'
        )


class CRASTipoAtendimentoManager(models.Manager):
    """Manager que filtra apenas tipos de atendimento do CRAS."""
    def get_queryset(self):
        return super().get_queryset().filter(
            instituicao_responsavel='CRAS'
        )


class AtendimentoCRAS(ModeloPenal):
    """Proxy model para atendimentos do CRAS."""
    objects = CRASAtendimentoManager()

    class Meta:
        proxy = True
        verbose_name = 'Atendimento CRAS'
        verbose_name_plural = 'Atendimentos CRAS'


class TipoAtendimentoCRAS(tipo_atendimento):
    """Proxy model para tipos de atendimento do CRAS."""
    objects = CRASTipoAtendimentoManager()

    class Meta:
        proxy = True
        verbose_name = 'Tipo de Atendimento CRAS'
        verbose_name_plural = 'Tipos de Atendimento CRAS'