
from django.db import models
from .base import OcorrenciaBase
from seguranca_publica.models.base import Vitima_dados

tipo_de_patrulha_choices = [
    ("EM", "Emergência 190"),
    ("PM", "Policiamento Montado"),
    ("TP","Pelotão de Patrulhamento Tático"),
    ("RP", "Radio Patrulha "),
    ("PE", "Policiamento de Eventos"),
    ("OA", "Operações de Aviação Policial"),
    ("OE", "Operações Especiais"),
    ("PC", "Policiamento com Cães"),
    ("PB", "Policiamento ostensivo com bicicleta"),
    ("PP", "Policiamento Ostensivo a Pé"),
    ("PR", "Policiamento com Motocicleta"),
    ("P2", "Agência de Inteligência"),
    ("PS", "Policiamento em Praias"),
    ("PT", "Policiamento Ostensivo de Trânsito"),
]

class Patrulhamento(models.Model):
   pass


class OcorrenciaMilitar(OcorrenciaBase):
    vtr = models.CharField(
        max_length=20,
        verbose_name="VTR",
    )
    horario = models.DateTimeField(
        auto_now=True,
    )
    equipe = models.ForeignKey(
        Patrulhamento,
        on_delete=models.SET_NULL,

        null=True,
        verbose_name="Equipe",
    )
    tipo_patrulha = models.CharField(
        verbose_name="Patrulha",
        default="RP",
        max_length=4,
        choices=tipo_de_patrulha_choices,
    )