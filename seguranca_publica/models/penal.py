# Models da Polícia Penal

# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from sistema_justica.models.base import Agressor_dados, Municipio, Estado
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField, GroupedForeignKey





setor_choices = (
    ('Assistente Social', 'Assistente Social'),
    ('Psicóloga', 'Psicóloga'),
    ('Enfermagem', 'Enfermagem'),
    ('Grupo refletivo', 'Grupo refletivo'),
    ('Outros', 'Outros'),
)

classe_atendimento_choices = (
    ('Atendimento Individual', 'Atendimento Individual'),
    ('Atendimento em Grupo', 'Atendimento em Grupo'),
)

instituicao_choices = (
    ('Policia Penal', 'Policia Penal'),
    ('Policia Civil', 'Policia Civil'),
    ('Policia Militar', 'Policia Militar'),
    ('Centro de Atendimento Socioeducativo', 'Centro de Atendimento Socioeducativo'),
    ('Centro de Referência Especializado de Assistência Social', 'Centro de Referência Especializado de Assistência Social'),
    ('Centro de Atenção Psicossocial', 'Centro de Atenção Psicossocial'),
)

tematica_choices = (
    ('Saúde', 'Saúde'),
    ('Educação', 'Educação'),
    ('Trabalho', 'Trabalho'),
    ('Assistência Social', 'Assistência Social'),
    ('Direitos Humanos', 'Direitos Humanos'),
    ('Segurança Pública', 'Segurança Pública'),
    ('Psicologia', 'Psicologia'),
    ('Outros', 'Outros'),
)


class tipo_atendimento(models.Model):
    instituicao_responsavel = models.CharField(
        max_length=100, 
        verbose_name="Nome da Instituição responsável", 
        choices=instituicao_choices, 
        default='Policia Penal'
    )
    #busca_instituicao_responsavel = Q(filter=instituicao_responsavel)
    
    tematica = models.CharField(
        max_length=100, 
        verbose_name="Temática", 
        choices=tematica_choices, 
        default='Saúde'
    )

    def __str__(self):
        return f"{self.instituicao_responsavel} - {self.tematica}"

    class Meta:
        verbose_name = 'Tipo de Atendimento'
        verbose_name_plural = 'Tipos de Atendimentos'


class ModeloPenal(models.Model):
    """
    Classe base para os modelos, Penal.
    """
    id = models.AutoField(primary_key=True)
    data_atendimento = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Data do Atendimento"
    )
    tempo_atendimento = models.DurationField(
        verbose_name="Tempo de Atendimento",
        blank=True, null=True
    )
    setor_atendimento = models.CharField(
        max_length=50, 
        verbose_name="Setor de Atendimento", 
        choices=setor_choices, 
        default='assistente social'
    )
    atendimento = models.ForeignKey(
        tipo_atendimento, 
        on_delete=models.CASCADE, 
        verbose_name="Grupo de Atendimento", 
        related_name='grupo_atendimento', 
        null=True, blank=True
    )
    agressores_atendidos = models.ManyToManyField(
        Agressor_dados,
        verbose_name='Participantes do Grupo',
        related_name='agressores_atendidos',
        blank=True,
        
    )
    
    avaliacao = models.TextField(
        verbose_name="Avaliação do Atendimento", 
        blank=True, null=True
    )
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        verbose_name="Usuário", 
        null=True, blank=True
    )
    teste = models.BooleanField(default=False, verbose_name="Teste")


    def __str__(self):
        return f"{self.data_atendimento} - {self.setor_atendimento} - {self.atendimento} - {self.usuario}"
    class Meta:
        verbose_name = "Modelo Penal"
        verbose_name_plural = "Modelos Penais"
        ordering = ['-data_atendimento']
        permissions = [
            ("Policia Penal", "Policia Penal"),
        ]
    