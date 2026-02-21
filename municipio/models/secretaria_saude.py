# municipio/models/secretaria_saude.py
# Modelos proxy para filtrar atendimentos da Secretaria da Saúde no admin

from django.db import models
from seguranca_publica.models.penal import ModeloPenal, tipo_atendimento


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