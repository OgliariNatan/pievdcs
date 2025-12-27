# -*- coding: utf-8 -*-
"""
Script para criar grupos institucionais do PIEVDCS com permissões
Conforme especificação PIEVDCS em .github/copilot-instructions.md

Instituições por categoria:
- Sistema de Justiça: Poder Judiciário, Ministério Público, Defensoria Pública
- Segurança Pública: Polícia Militar, Polícia Civil, Polícia Penal, Polícia Científica
- Serviços Municipais: CAPS, CRAS, CREAS, Secretaria da Saúde
- Administração

Para executar:
    python manage.py shell < automacoes/criar_grupos_institucionais.py
"""

import os
import sys
import django
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# Configuração do Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MAIN.settings')
    django.setup()

from usuarios.models import CustomUser


def criar_grupos_institucionais():
    """
    Cria grupos institucionais padrão do PIEVDCS em auth.Group
    com permissões específicas por instituição
    
    Estrutura de permissões:
    - Sistema de Justiça: acesso total a sistema_justica
    - Segurança Pública: acesso total a seguranca_publica
    - Serviços Municipais: acesso a MAIN e leitura em sistema_justica
    - Administração: acesso total a todos os apps
    
    Returns:
        int: Quantidade de grupos criados
    """
    
    print("=" * 70)
    print("CRIANDO GRUPOS INSTITUCIONAIS DO PIEVDCS")
    print("Conforme especificação em .github/copilot-instructions.md")
    print("=" * 70)
    
    # ========================================================================
    # DEFINIÇÃO DOS GRUPOS E PERMISSÕES
    # ========================================================================
    
    grupos_config = {
        # ====================================================================
        # SISTEMA DE JUSTIÇA
        # ====================================================================
        'Poder Judiciário': {
            'descricao': 'Juízes e servidores do Poder Judiciário',
            'apps': ['sistema_justica'],
            'permissions': ['view', 'add', 'change', 'delete'],
            'models_especificos': [
                'comarcaspoderjudiciario',
                'medidaprotetiva',
                'audiencia',
                'sentenca',
            ]
        },
        
        'Ministério Público': {
            'descricao': 'Promotores e servidores do Ministério Público',
            'apps': ['sistema_justica', 'MAIN'],
            'permissions': ['view', 'add', 'change', 'delete'],
            'models_especificos': [
                'formulariomedidaprotetiva',
                'investigacao',
                'denuncia',
            ]
        },
        
        'Defensoria Pública': {
            'descricao': 'Defensores públicos e assistentes',
            'apps': ['sistema_justica'],
            'permissions': ['view', 'add', 'change', 'delete'],
            'models_especificos': [
                'formulariomedidaprotetiva',
                'atendimento',
                'acompanhamento',
            ]
        },
        
        # ====================================================================
        # SEGURANÇA PÚBLICA
        # ====================================================================
        'Polícia Militar': {
            'descricao': 'Oficiais e praças da Polícia Militar',
            'apps': ['seguranca_publica'],
            'permissions': ['view', 'add', 'change'],
            'models_especificos': [
                'ocorrencia',
                'boletim_ocorrencia',
                'atendimento_emergencial',
            ],
            'leitura_adicional': ['sistema_justica']  # Pode ler dados do judiciário
        },
        
        'Polícia Civil': {
            'descricao': 'Delegados e investigadores da Polícia Civil',
            'apps': ['seguranca_publica'],
            'permissions': ['view', 'add', 'change', 'delete'],
            'models_especificos': [
                'boletim_ocorrencia',
                'inquerito',
                'investigacao',
                'depoimento',
            ],
            'leitura_adicional': ['sistema_justica']
        },
        
        'Polícia Penal': {
            'descricao': 'Agentes penitenciários e gestão prisional',
            'apps': ['seguranca_publica'],
            'permissions': ['view', 'add', 'change'],
            'models_especificos': [
                'registro_prisional',
                'monitoramento',
                'visita',
            ],
            'leitura_adicional': ['sistema_justica']
        },
        
        'Polícia Científica': {
            'descricao': 'Peritos criminais e técnicos forenses',
            'apps': ['seguranca_publica'],
            'permissions': ['view', 'add', 'change'],
            'models_especificos': [
                'pericia',
                'laudo_tecnico',
                'exame_corpo_delito',
            ],
            'leitura_adicional': ['sistema_justica']
        },
        
        # ====================================================================
        # SERVIÇOS MUNICIPAIS
        # ====================================================================
        'CAPS': {
            'descricao': 'Centro de Atenção Psicossocial',
            'apps': ['municipio'],
            'permissions': ['view', 'add', 'change'],
            'models_especificos': [
                'atendimento_psicologico',
                'acompanhamento_psicossocial',
                'grupo_terapeutico',
            ],
            'leitura_adicional': ['sistema_justica']  # Visualizar dados de vítimas
        },
        
        'CRAS': {
            'descricao': 'Centro de Referência de Assistência Social',
            'apps': ['municipio'],
            'permissions': ['view', 'add', 'change'],
            'models_especificos': [
                'cadastro_familiar',
                'visita_domiciliar',
                'encaminhamento',
            ],
            'leitura_adicional': ['sistema_justica']
        },
        
        'CREAS': {
            'descricao': 'Centro de Referência Especializado de Assistência Social',
            'apps': ['municipio'],
            'permissions': ['view', 'add', 'change'],
            'models_especificos': [
                'atendimento_especializado',
                'plano_acompanhamento',
                'medida_protecao',
            ],
            'leitura_adicional': ['sistema_justica']
        },
        
        'Secretaria da Saúde': {
            'descricao': 'Secretaria Municipal de Saúde',
            'apps': ['municipio'],
            'permissions': ['view', 'add', 'change'],
            'models_especificos': [
                'atendimento_medico',
                'prontuario',
                'encaminhamento_especialista',
            ],
            'leitura_adicional': {
                'sistema_justica': [
                    'vitima_dados',
                    'agressor_dados',
                    'filhos_dados',
                ],
                #Adicinar mais
            }
        },
        
        # ====================================================================
        # ADMINISTRAÇÃO
        # ====================================================================
        'Administração': {
            'descricao': 'Administradores do sistema com acesso total',
            'apps': ['sistema_justica', 'seguranca_publica', 'municipio', 'MAIN', 'usuarios', 'MAIN'],
            'permissions': ['view', 'add', 'change', 'delete'],
            'is_superuser_group': True  # Marca como grupo de administradores
        },
    }
    
    # ========================================================================
    # CRIAR GRUPOS E ATRIBUIR PERMISSÕES
    # ========================================================================
    
    grupos_criados = 0
    grupos_atualizados = 0
    
    for nome_grupo, config in grupos_config.items():
        grupo, created = Group.objects.get_or_create(name=nome_grupo)
        
        if created:
            grupos_criados += 1
            status = "✅ Criado"
        else:
            grupos_atualizados += 1
            status = "🔄 Atualizado"
            # Limpar permissões existentes para reconfigurar
            grupo.permissions.clear()
        
        print(f"\n{status}: {nome_grupo}")
        print(f"   📝 {config['descricao']}")
        
        # Contador de permissões adicionadas
        perms_adicionadas = 0
        
        # ====================================================================
        # PERMISSÕES PRINCIPAIS (apps especificados)
        # ====================================================================
        for app_label in config.get('apps', []):
            try:
                # Obter todos os ContentTypes do app
                content_types = ContentType.objects.filter(app_label=app_label)
                
                for ct in content_types:
                    # Adicionar permissões especificadas
                    for perm_type in config.get('permissions', []):
                        codename = f"{perm_type}_{ct.model}"
                        
                        try:
                            permission = Permission.objects.get(
                                codename=codename,
                                content_type=ct
                            )
                            grupo.permissions.add(permission)
                            perms_adicionadas += 1
                        except Permission.DoesNotExist:
                            pass  # Permissão não existe para este modelo
            
            except Exception as e:
                print(f"   ⚠️  Erro ao processar app '{app_label}': {e}")
        
        # ====================================================================
        # PERMISSÕES DE LEITURA ADICIONAL
        # ====================================================================
        for app_label in config.get('leitura_adicional', []):
            try:
                content_types = ContentType.objects.filter(app_label=app_label)
                
                for ct in content_types:
                    codename = f"view_{ct.model}"
                    
                    try:
                        permission = Permission.objects.get(
                            codename=codename,
                            content_type=ct
                        )
                        grupo.permissions.add(permission)
                        perms_adicionadas += 1
                    except Permission.DoesNotExist:
                        pass
            
            except Exception as e:
                print(f"   ⚠️  Erro ao adicionar leitura de '{app_label}': {e}")
        
        print(f"   🔐 Permissões configuradas: {perms_adicionadas}")
    
    print("\n" + "=" * 70)
    print("📊 RESUMO DA CRIAÇÃO DE GRUPOS")
    print("=" * 70)
    print(f"✅ Grupos criados: {grupos_criados}")
    print(f"🔄 Grupos atualizados: {grupos_atualizados}")
    print(f"📊 Total de grupos institucionais: {Group.objects.count()}")
    print("=" * 70)
    
    # ========================================================================
    # ASSOCIAR SUPERUSUÁRIOS AO GRUPO ADMINISTRAÇÃO
    # ========================================================================
    print("\n🔧 Configurando superusuários...")
    
    grupo_admin = Group.objects.get(name='Administração')
    superusers = CustomUser.objects.filter(is_superuser=True)
    
    for admin in superusers:
        if not admin.groups.filter(name='Administração').exists():
            admin.groups.add(grupo_admin)
            print(f"   ✅ Superusuário '{admin.username}' adicionado ao grupo 'Administração'")
        else:
            print(f"   ⏭️  Superusuário '{admin.username}' já está no grupo 'Administração'")
    
    # ========================================================================
    # ESTATÍSTICAS FINAIS
    # ========================================================================
    print("\n" + "=" * 70)
    print("📈 ESTATÍSTICAS DE PERMISSÕES POR GRUPO")
    print("=" * 70)
    
    for grupo in Group.objects.all().order_by('name'):
        total_perms = grupo.permissions.count()
        total_users = grupo.user_set.count()
        print(f"\n🏛️  {grupo.name}")
        print(f"   👥 Usuários: {total_users}")
        print(f"   🔐 Permissões: {total_perms}")
        
        if total_perms > 0:
            # Mostrar distribuição por app
            perms_por_app = {}
            for perm in grupo.permissions.all():
                app_label = perm.content_type.app_label
                perms_por_app[app_label] = perms_por_app.get(app_label, 0) + 1
            
            print(f"   📱 Apps com acesso:")
            for app, count in sorted(perms_por_app.items()):
                print(f"      • {app}: {count} permissões")
    
    print("\n" + "=" * 70)
    print("✨ GRUPOS INSTITUCIONAIS CRIADOS COM SUCESSO!")
    print("=" * 70)
    print("\n💡 Próximos passos:")
    print("   1. Acesse /admin/auth/group/ para visualizar os grupos")
    print("   2. Atribua usuários aos grupos conforme instituição")
    print("   3. Teste as permissões de cada grupo")
    
    return grupos_criados + grupos_atualizados


def listar_permissoes_grupo(nome_grupo):
    """
    Lista todas as permissões de um grupo específico
    
    Args:
        nome_grupo (str): Nome do grupo institucional
    """
    try:
        grupo = Group.objects.get(name=nome_grupo)
        
        print(f"\n{'=' * 70}")
        print(f"🔐 PERMISSÕES DO GRUPO: {nome_grupo}")
        print(f"{'=' * 70}")
        print(f"👥 Total de usuários: {grupo.user_set.count()}")
        print(f"🔐 Total de permissões: {grupo.permissions.count()}")
        
        # Agrupar por app
        perms_por_app = {}
        for perm in grupo.permissions.all():
            app_label = perm.content_type.app_label
            if app_label not in perms_por_app:
                perms_por_app[app_label] = []
            perms_por_app[app_label].append(perm)
        
        # Exibir permissões por app
        for app_label in sorted(perms_por_app.keys()):
            print(f"\n📱 {app_label.upper()}:")
            for perm in sorted(perms_por_app[app_label], key=lambda p: p.codename):
                print(f"   • {perm.name} ({perm.codename})")
        
        print(f"\n{'=' * 70}")
        
    except Group.DoesNotExist:
        print(f"❌ Grupo '{nome_grupo}' não encontrado.")
        print("\n📋 Grupos disponíveis:")
        for g in Group.objects.all():
            print(f"   • {g.name}")


def remover_todos_grupos():
    """
    Remove todos os grupos institucionais (usar com CUIDADO!)
    """
    print("⚠️  AVISO: Esta função irá apagar TODOS os grupos institucionais!")
    print("   Os usuários NÃO serão deletados, apenas desvinculados dos grupos.")
    confirmacao = input("\nDigite 'CONFIRMAR' para continuar: ")
    
    if confirmacao == 'CONFIRMAR':
        count = Group.objects.count()
        Group.objects.all().delete()
        print(f"🗑️  {count} grupos foram removidos com sucesso.")
    else:
        print("❌ Operação cancelada.")


if __name__ == "__main__":
    pass
criar_grupos_institucionais()