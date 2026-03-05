# Create your models here.
from django.db import models
from django.contrib.auth.models import Group as CustomGroup
from usuarios.models import CustomUser
from django.utils import timezone

class TipoNotificacao(models.TextChoices):
    SISTEMA = 'SISTEMA', 'Sistema'
    ALERTA = 'ALERTA', 'Alerta'
    MENSAGEM = 'MENSAGEM', 'Mensagem'
    VIOLENCIA_DOMESTICA = 'VIOLENCIA_DOMESTICA', 'Violência Doméstica'
    CRIME_SEXUAL = 'CRIME_SEXUAL', 'Crime Sexual'
    MEDIDA_PROTETIVA = 'MEDIDA_PROTETIVA', 'Medida Protetiva'
    ENCAMINHAMENTO = 'ENCAMINHAMENTO', 'Encaminhamento'

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
    """
    Modelo unificado para notificações do sistema PIEVDCS
    Gerencia tanto notificações individuais quanto para grupos
    """
    
    # Remetente - será preenchido automaticamente com o usuário logado
    remetente = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='notificacoes_enviadas',
        verbose_name='Remetente',
        help_text='Preenchido automaticamente com o usuário atual'
    )
    
    # Destinatários - Pode ser usuário OU grupo
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
    
    # Para notificações de grupo, rastrear qual usuário específico já leu
    usuarios_que_leram = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name='notificacoes_lidas',
        verbose_name='Usuários que Leram'
    )
    
    usuarios_que_arquivaram = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name='notificacoes_arquivadas',
        verbose_name='Usuários que Arquivaram'
    )
    
    # Conteúdo
    titulo = models.CharField(
        max_length=200, 
        verbose_name='Título*'
    )
    
    mensagem = models.TextField(
        verbose_name='Mensagem*'
    )
    
    # Metadados
    tipo = models.CharField(
        max_length=30,
        choices=TipoNotificacao.choices,
        default=TipoNotificacao.SISTEMA,
        verbose_name='Tipo de Notificação'
    )
    
    prioridade = models.CharField(
        max_length=10,
        choices=PrioridadeNotificacao.choices,
        default=PrioridadeNotificacao.NORMAL,
        verbose_name='Prioridade'
    )
    
    # Status para notificações individuais
    status = models.CharField(
        max_length=15,
        choices=StatusNotificacao.choices,
        default=StatusNotificacao.NAO_LIDA,
        verbose_name='Status',
        help_text='Status para notificações individuais'
    )
    
    # Timestamps principais
    data_criacao = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Data de Criação'
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True, 
        verbose_name='Data de Atualização'
    )
    
    # Timestamp de leitura para notificações individuais
    data_leitura = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Leitura',
        help_text='Para notificações individuais'
    )
    
    data_arquivamento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Arquivamento',
        help_text='Para notificações individuais'
    )
    
    # Referências para rastreabilidade
    objeto_relacionado_tipo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Tipo do Objeto Relacionado',
        help_text='Ex: FormularioMedidaProtetiva, Vitima_dados'
    )
    
    objeto_relacionado_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='ID do Objeto Relacionado'
    )
    
    # Flag para notificações importantes
    importante = models.BooleanField(
        default=False,
        verbose_name='Importante',
        help_text='Marca notificação como importante'
    )
    
    # Expiração opcional
    data_expiracao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Expiração',
        help_text='Após esta data, a notificação não será mais exibida'
    )
    
    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-importante', '-prioridade', '-data_criacao']
        indexes = [
            models.Index(fields=['-data_criacao']),
            models.Index(fields=['destinatario_usuario', 'status', '-data_criacao']),
            models.Index(fields=['destinatario_grupo', '-data_criacao']),
            models.Index(fields=['tipo', '-data_criacao']),
            models.Index(fields=['prioridade', '-data_criacao']),
        ]
    
    def __str__(self):
        destinatario = self.destinatario_usuario or self.destinatario_grupo
        return f"{self.titulo} - {destinatario} - {self.get_prioridade_display()}"
    
    def save(self, *args, **kwargs):
        """Validação para garantir que tenha um destinatário"""
        if not self.destinatario_usuario and not self.destinatario_grupo:
            raise ValueError("A notificação deve ter um destinatário (usuário ou grupo)")
        
        if self.destinatario_usuario and self.destinatario_grupo:
            raise ValueError("A notificação deve ter apenas um tipo de destinatário")
        
        super().save(*args, **kwargs)
    
    # Métodos para notificações individuais
    def marcar_como_lida(self):
        """Marca notificação individual como lida"""
        if self.destinatario_usuario and self.status == StatusNotificacao.NAO_LIDA:
            self.status = StatusNotificacao.LIDA
            self.data_leitura = timezone.now()
            self.save()
            return True
        return False
    
    def arquivar(self):
        """Arquiva notificação individual"""
        if self.destinatario_usuario:
            self.status = StatusNotificacao.ARQUIVADA
            self.data_arquivamento = timezone.now()
            self.save()
            return True
        return False
    
    # Métodos para notificações de grupo
    def marcar_lida_por_usuario(self, usuario):
        """Marca notificação de grupo como lida por um usuário específico"""
        if self.destinatario_grupo and usuario not in self.usuarios_que_leram.all():
            self.usuarios_que_leram.add(usuario)
            return True
        return False
    
    def arquivar_por_usuario(self, usuario):
        """Arquiva notificação de grupo para um usuário específico"""
        if self.destinatario_grupo and usuario not in self.usuarios_que_arquivaram.all():
            self.usuarios_que_arquivaram.add(usuario)
            return True
        return False
    
    def foi_lida_por(self, usuario):
        """Verifica se notificação foi lida por um usuário específico"""
        if self.destinatario_usuario == usuario:
            return self.status in [StatusNotificacao.LIDA, StatusNotificacao.ARQUIVADA]
        elif self.destinatario_grupo:
            return usuario in self.usuarios_que_leram.all()
        return False
    
    def foi_arquivada_por(self, usuario):
        """Verifica se notificação foi arquivada por um usuário específico"""
        if self.destinatario_usuario == usuario:
            return self.status == StatusNotificacao.ARQUIVADA
        elif self.destinatario_grupo:
            return usuario in self.usuarios_que_arquivaram.all()
        return False
    
    def get_status_para_usuario(self, usuario):
        """Retorna o status da notificação para um usuário específico"""
        if self.destinatario_usuario == usuario:
            return self.status
        elif self.destinatario_grupo and usuario.groups.filter(id=self.destinatario_grupo.id).exists():
            if usuario in self.usuarios_que_arquivaram.all():
                return StatusNotificacao.ARQUIVADA
            elif usuario in self.usuarios_que_leram.all():
                return StatusNotificacao.LIDA
            else:
                return StatusNotificacao.NAO_LIDA
        return None
    
    def get_url_acao(self):
        """Gera URL de ação baseado no tipo e objeto relacionado"""
        if self.objeto_relacionado_tipo and self.objeto_relacionado_id:
            # Mapear tipos para URLs
            urls_map = {
                'FormularioMedidaProtetiva': f'/sistema_justica/mpu/{self.objeto_relacionado_id}/',
                'Vitima_dados': f'/sistema_justica/vitima/{self.objeto_relacionado_id}/',
                'Agressor_dados': f'/sistema_justica/agressor/{self.objeto_relacionado_id}/',
            }
            return urls_map.get(self.objeto_relacionado_tipo, '#')
        return '#'
    
    @property
    def esta_expirada(self):
        """Verifica se a notificação expirou"""
        if self.data_expiracao:
            return timezone.now() > self.data_expiracao
        return False
    
    @classmethod
    def get_nao_lidas_usuario(cls, usuario):
        """Retorna notificações não lidas para um usuário"""
        from django.db.models import Q
        
        # Notificações individuais não lidas
        q_individuais = Q(
            destinatario_usuario=usuario,
            status=StatusNotificacao.NAO_LIDA
        )
        
        # Notificações de grupo não lidas
        grupos_usuario = usuario.groups.all()
        q_grupo = Q(
            destinatario_grupo__in=grupos_usuario
        ) & ~Q(usuarios_que_leram=usuario) & ~Q(usuarios_que_arquivaram=usuario)
        
        # Excluir expiradas
        q_nao_expirada = Q(data_expiracao__isnull=True) | Q(data_expiracao__gt=timezone.now())
        
        return cls.objects.filter(
            (q_individuais | q_grupo) & q_nao_expirada
        ).distinct()
    
    @classmethod
    def get_todas_usuario(cls, usuario):
        """Retorna todas as notificações visíveis para um usuário"""
        from django.db.models import Q
        
        # Notificações individuais
        q_individuais = Q(destinatario_usuario=usuario)
        
        # Notificações de grupo
        grupos_usuario = usuario.groups.all()
        q_grupo = Q(destinatario_grupo__in=grupos_usuario) & ~Q(usuarios_que_arquivaram=usuario)
        
        # Excluir expiradas
        q_nao_expirada = Q(data_expiracao__isnull=True) | Q(data_expiracao__gt=timezone.now())
        
        return cls.objects.filter(
            (q_individuais | q_grupo) & q_nao_expirada
        ).distinct()
    
    @classmethod
    def contar_nao_lidas_usuario(cls, usuario):
        """Conta notificações não lidas para um usuário"""
        return cls.get_nao_lidas_usuario(usuario).count()
    
    def get_cor_prioridade(self):
        """Retorna a cor CSS baseada na prioridade"""
        cores = {
            PrioridadeNotificacao.URGENTE: 'red',
            PrioridadeNotificacao.ALTA: 'amber',
            PrioridadeNotificacao.NORMAL: 'blue',
            PrioridadeNotificacao.BAIXA: 'gray'
        }
        return cores.get(self.prioridade, 'gray')
    
    def get_icone_tipo(self):
        """Retorna o ícone FontAwesome baseado no tipo"""
        icones = {
            TipoNotificacao.SISTEMA: 'fa-cog',
            TipoNotificacao.ALERTA: 'fa-exclamation-triangle',
            TipoNotificacao.MENSAGEM: 'fa-envelope',
            TipoNotificacao.VIOLENCIA_DOMESTICA: 'fa-hand-paper',
            TipoNotificacao.CRIME_SEXUAL: 'fa-shield-alt',
            TipoNotificacao.MEDIDA_PROTETIVA: 'fa-gavel'
        }
        return icones.get(self.tipo, 'fa-info-circle')