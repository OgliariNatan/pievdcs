from django.db import models
from .base import OcorrenciaBase
from django.utils import timezone
from seguranca_publica.models.base import Vitima_dados
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from usuarios.models import CustomUser

tipo_de_patrulha_choices = [
    ("EM", "Emergência 190"),
    ("PM", "Policiamento Montado"),
    ("TP", "Pelotão de Patrulhamento Tático"),
    ("RP", "Radio Patrulha"),
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

SITUACAO_VITIMA_CHOICES = [
    ('segura', 'Segura'),
    ('apreensiva', 'Apreensiva'),
    ('risco', 'Em situação de risco'),
    ('nao_encontrada', 'Não encontrada'),
]


class Patrulhamento(models.Model):
    """Modelo de patrulhamento da Polícia Militar."""
    nome_patrulha = models.CharField(
        max_length=15,
        verbose_name='Patrulha:',
    )
    equipe = models.CharField(
        max_length=15,
        verbose_name="Equipe",
    )

    def __str__(self):
        return self.nome_patrulha

    class Meta:
        verbose_name = "Patrulhamento"
        verbose_name_plural = "Patrulhamentos"


class OcorrenciaMilitar(OcorrenciaBase):
    """Registro de ocorrências da Polícia Militar."""
    vtr = models.CharField(max_length=20, verbose_name="VTR")
    horario = models.DateTimeField(auto_now=True)
    equipe = models.CharField(max_length=15, verbose_name="Equipe")
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


class AtendimentosRedeCatarina(models.Model):
    """Registro de atendimentos da Rede Catarina vinculados a medidas protetivas."""

    medida_protetiva = models.ForeignKey(
        FormularioMedidaProtetiva,
        on_delete=models.CASCADE,
        related_name='atendimentos_rede_catarina',
        verbose_name="Medida Protetiva Associada",
    )

    responsavel = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável pelo atendimento",
    )

    tipo_patrulha = models.CharField(
        verbose_name="Tipo de patrulha",
        max_length=4,
        choices=tipo_de_patrulha_choices,
        default="RP",
    )

    equipe = models.CharField(
        max_length=50,
        verbose_name="Equipe/Viatura",
        blank=True,
    )

    houve_contato_vitima = models.BooleanField(
        default=False,
        verbose_name="Houve contato com a vítima?",
    )

    situacao_vitima = models.CharField(
        max_length=20,
        choices=SITUACAO_VITIMA_CHOICES,
        default='segura',
        verbose_name="Situação da vítima",
    )

    agressor_presente = models.BooleanField(
        default=False,
        verbose_name="O agressor estava presente no local?",
    )

    vitima_relatou_descumprimento = models.BooleanField(
        default=False,
        verbose_name="A vítima relatou descumprimento da medida protetiva?",
    )

    descricao_descumprimento = models.TextField(
        blank=True,
        verbose_name="Descrição do descumprimento",
        help_text="Descreva os detalhes do descumprimento relatado pela vítima.",
    )

    providencias_tomadas = models.TextField(
        blank=True,
        verbose_name="Providências tomadas",
    )

    data_atendimento = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data do Atendimento",
    )

    descricao_atendimento = models.TextField(
        verbose_name="Descrição do atendimento",
    )

    notificacao_enviada = models.BooleanField(
        default=False,
        verbose_name="Notificação de descumprimento enviada?",
    )

    def __str__(self):
        return (
            f"Atendimento #{self.pk} - MP {self.medida_protetiva.ID} "
            f"em {self.data_atendimento.strftime('%d/%m/%Y %H:%M')}"
        )

    class Meta:
        verbose_name = "Atendimento da Rede Catarina"
        verbose_name_plural = "Atendimentos da Rede Catarina"
        ordering = ['-data_atendimento']