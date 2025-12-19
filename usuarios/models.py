# -*- coding: utf-8 -*-
"""

Sistema de Permissões:
- Usa auth.Group padrão do Django
- CustomUser com validações brasileiras (CPF, telefone)
- Nomenclatura em português brasileiro
"""
import os
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator



# ============================================================================
# VALIDADOR: Arquivo PDF
# ============================================================================
def validate_pdf_file(value):
    """Valida se o arquivo enviado é PDF"""
    ext = os.path.splitext(value.name)[1]
    if ext.lower() != '.pdf':
        raise ValidationError('Apenas arquivos .pdf são permitidos.')


# ============================================================================
# MODELO: CustomUser (Usuário Personalizado)
# ============================================================================
class CustomUser(AbstractUser):
    """
    Modelo de usuário customizado para PIEVDCS
    
    Características:
    - CPF único obrigatório (formato brasileiro 000.000.000-00)
    - Telefone com formato brasileiro ((00) 00000-0000)
    - Foto de perfil
    - Vínculo com instituições via auth.Group padrão do Django
    - Comprovante de vínculo institucional (PDF)
    
    Conforme especificação PIEVDCS:
    - Nomenclatura em português brasileiro
    - Validações brasileiras (CPF, telefone)
    - Permissões baseadas em grupos institucionais
    """
    
    # ========================================================================
    # VALIDADORES
    # ========================================================================
    cpf_validator = RegexValidator(
        regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
        message='CPF deve estar no formato: 000.000.000-00'
    )
    
    phone_validator = RegexValidator(
        regex=r'^\(\d{2}\) \d{4,5}-\d{4}$',
        message='Telefone deve estar no formato: (00) 00000-0000 ou (00) 0000-0000'
    )
    
    # ========================================================================
    # CAMPOS PERSONALIZADOS
    # ========================================================================
    cpf = models.CharField(
        'CPF',
        max_length=14,
        unique=True,
        validators=[cpf_validator],
        help_text='Formato: 000.000.000-00',
        null=True,
        blank=True
    )
    
    data_nascimento = models.DateField(
        verbose_name='Data de Nascimento',
        null=True,
        blank=True
    )
    
    genero = models.CharField(
        verbose_name='Gênero',
        max_length=10,
        choices=[
            ('M', 'Masculino'),
            ('F', 'Feminino'),
            ('N', 'Prefiro não informar'),
        ],
        null=True,
        blank=True
    )
    
    telefone = models.CharField(
        verbose_name='Telefone',
        max_length=15,
        validators=[phone_validator],
        help_text='Formato: (00) 00000-0000',
        null=True,
        blank=True
    )
    
    foto = models.ImageField(
        verbose_name='Foto do Perfil',
        upload_to='usuarios/fotos/%Y/%m/',
        null=True,
        blank=True,
    )
    
    comprovante_vinculo = models.FileField(
        verbose_name='Comprovante de Vínculo',
        upload_to='usuarios/comprovantes/%Y/%m/',
        validators=[validate_pdf_file],
        null=True,
        blank=True,
    )
    
    # ========================================================================
    # METADATA
    # ========================================================================
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['username']
        db_table = 'usuarios_customuser'
    
    def __str__(self):
        nome_completo = self.get_full_name()
        return f"{nome_completo} ({self.username})" if nome_completo else self.username
    
    # ========================================================================
    # MÉTODOS AUXILIARES: Gerenciamento de Instituições
    # ========================================================================
    def get_instituicoes(self):
        """Retorna lista de nomes das instituições (grupos) do usuário"""
        return list(self.groups.values_list('name', flat=True))
    
    def pertence_a_instituicao(self, nome_instituicao):
        """Verifica se usuário pertence a uma instituição específica"""
        return self.groups.filter(name=nome_instituicao).exists()
    
    @property
    def tem_instituicao(self):
        """Verifica se usuário tem pelo menos uma instituição"""
        return self.groups.exists()
    
    def instituicoes_formatadas(self):
        """Retorna instituições formatadas para exibição"""
        instituicoes = self.get_instituicoes()
        return ', '.join(instituicoes) if instituicoes else 'Sem instituição'
    
    def tem_acesso_administracao(self):
        """Verifica se usuário tem acesso à Administração"""
        return self.pertence_a_instituicao('Administração')