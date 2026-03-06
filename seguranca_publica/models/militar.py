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

TIPO_ANEXO_CHOICES = [
    ('imagem', 'Imagem'),
    ('video', 'Vídeo'),
    #('documento', 'Documento'),
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

def _upload_path_imagem(instance, filename):
    """Gera caminho de upload para imagens: anexos/sistema_justica/PM/IMG/<atendimento_pk>/"""
    return f'sistema_justica/PM/IMG/{instance.atendimento.pk}/{filename}'


def _upload_path_video(instance, filename):
    """Gera caminho de upload para vídeos: anexos/sistema_justica/PM/Video/<atendimento_pk>/"""
    return f'sistema_justica/PM/Video/{instance.atendimento.pk}/{filename}'


class AnexoAtendimento(models.Model):
    """Imagem ou vídeo anexado como prova a um atendimento da Rede Catarina."""

    atendimento = models.ForeignKey(
        AtendimentosRedeCatarina,
        on_delete=models.CASCADE,
        related_name='anexos',
        verbose_name="Atendimento",
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_ANEXO_CHOICES,
        verbose_name="Tipo de anexo",
    )

    imagem = models.ImageField(
        upload_to=_upload_path_imagem,
        blank=True,
        null=True,
        verbose_name="Imagem",
    )

    video = models.FileField(
        upload_to=_upload_path_video,
        blank=True,
        null=True,
        verbose_name="Vídeo",
    )

    descricao = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descrição do anexo",
    )

    data_upload = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data do upload",
    )

    def __str__(self):
        return f"{self.get_tipo_display()} #{self.pk} — Atendimento #{self.atendimento.pk}"

    @property
    def arquivo(self):
        """Retorna o campo de arquivo ativo (imagem ou vídeo)."""
        return self.imagem if self.tipo == 'imagem' else self.video

    class Meta:
        verbose_name = "Anexo do Atendimento"
        verbose_name_plural = "Anexos do Atendimento"
        ordering = ['-data_upload']