# -*- coding: utf-8 -*-
"""
Configuração do Django Admin para app usuarios do PIEVDCS
Conforme especificação PIEVDCS em .github/copilot-instructions.md

Sistema de Permissões:
- Usa auth.Group padrão do Django para grupos institucionais
- CustomUser com validações brasileiras (CPF, telefone)
- Nomenclatura em português brasileiro
- Interface administrativa customizada

Instituições integradas:
- Sistema de Justiça: Poder Judiciário, Ministério Público, Defensoria Pública
- Segurança Pública: Polícia Militar, Polícia Civil, Polícia Penal, Polícia Científica
- Serviços Municipais: CAPS, CRAS, CREAS, Secretaria da Saúde
- Administração
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from .models import CustomUser


# ============================================================================
# ADMIN: CustomUser (Usuário Personalizado)
# ============================================================================
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Administração de usuários personalizados do PIEVDCS
    
    Características:
    - Gerenciamento de grupos institucionais (auth.Group)
    - Validação de CPF brasileiro
    - Upload de comprovantes de vínculo (PDF)
    - Nomenclatura em português brasileiro
    - Badges coloridos para grupos institucionais
    
    Conforme especificação PIEVDCS em .github/copilot-instructions.md
    """
    
    # ========================================================================
    # CONFIGURAÇÃO DE EXIBIÇÃO
    # ========================================================================
    list_display = [
        'username',
        'get_nome_completo',
        'email',
        'cpf',
        'telefone',
        'exibir_grupos',
        'is_active',
        'is_staff',
        'date_joined',
    ]
    
    list_filter = [
        'is_staff',
        'is_superuser',
        'is_active',
        'groups',
        'genero',
        'date_joined',
    ]
    
    search_fields = [
        'username',
        'first_name',
        'last_name',
        'email',
        'cpf',
        'telefone',
    ]
    
    ordering = ['-date_joined']
    
    # ========================================================================
    # FIELDSETS: Organização dos Formulários
    # ========================================================================
    fieldsets = (
        ('Autenticação', {
            'fields': ('username', 'password')
        }),
        
        ('Informações Pessoais', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'cpf',
                'data_nascimento',
                'genero',
                'telefone',
                'foto',
            ),
            'description': 'Dados pessoais do usuário conforme padrão brasileiro'
        }),
        
        ('Vínculo Institucional', {
            'fields': (
                'groups',
                'comprovante_vinculo',
            ),
            'description': (
                '<strong>Grupos:</strong> Instituições às quais o usuário pertence<br>'
                '<strong>Comprovante:</strong> Documento PDF comprovando vínculo institucional<br><br>'
                '<em>Instituições disponíveis:</em><br>'
                '• Sistema de Justiça: Poder Judiciário, Ministério Público, Defensoria Pública<br>'
                '• Segurança Pública: Polícia Militar, Polícia Civil, Polícia Penal, Polícia Científica<br>'
                '• Serviços Municipais: CAPS, CRAS, CREAS, Secretaria da Saúde<br>'
                '• Administração'
            )
        }),
        
        ('Permissões', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'user_permissions',
            ),
            'classes': ('collapse',),
        }),
        
        ('Datas Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Criar Novo Usuário', {
            'classes': ('wide',),
            'fields': (
                'username',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'email',
                'cpf',
                'groups',
                'is_staff',
                'is_active',
            ),
            'description': (
                'Preencha os campos abaixo para criar um novo usuário.<br>'
                '<strong>Obrigatório:</strong> username, password, groups (instituição)'
            )
        }),
    )
    
    filter_horizontal = ['groups', 'user_permissions']
    
    # ========================================================================
    # MÉTODOS PERSONALIZADOS: Exibição de Dados
    # ========================================================================
    def get_nome_completo(self, obj):
        """Retorna nome completo formatado"""
        nome = obj.get_full_name()
        return nome if nome else '-'
    
    get_nome_completo.short_description = 'Nome Completo'
    get_nome_completo.admin_order_field = 'first_name'
    
    def exibir_grupos(self, obj):
        """
        Exibe grupos institucionais como badges coloridos
        
        Cores por instituição (conforme PIEVDCS):
        - Poder Judiciário: Azul escuro (#1e40af)
        - Ministério Público: Vermelho (#dc2626)
        - Defensoria Pública: Verde (#059669)
        - Polícia Militar: Roxo (#7c3aed)
        - Polícia Civil: Laranja (#ea580c)
        - Polícia Penal: Ciano (#0891b2)
        - Polícia Científica: Índigo (#4f46e5)
        - CAPS: Verde claro (#10b981)
        - CRAS: Amarelo (#f59e0b)
        - CREAS: Rosa (#ec4899)
        - Secretaria da Saúde: Turquesa (#06b6d4)
        - Administração: Cinza (#6b7280)
        """
        grupos = obj.groups.all()
        
        if not grupos:
            return format_html('<span style="color: #999;">Sem grupo</span>')
        
        cores = {
            'Poder Judiciário': '#1e40af',
            'Ministério Público': '#dc2626',
            'Defensoria Pública': '#059669',
            'Polícia Militar': '#7c3aed',
            'Polícia Civil': '#ea580c',
            'Polícia Penal': '#0891b2',
            'Polícia Científica': '#4f46e5',
            'CAPS': '#10b981',
            'CRAS': '#f59e0b',
            'CREAS': '#ec4899',
            'Secretaria da Saúde': '#06b6d4',
            'Administração': '#6b7280',
        }
        
        badges = []
        for grupo in grupos:
            cor = cores.get(grupo.name, '#6b7280')
            badges.append(
                f'<span style="background-color: {cor}; color: white; '
                f'padding: 3px 10px; border-radius: 4px; margin-right: 5px; '
                f'font-size: 11px; font-weight: bold; display: inline-block; '
                f'white-space: nowrap;">{grupo.name}</span>'
            )
        
        return format_html(''.join(badges))
    
    exibir_grupos.short_description = 'Grupos Institucionais'
    
    # ========================================================================
    # MÉTODOS PERSONALIZADOS: Comportamento do Admin
    # ========================================================================
    def get_queryset(self, request):
        """Otimiza queryset com prefetch de grupos"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('groups')
    
    def save_model(self, request, obj, form, change):
        """Salva modelo com validações adicionais"""
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        
        # Para novos usuários sem grupos, adicionar ao grupo Administração
        if is_new and not obj.groups.exists():
            try:
                grupo_admin = Group.objects.get(name='Administração')
                obj.groups.add(grupo_admin)
            except Group.DoesNotExist:
                pass


# ============================================================================
# ADMIN: Group (Grupos Institucionais)
# ============================================================================
class GrupoInstituicionalAdmin(GroupAdmin):
    """
    Administração customizada para grupos institucionais do PIEVDCS
    
    Características:
    - Exibição de quantidade de usuários por grupo
    - Exibição de quantidade de permissões por grupo
    - Interface otimizada para gerenciamento de instituições
    
    Conforme especificação PIEVDCS em .github/copilot-instructions.md
    """
    
    list_display = [
        'name',
        'quantidade_usuarios',
        'quantidade_permissoes',
    ]
    
    search_fields = ['name']
    filter_horizontal = ['permissions']
    
    def quantidade_usuarios(self, obj):
        """
        Retorna quantidade de usuários no grupo institucional
        
        ✅ CORRETO: Usa 'user_set' (relacionamento reverso padrão do Django)
        """
        count = obj.user_set.count()  # ✅ MUDANÇA AQUI: customuser_set → user_set
        
        if count == 0:
            cor = '#999999'
        elif count < 5:
            cor = '#10b981'
        elif count < 20:
            cor = '#3b82f6'
        else:
            cor = '#dc2626'
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 2px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            cor,
            count
        )
    
    quantidade_usuarios.short_description = 'Usuários'
    
    def quantidade_permissoes(self, obj):
        """Retorna quantidade de permissões do grupo"""
        count = obj.permissions.count()
        return format_html(
            '<span style="background-color: #10b981; color: white; '
            'padding: 2px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            count
        )
    
    quantidade_permissoes.short_description = 'Permissões'
    
    def get_queryset(self, request):
        """
        Otimiza queryset com prefetch de usuários e permissões
        
        ✅ CORRETO: Usa 'user_set' (relacionamento reverso padrão do Django)
        """
        qs = super().get_queryset(request)
        return qs.prefetch_related('user_set', 'permissions')  # ✅ MUDANÇA AQUI


# ============================================================================
# REGISTRAR ADMIN CUSTOMIZADO PARA GROUP
# ============================================================================
admin.site.unregister(Group)
admin.site.register(Group, GrupoInstituicionalAdmin)


# ============================================================================
# CUSTOMIZAÇÃO DO SITE ADMIN (Conforme PIEVDCS)
# ============================================================================
admin.site.site_header = "PIEVDCS - Administração"
admin.site.site_title = "PIEVDCS Admin"
admin.site.index_title = "Painel de Controle - Plataforma Integrada de Enfrentamento à Violência"
admin.site.empty_value_display = "-vazio-"

