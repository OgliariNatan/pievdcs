# -*- coding: utf-8 -*-
"""
Script para criar grupos de usuários personalizados para as instituições do sistema PIEVDCS.
Cria grupos com permissões específicas para cada instituição participante da plataforma.

Para executar:
1. Abra o Django shell: python manage.py shell
<<<<<<< HEAD
2. Execute: from automacoes.cria_grupos_usuarios import criar_grupos_institucionais
=======
2. Execute: from automacoes.cria_grupos_usuarios import *
>>>>>>> ed41264 (ajustando para pull)
3. Execute: criar_grupos_institucionais()

@autor: Ogliarinatan
@data: 2025
"""

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from usuarios.models import CustomGroup, CustomUser


# Dicionário com os grupos institucionais e suas descrições
GRUPOS_INSTITUCIONAIS = {
    'CAPS': {
        'nome': 'CAPS - Centro de Atenção Psicossocial',
        'descricao': 'Profissionais do Centro de Atenção Psicossocial - Serviço de saúde mental para atendimento de pessoas com transtornos mentais',
        'categoria': 'municipio',
        'sigla': 'CAPS'
    },
    'CRAS': {
        'nome': 'CRAS - Centro de Referência de Assistência Social',
        'descricao': 'Profissionais do Centro de Referência de Assistência Social - Porta de entrada da Assistência Social',
        'categoria': 'municipio',
        'sigla': 'CRAS'
    },
    'CREAS': {
        'nome': 'CREAS - Centro de Referência Especializado de Assistência Social',
        'descricao': 'Profissionais do Centro de Referência Especializado de Assistência Social - Atendimento especializado a famílias e indivíduos em situação de risco',
        'categoria': 'municipio',
        'sigla': 'CREAS'
    },
    'Conselho Tutelar': {
        'nome': 'Conselho Tutelar',
        'descricao': 'Conselheiros Tutelares - Órgão responsável por zelar pelos direitos de crianças e adolescentes',
        'categoria': 'municipio',
        'sigla': 'Conselho Tutelar'
    },
    'Defensoria Pública': {
        'nome': 'Defensoria Pública',
        'descricao': 'Defensores Públicos e equipe de apoio - Assistência jurídica integral e gratuita aos necessitados',
        'categoria': 'sistema_justica',
        'sigla': 'Defensoria Pública'
    },
    'Ministério Público': {
        'nome': 'Ministério Público',
        'descricao': 'Promotores de Justiça e equipe de apoio - Defesa da ordem jurídica, do regime democrático e dos interesses sociais',
        'categoria': 'sistema_justica',
        'sigla': 'Ministério Público'
    },
    'Poder Judiciário': {
        'nome': 'Poder Judiciário',
        'descricao': 'Magistrados e servidores do Poder Judiciário - Administração da justiça e julgamento de casos',
        'categoria': 'sistema_justica',
        'sigla': 'Poder Judiciário'
    },
    'Polícia Científica': {
        'nome': 'Polícia Científica',
        'descricao': 'Peritos e equipe da Polícia Científica - Perícias criminais e laudos técnicos',
        'categoria': 'seguranca_publica',
        'sigla': 'Polícia Científica'
    },
    'Polícia Civil': {
        'nome': 'Polícia Civil',
        'descricao': 'Delegados, investigadores e equipe da Polícia Civil - Polícia judiciária e investigação criminal',
        'categoria': 'seguranca_publica',
        'sigla': 'Polícia Civil'
    },
    'Polícia Militar': {
        'nome': 'Polícia Militar',
        'descricao': 'Oficiais e praças da Polícia Militar - Policiamento ostensivo e preservação da ordem pública',
        'categoria': 'seguranca_publica',
        'sigla': 'Polícia Militar'
    },
    'Polícia Penal': {
        'nome': 'Polícia Penal',
        'descricao': 'Agentes e equipe da Polícia Penal - Segurança nos estabelecimentos penais',
        'categoria': 'seguranca_publica',
        'sigla': 'Polícia Penal'
    },
    'Secretaria da Saúde': {
        'nome': 'Secretaria da Saúde',
        'descricao': 'Profissionais da Secretaria Municipal/Estadual de Saúde - Gestão e execução de políticas públicas de saúde',
        'categoria': 'municipio',
        'sigla': 'Secretaria da Saúde'
    }
}


def criar_grupos_institucionais():
    """
    Cria os grupos de usuários personalizados para cada instituição do sistema PIEVDCS.
    """
    
    print("🚀 Iniciando criação de grupos institucionais do PIEVDCS...")
    print("="*70)
    
    grupos_criados = 0
    grupos_atualizados = 0
    erros = []
    
    with transaction.atomic():
        for chave, info in GRUPOS_INSTITUCIONAIS.items():
            try:
                # Cria ou busca o grupo personalizado
                grupo, criado = CustomGroup.objects.get_or_create(
                    name=info['sigla'],
                    defaults={
                        'description': info['descricao']
                    }
                )
                
                if criado:
                    grupos_criados += 1
                    print(f"✅ Grupo criado: {info['nome']} ({info['sigla']})")
                else:
                    # Atualiza a descrição se o grupo já existe
                    if grupo.description != info['descricao']:
                        grupo.description = info['descricao']
                        grupo.save()
                        grupos_atualizados += 1
                        print(f"📝 Grupo atualizado: {info['nome']} ({info['sigla']})")
                    else:
                        print(f"⚠️  Grupo já existe: {info['nome']} ({info['sigla']})")
                
                print(f"   📁 Categoria: {info['categoria']}")
                print(f"   📄 Descrição: {info['descricao'][:80]}...")
                
                # Adicionar permissões específicas baseadas na categoria
                adicionar_permissoes_grupo(grupo, info['categoria'], info['sigla'])
                
            except Exception as e:
                erros.append(f"Erro ao criar grupo {chave}: {str(e)}")
                print(f"❌ Erro ao criar grupo {info['nome']}: {str(e)}")
                continue
    
    # Relatório final
    print("\n" + "="*70)
    print("📊 RELATÓRIO DE CRIAÇÃO DE GRUPOS")
    print("="*70)
    print(f"✅ Grupos criados: {grupos_criados}")
    print(f"📝 Grupos atualizados: {grupos_atualizados}")
    print(f"⚠️  Grupos já existentes: {len(GRUPOS_INSTITUCIONAIS) - grupos_criados - grupos_atualizados}")
    print(f"❌ Erros encontrados: {len(erros)}")
    print(f"📋 Total de grupos no sistema: {CustomGroup.objects.count()}")
    
    if erros:
        print(f"\n❌ DETALHES DOS ERROS:")
        for erro in erros:
            print(f"   • {erro}")
    
    print("\n✨ Script concluído!")
    print("💡 Para visualizar os grupos, acesse: /admin/usuarios/customgroup/")
    
    return grupos_criados


def adicionar_permissoes_grupo(grupo, categoria, sigla):
    """
    Adiciona permissões específicas para cada grupo baseado em sua categoria.
    
    Args:
        grupo: Objeto CustomGroup
        categoria: Categoria da instituição (municipio, sistema_justica, seguranca_publica)
        sigla: Sigla da instituição
    """
    
    try:
        # Limpar permissões antigas antes de adicionar novas
        grupo.permissions.clear()
        
        # Permissões básicas para todos os grupos - apenas visualização
        permissoes_basicas = []
        
        # Buscar permissões de visualização de dados de vítimas e agressores
        content_types_basicos = ContentType.objects.filter(
            app_label='sistema_justica',
            model__in=['vitima_dados', 'agressor_dados']
        )
        
        for ct in content_types_basicos:
            perms = Permission.objects.filter(
                content_type=ct,
                codename__startswith='view_'
            )
            permissoes_basicas.extend(perms)
        
        # Adicionar permissões básicas
        grupo.permissions.add(*permissoes_basicas)
        
        # Adicionar permissões específicas por categoria
        if categoria == 'sistema_justica':
            # Sistema de Justiça tem mais permissões
<<<<<<< HEAD
            if sigla == 'Defensoria Pública':  # Defensoria Pública
=======
            if sigla == 'DP':  # Defensoria Pública
>>>>>>> ed41264 (ajustando para pull)
                content_types = ContentType.objects.filter(
                    app_label='sistema_justica',
                    model__in=['formulariomedidaprotetiva', 'vitima_dados', 'agressor_dados']
                )
                for ct in content_types:
                    perms = Permission.objects.filter(content_type=ct)
                    grupo.permissions.add(*perms)
                    
<<<<<<< HEAD
            elif sigla == 'Ministério Público':  # Ministério Público
=======
            elif sigla == 'MP':  # Ministério Público
>>>>>>> ed41264 (ajustando para pull)
                content_types = ContentType.objects.filter(
                    app_label='sistema_justica',
                    model__in=['vitima_dados', 'agressor_dados']
                )
                for ct in content_types:
                    # MP pode visualizar e adicionar, mas não deletar
                    perms = Permission.objects.filter(
                        content_type=ct,
                        codename__in=[f'view_{ct.model}', f'add_{ct.model}', f'change_{ct.model}']
                    )
                    grupo.permissions.add(*perms)
                    
<<<<<<< HEAD
            elif sigla == 'Poder Judiciário':  # Poder Judiciário
=======
            elif sigla == 'PJ':  # Poder Judiciário
>>>>>>> ed41264 (ajustando para pull)
                content_types = ContentType.objects.filter(
                    app_label='sistema_justica'
                )
                for ct in content_types:
                    # PJ tem acesso total ao sistema_justica
                    perms = Permission.objects.filter(content_type=ct)
                    grupo.permissions.add(*perms)
                
        elif categoria == 'seguranca_publica':
            # Segurança Pública - acesso ao app seguranca_publica
            content_types_seg = ContentType.objects.filter(
                app_label='seguranca_publica'
            )
            
            for ct in content_types_seg:
<<<<<<< HEAD
                if sigla in ['Polícia Civil', 'Polícia Militar']:  # Polícias Civil e Militar têm acesso total
=======
                if sigla in ['PC', 'PM']:  # Polícias Civil e Militar têm acesso total
>>>>>>> ed41264 (ajustando para pull)
                    perms = Permission.objects.filter(content_type=ct)
                else:  # Outras polícias têm acesso mais restrito
                    perms = Permission.objects.filter(
                        content_type=ct,
                        codename__in=[f'view_{ct.model}', f'add_{ct.model}', f'change_{ct.model}']
                    )
                grupo.permissions.add(*perms)
            
        elif categoria == 'municipio':
            # Serviços municipais - permissões mais restritas
            if sigla in ['CAPS', 'CRAS', 'CREAS', 'SAUDE']:
                # Apenas visualização de dados básicos já adicionados acima
                pass
                
<<<<<<< HEAD
            elif sigla == 'Conselho Tutelar':  # Conselho Tutelar
=======
            elif sigla == 'CT':  # Conselho Tutelar
>>>>>>> ed41264 (ajustando para pull)
                # Conselho Tutelar pode adicionar casos envolvendo menores
                try:
                    ct_vitima = ContentType.objects.get(
                        app_label='sistema_justica',
                        model='vitima_dados'
                    )
                    perms = Permission.objects.filter(
                        content_type=ct_vitima,
                        codename__in=['view_vitima_dados', 'add_vitima_dados']
                    )
                    grupo.permissions.add(*perms)
                except ContentType.DoesNotExist:
                    pass
        
        total_perms = grupo.permissions.count()
        print(f"   📝 {total_perms} permissões atribuídas ao grupo {grupo.name}")
        
    except Exception as e:
        print(f"   ⚠️  Erro ao adicionar permissões: {str(e)}")


def listar_grupos_e_permissoes():
    """
    Lista todos os grupos personalizados criados e suas respectivas permissões.
    """
    
    print("\n📋 GRUPOS PERSONALIZADOS E PERMISSÕES DO SISTEMA")
    print("="*70)
    
    grupos = CustomGroup.objects.all().order_by('name')
    
    if not grupos:
        print("❌ Nenhum grupo encontrado no sistema.")
        return
    
    for grupo in grupos:
        print(f"\n👥 Grupo: {grupo.name}")
        print(f"   ID: {grupo.id}")
        print(f"   Descrição: {grupo.description[:100]}..." if grupo.description else "   Descrição: -")
        print(f"   Criado em: {grupo.created_at.strftime('%d/%m/%Y %H:%M')}")
        print(f"   Usuários: {grupo.user_set.count()}")
        print(f"   Permissões: {grupo.permissions.count()}")
        
        # Listar algumas permissões como exemplo
        permissoes = grupo.permissions.all()[:5]
        if permissoes:
            print("   Algumas permissões:")
            for perm in permissoes:
                print(f"      • {perm.content_type.app_label}.{perm.codename}")
            
            if grupo.permissions.count() > 5:
                print(f"      ... e mais {grupo.permissions.count() - 5} permissões")


def limpar_grupos_institucionais():
    """
    Remove apenas os grupos institucionais criados por este script.
    CUIDADO: Esta função remove os grupos e suas associações com usuários!
    """
    
    print("⚠️  AVISO: Esta função irá remover os grupos institucionais do sistema!")
    print("Grupos que serão removidos:")
    for sigla in [info['sigla'] for info in GRUPOS_INSTITUCIONAIS.values()]:
        print(f"   • {sigla}")
    
    confirmacao = input("\nDigite 'CONFIRMAR' para continuar: ")
    
    if confirmacao == 'CONFIRMAR':
        count = 0
        for info in GRUPOS_INSTITUCIONAIS.values():
            try:
                grupo = CustomGroup.objects.get(name=info['sigla'])
                grupo.delete()
                count += 1
                print(f"🗑️  Grupo {info['sigla']} removido.")
            except CustomGroup.DoesNotExist:
                pass
        
        print(f"\n✅ {count} grupos foram removidos com sucesso.")
    else:
        print("❌ Operação cancelada.")


def atribuir_usuario_ao_grupo(username, sigla_grupo):
    """
    Atribui um usuário a um grupo institucional.
    
    Args:
        username: Nome de usuário
        sigla_grupo: Sigla do grupo (ex: 'PM', 'DP', 'CAPS')
    """
    
    try:
        usuario = CustomUser.objects.get(username=username)
        grupo = CustomGroup.objects.get(name=sigla_grupo)
        
        usuario.groups.add(grupo)
        print(f"✅ Usuário {username} adicionado ao grupo {sigla_grupo}")
        print(f"   Grupos do usuário: {', '.join([g.name for g in usuario.groups.all()])}")
        
    except CustomUser.DoesNotExist:
        print(f"❌ Usuário {username} não encontrado.")
    except CustomGroup.DoesNotExist:
        print(f"❌ Grupo {sigla_grupo} não encontrado.")
        print(f"   Grupos disponíveis: {', '.join([g.name for g in CustomGroup.objects.all()])}")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")


def remover_usuario_do_grupo(username, sigla_grupo):
    """
    Remove um usuário de um grupo institucional.
    
    Args:
        username: Nome de usuário
        sigla_grupo: Sigla do grupo
    """
    
    try:
        usuario = CustomUser.objects.get(username=username)
        grupo = CustomGroup.objects.get(name=sigla_grupo)
        
        usuario.groups.remove(grupo)
        print(f"✅ Usuário {username} removido do grupo {sigla_grupo}")
        print(f"   Grupos restantes: {', '.join([g.name for g in usuario.groups.all()]) or 'Nenhum'}")
        
    except CustomUser.DoesNotExist:
        print(f"❌ Usuário {username} não encontrado.")
    except CustomGroup.DoesNotExist:
        print(f"❌ Grupo {sigla_grupo} não encontrado.")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")


def estatisticas_grupos():
    """
    Mostra estatísticas detalhadas sobre os grupos do sistema.
    """
    
    print("\n📊 ESTATÍSTICAS DOS GRUPOS DO SISTEMA PIEVDCS")
    print("="*70)
    
    total_grupos = CustomGroup.objects.count()
    total_usuarios = CustomUser.objects.count()
    usuarios_com_grupo = CustomUser.objects.filter(groups__isnull=False).distinct().count()
    
    print(f"\n📈 RESUMO GERAL:")
    print(f"   Total de grupos: {total_grupos}")
    print(f"   Total de usuários: {total_usuarios}")
    print(f"   Usuários com grupo: {usuarios_com_grupo}")
    print(f"   Usuários sem grupo: {total_usuarios - usuarios_com_grupo}")
    
    print(f"\n👥 DISTRIBUIÇÃO POR CATEGORIA:")
    
    # Agrupar por categoria
    categorias = {}
    for info in GRUPOS_INSTITUCIONAIS.values():
        categoria = info['categoria']
        if categoria not in categorias:
            categorias[categoria] = []
        
        try:
            grupo = CustomGroup.objects.get(name=info['sigla'])
            categorias[categoria].append({
                'nome': info['sigla'],
                'usuarios': grupo.user_set.count(),
                'permissoes': grupo.permissions.count()
            })
        except CustomGroup.DoesNotExist:
            pass
    
    for categoria, grupos in categorias.items():
        if grupos:
            print(f"\n   {categoria.upper().replace('_', ' ')}:")
            for g in grupos:
                print(f"      • {g['nome']}: {g['usuarios']} usuários, {g['permissoes']} permissões")
    
    print(f"\n🔐 GRUPOS COM MAIS PERMISSÕES:")
    grupos_top = CustomGroup.objects.all().order_by('-permissions__count')[:5]
    for i, grupo in enumerate(grupos_top, 1):
        print(f"   {i}. {grupo.name}: {grupo.permissions.count()} permissões")


if __name__ == "__main__":
    print("🏛️ Script de Criação de Grupos Institucionais - PIEVDCS")
    print("\nPara executar, use o Django shell:")
    print("python manage.py shell")
    print(">>> from automacoes.cria_grupos_usuarios import criar_grupos_institucionais")
    print(">>> criar_grupos_institucionais()")
    print("\n📚 FUNÇÕES DISPONÍVEIS:")
    print(">>> listar_grupos_e_permissoes()  # Lista todos os grupos e suas permissões")
    print(">>> atribuir_usuario_ao_grupo('nome_usuario', 'PM')  # Atribui usuário a um grupo")
    print(">>> remover_usuario_do_grupo('nome_usuario', 'PM')  # Remove usuário de um grupo")
    print(">>> estatisticas_grupos()  # Mostra estatísticas detalhadas dos grupos")
<<<<<<< HEAD
    print(">>> limpar_grupos_institucionais()  # Remove os grupos (use com cuidado!)")
=======
    print(">>> limpar_grupos_institucionais()  # Remove os grupos (use com cuidado!)")
>>>>>>> ed41264 (ajustando para pull)
