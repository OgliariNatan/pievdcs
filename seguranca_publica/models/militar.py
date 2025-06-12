
from django.db import models
from .base import OcorrenciaBase
from django.utils import timezone
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
   nome_patrulha = models.CharField(
       max_length=15,
       verbose_name='Patrulha:'
   )

   equipe = models.CharField(
        max_length=15,
        #on_delete=models.SET_NULL,
        #null=True,
        verbose_name="Equipe",
    )
   
   def __str__(self):
       return self.nome_patrulha

   class Meta:
        verbose_name = "Patrulhamento"
        verbose_name_plural = "Patrulhamentos"


class OcorrenciaMilitar(OcorrenciaBase):
    vtr = models.CharField(
        max_length=20,
        verbose_name="VTR",
    )
    horario = models.DateTimeField(
        auto_now=True,
    )
    equipe = models.CharField(
        max_length=15,
        #on_delete=models.SET_NULL,
        #null=True,
        verbose_name="Equipe",
    )
    tipo_patrulha = models.CharField(
        verbose_name="Patrulha",
        default="RP",
        max_length=4,
        choices=tipo_de_patrulha_choices,
    )

    def __str__(self):
        return self.tipo_patrulha
    
    class Meta:
        verbose_name = "Inserção da Polícia Militar"
        verbose_name_plural = "Inserções da Polícia Militar"