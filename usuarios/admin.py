from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, CustomGroup

from django.contrib.auth.models import Group
admin.site.unregister(Group)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups', 'cpf', 'telefone', 'foto','data_nascimento', 'genero', 'comprovante_vinculo')
    #empty_value_display = "-vazio-"

    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = 'Grupos'
    
    # Sobrescrever completamente os fieldsets para evitar duplicação
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email', 'cpf', 'telefone', 'foto', 'data_nascimento', 'genero', 'comprovante_vinculo')}),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Manter os outros atributos do UserAdmin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

@admin.register(CustomGroup)
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'get_permissions_count', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('permissions',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
        ('Permissões', {'fields': ('permissions',)}),
        ('Informações do Sistema', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_permissions_count(self, obj):
        return obj.permissions.count()
    get_permissions_count.short_description = 'Nº de Permissões'

# ============================================================================
# CUSTOMIZAÇÃO DO SITE ADMIN
# ============================================================================
admin.site.site_header = "PIEVDCS - Administração"
admin.site.site_title = "PIEVDCS Admin"
admin.site.index_title = "Painel de Controle - Plataforma Integrada de Enfrentamento à Violência"
admin.site.empty_value_display = "-vazio-"