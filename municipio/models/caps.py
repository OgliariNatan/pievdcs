# municipio/models/caps.py
# Modelos proxy para filtrar atendimentos do CAPS no admin

from django.db import models
from seguranca_publica.models.penal import ModeloPenal, tipo_atendimento


class CAPSAtendimentoManager(models.Manager):
    """Manager que filtra apenas atendimentos do CAPS."""
    def get_queryset(self):
        return super().get_queryset().filter(
            atendimento__instituicao_responsavel='CAPS'
        )


class CAPSTipoAtendimentoManager(models.Manager):
    """Manager que filtra apenas tipos de atendimento do CAPS."""
    def get_queryset(self):
        return super().get_queryset().filter(
            instituicao_responsavel='CAPS'
        )


class AtendimentoCAPS(ModeloPenal):
    """Proxy model para atendimentos do CAPS."""
    objects = CAPSAtendimentoManager()

    class Meta:
        proxy = True
        verbose_name = 'Atendimento CAPS'
        verbose_name_plural = 'Atendimentos CAPS'


class TipoAtendimentoCAPS(tipo_atendimento):
    """Proxy model para tipos de atendimento do CAPS."""
    objects = CAPSTipoAtendimentoManager()

    class Meta:
        proxy = True
        verbose_name = 'Tipo de Atendimento CAPS'
        verbose_name_plural = 'Tipos de Atendimento CAPS'