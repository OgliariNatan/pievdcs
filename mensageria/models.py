# Create your models here.
from django.db import models
#from django.contrib.auth.models import User, Group
from usuarios.models import CustomUser, CustomGroup
from django.utils import timezone

class TipoNotificacao(models.TextChoices):
    SISTEMA = 'SISTEMA', 'Sistema'
    ALERTA = 'ALERTA', 'Alerta'
    MENSAGEM = 'MENSAGEM', 'Mensagem'
    VIOLENCIA_DOMESTICA = 'VIOLENCIA_DOMESTICA', 'Violência Doméstica'
    CRIME_SEXUAL = 'CRIME_SEXUAL', 'Crime Sexual'
    MEDIDA_PROTETIVA = 'MEDIDA_PROTETIVA', 'Medida Protetiva'

class PrioridadeNotificacao(models.TextChoices):
    BAIXA = 'BAIXA', 'Baixa'
    NORMAL = 'NORMAL', 'Normal'
    ALTA = 'ALTA', 'Alta'
    URGENTE = 'URGENTE', 'Urgente'

class StatusNotificacao(models.TextChoices):
    NAO_LIDA = 'NAO_LIDA', 'Não Lida'
    LIDA = 'LIDA', 'Lida'
    ARQUIVADA = 'ARQUIVADA', 'Arquivada'

class Notificacao(models.Model):
    # Remetente
    remetente = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='notificacoes_enviadas',
        verbose_name='Remetente'
    )
    
    # Destinatários
    destinatario_usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificacoes_recebidas',
        verbose_name='Destinatário (Usuário)'
    )
    
    destinatario_grupo = models.ForeignKey(
        CustomGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificacoes_grupo',
        verbose_name='Destinatário (Grupo)'
    )
    
    # Conteúdo
    titulo = models.CharField(max_length=200, verbose_name='Título')
    mensagem = models.TextField(verbose_name='Mensagem')
    
    # Metadados
    tipo = models.CharField(
        max_length=30,
        choices=TipoNotificacao.choices,
        default=TipoNotificacao.SISTEMA,
        verbose_name='Tipo'
    )
    
    prioridade = models.CharField(
        max_length=10,
        choices=PrioridadeNotificacao.choices,
        default=PrioridadeNotificacao.NORMAL,
        verbose_name='Prioridade'
    )
    
    # Timestamps
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    
    # Links e referências
    url_acao = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='URL de Ação'
    )
    
    # Referências para rastreabilidade
    objeto_relacionado_tipo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Tipo do Objeto Relacionado'
    )
    objeto_relacionado_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='ID do Objeto Relacionado'
    )
    
    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-prioridade', '-data_criacao']
        indexes = [
            models.Index(fields=['-data_criacao']),
            models.Index(fields=['destinatario_usuario', '-data_criacao']),
            models.Index(fields=['destinatario_grupo', '-data_criacao']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.get_prioridade_display()}"

class StatusNotificacaoUsuario(models.Model):
    """
    Rastreia o status individual de cada notificação para cada usuário
    """
    notificacao = models.ForeignKey(
        Notificacao,
        on_delete=models.CASCADE,
        related_name='status_usuarios'
    )
    
    usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='status_notificacoes'
    )
    
    status = models.CharField(
        max_length=15,
        choices=StatusNotificacao.choices,
        default=StatusNotificacao.NAO_LIDA,
        verbose_name='Status'
    )
    
    data_leitura = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Leitura'
    )
    
    data_arquivamento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Arquivamento'
    )
    
    class Meta:
        verbose_name = 'Status de Notificação por Usuário'
        verbose_name_plural = 'Status de Notificações por Usuário'
        unique_together = ['notificacao', 'usuario']
        indexes = [
            models.Index(fields=['usuario', 'status']),
            models.Index(fields=['usuario', 'notificacao']),
        ]
    
    def marcar_como_lida(self):
        if self.status == StatusNotificacao.NAO_LIDA:
            self.status = StatusNotificacao.LIDA
            self.data_leitura = timezone.now()
            self.save()
    
    def arquivar(self):
        self.status = StatusNotificacao.ARQUIVADA
        self.data_arquivamento = timezone.now()
        self.save()# Create your models here.
from django.db import models
#from django.contrib.auth.models import User, Group
from usuarios.models import CustomUser, CustomGroup
from django.utils import timezone

class TipoNotificacao(models.TextChoices):
    SISTEMA = 'SISTEMA', 'Sistema'
    ALERTA = 'ALERTA', 'Alerta'
    MENSAGEM = 'MENSAGEM', 'Mensagem'
    VIOLENCIA_DOMESTICA = 'VIOLENCIA_DOMESTICA', 'Violência Doméstica'
    CRIME_SEXUAL = 'CRIME_SEXUAL', 'Crime Sexual'
    MEDIDA_PROTETIVA = 'MEDIDA_PROTETIVA', 'Medida Protetiva'

class PrioridadeNotificacao(models.TextChoices):
    BAIXA = 'BAIXA', 'Baixa'
    NORMAL = 'NORMAL', 'Normal'
    ALTA = 'ALTA', 'Alta'
    URGENTE = 'URGENTE', 'Urgente'

class StatusNotificacao(models.TextChoices):
    NAO_LIDA = 'NAO_LIDA', 'Não Lida'
    LIDA = 'LIDA', 'Lida'
    ARQUIVADA = 'ARQUIVADA', 'Arquivada'

class Notificacao(models.Model):
    # Remetente
    remetente = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='notificacoes_enviadas',
        verbose_name='Remetente'
    )
    
    # Destinatários
    destinatario_usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificacoes_recebidas',
        verbose_name='Destinatário (Usuário)'
    )
    
    destinatario_grupo = models.ForeignKey(
        CustomGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificacoes_grupo',
        verbose_name='Destinatário (Grupo)'
    )
    
    # Conteúdo
    titulo = models.CharField(max_length=200, verbose_name='Título')
    mensagem = models.TextField(verbose_name='Mensagem')
    
    # Metadados
    tipo = models.CharField(
        max_length=30,
        choices=TipoNotificacao.choices,
        default=TipoNotificacao.SISTEMA,
        verbose_name='Tipo'
    )
    
    prioridade = models.CharField(
        max_length=10,
        choices=PrioridadeNotificacao.choices,
        default=PrioridadeNotificacao.NORMAL,
        verbose_name='Prioridade'
    )
    
    # Timestamps
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    
    # Links e referências
    url_acao = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='URL de Ação'
    )
    
    # Referências para rastreabilidade
    objeto_relacionado_tipo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Tipo do Objeto Relacionado'
    )
    objeto_relacionado_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='ID do Objeto Relacionado'
    )
    
    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-prioridade', '-data_criacao']
        indexes = [
            models.Index(fields=['-data_criacao']),
            models.Index(fields=['destinatario_usuario', '-data_criacao']),
            models.Index(fields=['destinatario_grupo', '-data_criacao']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.get_prioridade_display()}"

class StatusNotificacaoUsuario(models.Model):
    """
    Rastreia o status individual de cada notificação para cada usuário
    """
    notificacao = models.ForeignKey(
        Notificacao,
        on_delete=models.CASCADE,
        related_name='status_usuarios'
    )
    
    usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='status_notificacoes'
    )
    
    status = models.CharField(
        max_length=15,
        choices=StatusNotificacao.choices,
        default=StatusNotificacao.NAO_LIDA,
        verbose_name='Status'
    )
    
    data_leitura = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Leitura'
    )
    
    data_arquivamento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Arquivamento'
    )
    
    class Meta:
        verbose_name = 'Status de Notificação por Usuário'
        verbose_name_plural = 'Status de Notificações por Usuário'
        unique_together = ['notificacao', 'usuario']
        indexes = [
            models.Index(fields=['usuario', 'status']),
            models.Index(fields=['usuario', 'notificacao']),
        ]
    
    def marcar_como_lida(self):
        if self.status == StatusNotificacao.NAO_LIDA:
            self.status = StatusNotificacao.LIDA
            self.data_leitura = timezone.now()
            self.save()
    
    def arquivar(self):
        self.status = StatusNotificacao.ARQUIVADA
        self.data_arquivamento = timezone.now()
        self.save()