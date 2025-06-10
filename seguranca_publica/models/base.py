
from django.db import models
from django.utils import timezone
from sistema_justica.models.base import Vitima_dados, Agressor_dados

tipo_de_violencia_choices = (
    ('Fisica', 'Física'),
    ('Psicologica', 'Psicológica'),
    ('Sexual', 'Sexual'),
    ('Patrimonial', 'Patrimonial'),
    ('Moral', 'Moral'),
)


grau_parentesco_agressor_choices = (
    ('Pai', 'Pai'),
    ('Tio', 'Tio'),
    ('Conjuge', 'Cônjuge'),
    ('Filho', 'Filho'),
    ('Cunhado', 'Cunhado'),
    ('Padasto', 'Padastro'),
    ('Outros', 'Outros'),
)

class OcorrenciaBase(models.Model):
    numero_ocorrencia = models.AutoField(
        primary_key=True,  
        verbose_name="nº",
    )

    data = models.DateTimeField(default=timezone.now, verbose_name="Data")
    #local = models.CharField(max_length=255, verbose_name="Local da Ocorrência")
    vitima = models.ForeignKey(
        Vitima_dados, 
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    agressor = models.ForeignKey(
        Agressor_dados, 
        on_delete= models.CASCADE, 
        null=True, blank=True,
    )
    tipo_de_violencia = models.CharField(
        max_length= 50, 
        choices= tipo_de_violencia_choices, 
        verbose_name= "Tipo de Violência"
    )
    grau_parentesco_agressor = models.CharField(
        max_length= 15,
        choices= grau_parentesco_agressor_choices,
        default='Pai',
    )
    descricao = models.TextField(verbose_name="Descrição da Ocorrência")

    def __str__(self):
        return f"{self.numero_ocorrencia} - {self.data.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        abstract = True
