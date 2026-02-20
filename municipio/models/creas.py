# municipio/models/creas.py
# Modelos proxy para filtrar atendimentos do CREAS no admin

from django.db import models
from seguranca_publica.models.penal import ModeloPenal, tipo_atendimento


class CREASAtendimentoManager(models.Manager):
    """Manager que filtra apenas atendimentos do CREAS."""
    def get_queryset(self):
        return super().get_queryset().filter(
            atendimento__instituicao_responsavel='CREAS'
        )


class CREASTipoAtendimentoManager(models.Manager):
    """Manager que filtra apenas tipos de atendimento do CREAS."""
    def get_queryset(self):
        return super().get_queryset().filter(
            instituicao_responsavel='CREAS'
        )


class AtendimentoCREAS(ModeloPenal):
    """Proxy model para atendimentos do CREAS."""
    objects = CREASAtendimentoManager()

    class Meta:
        proxy = True
        verbose_name = 'Atendimento CREAS'
        verbose_name_plural = 'Atendimentos CREAS'


class TipoAtendimentoCREAS(tipo_atendimento):
    """Proxy model para tipos de atendimento do CREAS."""
    objects = CREASTipoAtendimentoManager()

    class Meta:
        proxy = True
        verbose_name = 'Tipo de Atendimento CREAS'
        verbose_name_plural = 'Tipos de Atendimento CREAS'