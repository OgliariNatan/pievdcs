
from django.db import models
from django.utils import timezone
from sistema_justica.models.base import Vitima_dados, Agressor_dados, Municipio, Estado
from MAIN.cadastros_padrao import agressor_padrao
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField, GroupedForeignKey
from sistema_justica.models.poder_judiciario import ComarcasPoderJudiciario


tipo_de_violencia_choices = (
    ('Fisica', 'Física'),
    ('Psicologica', 'Psicológica'),
    ('Sexual', 'Sexual'),
    ('Patrimonial', 'Patrimonial'),
    ('Moral', 'Moral'),
)

status_MP_choices = [
    ("SO", "Solicitada"),
    ('NO', 'Não Solicitada'),
    ("AP", "Aprovada"),
    ("RE", "Rejeitada"),
    ("CA", "Cancelada"),
    ("AT", "Ativa"),
    ("EV", "Em Vigor"),
]

grau_parentesco_agressor_choices = (
    ('Pai', 'Pai'),
    ('Tio', 'Tio'),
    ('Conjuge', 'Cônjuge'),
    ('Filho', 'Filho'),
    ('Cunhado', 'Cunhado'),
    ('Padasto', 'Padastro'),
    ('Primo', 'Primo/Prima'),
    ('Irmao', 'Irmão'),
    ('ex-Conjuge', 'Ex-Cônjuge'),
    ('amigo', 'Amigo da família'),
    ('Outros', 'Outros'),
)

class OcorrenciaBase(models.Model):
    id = models.AutoField(
        primary_key=True,  
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
        on_delete=models.SET_DEFAULT,
        default=agressor_padrao, 
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
        default='Conjuge',
    )
    
    comarca_competente = models.ForeignKey(
        ComarcasPoderJudiciario,
        on_delete=models.CASCADE,
        verbose_name='Comarca',
        null=True, 
        blank=True
    )

    #Municipio da ocorrencia
    Estado = models.ForeignKey(
        Estado,
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="Estado",
    )

    municipio_ocorrencia = ChainedForeignKey(
        Municipio,
        chained_field="Estado",
        chained_model_field="estado",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="Município",
    )

    bairro_ocorrencia = models.CharField(
        max_length=150,
        verbose_name='Bairro',
        blank=False,
    )

    status_MP = models.CharField(# devemos soliciatar na ocorrencia
        max_length=2,
        choices=status_MP_choices,
        verbose_name="Status da Medida Protetiva",
        default="SO",
        null=True, blank=True,
    )
    
    possivel_causa = models.CharField(
        max_length= 25,
        verbose_name= "Possível Causa",
    )

    descricao = models.TextField(
        verbose_name="Descrição da Ocorrência",
    )

    def __str__(self):
        return f"Ocorrência: {self.id} - {self.data.strftime('%d/%m/%Y')}"

    class Meta:
        abstract = True
