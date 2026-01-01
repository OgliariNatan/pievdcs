"""
Script para gerar dados fictícios de FormularioMedidaProtetiva (Defensoria Pública)
Gera 500 registros de solicitações de medida protetiva com dados realistas brasileiros.

Para executar:
    python manage.py shell
    >>> from automacoes.gera_formularios_mp import criar_formularios_mp_aleatorios
    >>> criar_formularios_mp_aleatorios()
"""

import random
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models

# Configuração do Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MAIN.settings')
    django.setup()

from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from sistema_justica.models.base import Vitima_dados, Agressor_dados, TipoDeViolencia
from sistema_justica.models.poder_judiciario import ComarcasPoderJudiciario
from seguranca_publica.models.base import grau_parentesco_agressor_choices


def criar_formularios_mp_aleatorios(quantidade=500):
    """
    Cria registros fictícios de FormularioMedidaProtetiva
    
    Args:
        quantidade (int): Número de formulários a serem criados (padrão: 500)
    """
    
    print(f"🚀 Iniciando geração de {quantidade} Formulários de Medida Protetiva fictícios...")
    
    # Verificar se há dados suficientes nas tabelas relacionadas
    total_vitimas = Vitima_dados.objects.count()
    total_agressores = Agressor_dados.objects.count()
    total_comarcas = ComarcasPoderJudiciario.objects.count()
    total_tipos_violencia = TipoDeViolencia.objects.filter(ativo=True).count()
    
    if total_vitimas < 50:
        print(f"⚠️  AVISO: Apenas {total_vitimas} vítimas cadastradas. Recomenda-se ter pelo menos 50.")
        print("   Execute primeiro o script gera_vitimas.py para criar mais dados.")
    
    if total_agressores < 50:
        print(f"⚠️  AVISO: Apenas {total_agressores} agressores cadastrados. Recomenda-se ter pelo menos 50.")
        print("   Execute primeiro o script gera_agressores.py para criar mais dados.")
        
    if total_comarcas < 5:
        print(f"⚠️  AVISO: Apenas {total_comarcas} comarcas cadastradas. Alguns formulários não terão comarca.")
    
    if total_tipos_violencia == 0:
        print("❌ ERRO: Nenhum tipo de violência cadastrado no banco de dados!")
        print("   Por favor, cadastre os tipos de violência antes de executar este script.")
        print("   Acesse: /admin/sistema_justica/tipodeviolencia/")
        return 0
    
    print(f"📊 Dados disponíveis: {total_vitimas} vítimas, {total_agressores} agressores, " +
          f"{total_comarcas} comarcas, {total_tipos_violencia} tipos de violência")
    
    # Listas para seleção aleatória
    vitimas_disponiveis = list(Vitima_dados.objects.all())
    agressores_disponiveis = list(Agressor_dados.objects.all())
    comarcas_disponiveis = list(ComarcasPoderJudiciario.objects.all())
    tipos_violencia_disponiveis = list(TipoDeViolencia.objects.filter(ativo=True))
    
    # Choices para seleção aleatória
    graus_parentesco = [choice[0] for choice in grau_parentesco_agressor_choices]

    # Lista de ruas fictícias comuns
    RUAS = [
        "Rua das Flores", "Rua São João", "Rua Santa Maria", "Rua XV de Novembro",
        "Rua Tiradentes", "Rua Dom Pedro II", "Rua Getúlio Vargas", "Rua Presidente Vargas",
        "Rua José de Alencar", "Rua Santos Dumont", "Rua Castro Alves", "Rua Rui Barbosa",
        "Rua Marechal Deodoro", "Rua Benjamin Constant", "Rua Sete de Setembro",
        "Rua Coronel Oliveira", "Rua Major Silva", "Rua Capitão Santos", "Rua Doutor Lima",
        "Rua Professor Almeida", "Avenida Brasil", "Avenida Independência", "Avenida Liberdade",
        "Travessa das Palmeiras", "Travessa São José", "Alameda dos Ipês", "Avenida Sul Brasil"
    ]
    
    # Distribuição de períodos de medida protetiva (em dias)
    periodos_mp_dias = [120, 180, 240, 300, 360]
    pesos_periodos = [40, 20, 15, 10, 8]
    
    # Distribuição de pesos para tipos de violência (baseado em estatísticas reais)
    # Os pesos são proporcionais aos tipos cadastrados
    pesos_violencia_default = {
        'Fisica': 35,
        'Fisíca': 35,
        'Psicologica': 25,
        'Psicológica': 25,
        'Sexual': 15,
        'Patrimonial': 12,
        'Moral': 13
    }
    
    # Criar dicionário de pesos baseado nos tipos cadastrados
    pesos_violencia = []
    for tipo in tipos_violencia_disponiveis:
        peso = pesos_violencia_default.get(tipo.nome, 10)  # Peso padrão de 10 se não encontrado
        pesos_violencia.append(peso)
    
    # Normalizar pesos se necessário
    if sum(pesos_violencia) == 0:
        pesos_violencia = [1] * len(tipos_violencia_disponiveis)
    
    # Distribuição de graus de parentesco
    pesos_parentesco = {
        'Conjuge': 30,
        'Irmao': 12,
        'Pai': 10,
        'Filho': 8,
        'Tio': 7,
        'Cunhado': 6,
        'Padasto': 15,
        'Primo': 9,
        'Outros': 3
    }
    
    formularios_criados = 0
    formularios_existentes = 0
    erros = []
    
    for i in range(quantidade):
        try:
            # Selecionar vítima e agressor aleatoriamente
            if not vitimas_disponiveis or not agressores_disponiveis:
                print("❌ Não há vítimas ou agressores suficientes para continuar.")
                break
            
            vitima_selecionada = random.choice(vitimas_disponiveis)
            agressor_selecionado = random.choice(agressores_disponiveis)
            
            # Verificar se já existe um formulário com essa combinação vítima-agressor
            if FormularioMedidaProtetiva.objects.filter(
                vitima=vitima_selecionada, 
                agressor=agressor_selecionado
            ).exists():
                formularios_existentes += 1
                continue
            
            # Data de solicitação entre 2 anos atrás e hoje
            data_inicio = timezone.now() - timedelta(days=730)
            data_fim = timezone.now()
            data_aleatoria = data_inicio + timedelta(
                days=random.randint(0, (data_fim - data_inicio).days)
            )
            
            # Período da medida protetiva (120 dias é o padrão)
            dias_mp = random.choices(periodos_mp_dias, weights=pesos_periodos, k=1)[0]
            periodo_mp = data_aleatoria.date() + timedelta(days=dias_mp)
            
            # Medida Protetiva de Urgência (80% são de urgência)
            solicitada_mpu = random.choices([True, False], weights=[80, 20], k=1)[0]
            
            # Grau de parentesco
            grau_parentesco = random.choices(
                list(pesos_parentesco.keys()),
                weights=list(pesos_parentesco.values()),
                k=1
            )[0]
            
            # Comarca (100% dos casos têm comarca definida se houver comarcas disponíveis)
            comarca = random.choice(comarcas_disponiveis) if comarcas_disponiveis else None
            
            # Seleciona município entre os municípios da comarca
            municipio_mp = None
            if comarca:
                municipios_comarca = comarca.municipios_abrangentes.all()
                municipio_mp = random.choice(list(municipios_comarca)) if municipios_comarca else None
            
            # Criar o formulário
            formulario = FormularioMedidaProtetiva.objects.create(
                data_solicitacao=data_aleatoria,
                vitima=vitima_selecionada,
                agressor=agressor_selecionado,
                periodo_mp=periodo_mp,
                solicitada_mpu=solicitada_mpu,
                comarca_competente=comarca,
                grau_parentesco_agressor=grau_parentesco,
                bairro_mp=random.choice(RUAS),
                municipio_mp=municipio_mp
            )
            
            # ✅ NOVO: Adicionar tipos de violência ao relacionamento ManyToMany
            # Cada formulário pode ter de 1 a 3 tipos de violência
            quantidade_tipos = random.choices([1, 2, 3], weights=[60, 30, 10], k=1)[0]
            tipos_selecionados = random.choices(
                tipos_violencia_disponiveis,
                weights=pesos_violencia,
                k=quantidade_tipos
            )
            
            # Adicionar tipos de violência sem duplicatas
            tipos_unicos = list(set(tipos_selecionados))
            formulario.tipo_de_violencia.set(tipos_unicos)
            
            formularios_criados += 1
            
            # Progresso a cada 50 registros
            if (i + 1) % 50 == 0:
                print(f"   ⏳ Progresso: {i + 1}/{quantidade} formulários processados...")
                
        except Exception as e:
            erros.append(f"Erro no registro {i + 1}: {str(e)}")
            continue
    
    # Relatório final
    print("\n" + "="*70)
    print("📊 RELATÓRIO DE GERAÇÃO DE FORMULÁRIOS DE MEDIDA PROTETIVA")
    print("="*70)
    print(f"✅ Formulários criados com sucesso: {formularios_criados}")
    print(f"⚠️  Formulários já existentes (ignorados): {formularios_existentes}")
    print(f"❌ Erros encontrados: {len(erros)}")
    
    if formularios_criados + len(erros) > 0:
        taxa_sucesso = (formularios_criados / (formularios_criados + len(erros))) * 100
        print(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
    
    if formularios_criados > 0:
        print("\n📋 ESTATÍSTICAS DOS FORMULÁRIOS CRIADOS:")
        
        # Estatísticas por tipo de violência
        print("\n🔍 Distribuição por Tipo de Violência:")
        for tipo in tipos_violencia_disponiveis:
            count = FormularioMedidaProtetiva.objects.filter(tipo_de_violencia=tipo).count()
            percentual = (count / formularios_criados) * 100 if formularios_criados > 0 else 0
            print(f"   • {tipo.nome}: {count} casos ({percentual:.1f}%)")
        
        # Estatísticas por grau de parentesco
        print("\n👥 Distribuição por Grau de Parentesco:")
        for grau_codigo, grau_nome in grau_parentesco_agressor_choices:
            count = FormularioMedidaProtetiva.objects.filter(
                grau_parentesco_agressor=grau_codigo
            ).count()
            if count > 0:
                percentual = (count / formularios_criados) * 100
                print(f"   • {grau_nome}: {count} casos ({percentual:.1f}%)")
        
        # Estatísticas por urgência
        urgentes = FormularioMedidaProtetiva.objects.filter(solicitada_mpu=True).count()
        nao_urgentes = FormularioMedidaProtetiva.objects.filter(solicitada_mpu=False).count()
        total_analisados = urgentes + nao_urgentes
        
        if total_analisados > 0:
            print(f"\n⚡ Medidas de Urgência:")
            print(f"   • Urgentes: {urgentes} ({(urgentes/total_analisados)*100:.1f}%)")
            print(f"   • Não urgentes: {nao_urgentes} ({(nao_urgentes/total_analisados)*100:.1f}%)")
        
        # Período médio de validade
        formularios_recentes = FormularioMedidaProtetiva.objects.all()[:100]
        if formularios_recentes:
            periodos = []
            for form in formularios_recentes:
                if form.data_solicitacao and form.periodo_mp:
                    dias_validade = (form.periodo_mp - form.data_solicitacao.date()).days
                    periodos.append(dias_validade)
            
            if periodos:
                periodo_medio = sum(periodos) / len(periodos)
                print(f"\n📅 Período Médio de Validade: {periodo_medio:.0f} dias")
        
        # Estatísticas de tipos de violência múltiplos
        formularios_multiplos = FormularioMedidaProtetiva.objects.annotate(
            num_tipos=models.Count('tipo_de_violencia')
        ).filter(num_tipos__gt=1).count()
        
        if formularios_multiplos > 0:
            percentual_multiplos = (formularios_multiplos / formularios_criados) * 100
            print(f"\n🔗 Formulários com Múltiplos Tipos de Violência: {formularios_multiplos} ({percentual_multiplos:.1f}%)")
    
    if erros:
        print(f"\n❌ DETALHES DOS ERROS ({len(erros)} total):")
        for i, erro in enumerate(erros[:10]):
            print(f"   {i+1}. {erro}")
        if len(erros) > 10:
            print(f"   ... e mais {len(erros) - 10} erros similares.")
    
    print("\n✨ Script concluído!")
    print("💡 Para visualizar os dados, acesse: /admin/sistema_justica/formulariomedidaprotetiva/")
    
    return formularios_criados


def limpar_formularios_teste():
    """
    Remove todos os formulários de medida protetiva (usar com cuidado!)
    """
    print("⚠️  AVISO: Esta função irá apagar TODOS os formulários de medida protetiva!")
    confirmacao = input("Digite 'CONFIRMAR' para continuar: ")
    
    if confirmacao == 'CONFIRMAR':
        count = FormularioMedidaProtetiva.objects.count()
        FormularioMedidaProtetiva.objects.all().delete()
        print(f"🗑️  {count} formulários foram removidos com sucesso.")
    else:
        print("❌ Operação cancelada.")


def estatisticas_formularios():
    """
    Exibe estatísticas detalhadas dos formulários cadastrados
    """
    total = FormularioMedidaProtetiva.objects.count()
    
    if total == 0:
        print("📭 Nenhum formulário de medida protetiva cadastrado.")
        return
    
    print(f"📊 ESTATÍSTICAS DOS FORMULÁRIOS DE MEDIDA PROTETIVA ({total} total)")
    print("="*60)
    
    # Por tipo de violência (usando o modelo TipoDeViolencia)
    tipos_violencia = TipoDeViolencia.objects.filter(ativo=True)
    print("\n🔍 Por Tipo de Violência:")
    for tipo in tipos_violencia:
        count = FormularioMedidaProtetiva.objects.filter(tipo_de_violencia=tipo).count()
        if count > 0:
            percentual = (count / total) * 100
            print(f"   • {tipo.nome}: {count} ({percentual:.1f}%)")
    
    # Por grau de parentesco
    print("\n👥 Por Grau de Parentesco:")
    for codigo, nome in grau_parentesco_agressor_choices:
        count = FormularioMedidaProtetiva.objects.filter(grau_parentesco_agressor=codigo).count()
        if count > 0:
            percentual = (count / total) * 100
            print(f"   • {nome}: {count} ({percentual:.1f}%)")
    
    # Por urgência
    urgentes = FormularioMedidaProtetiva.objects.filter(solicitada_mpu=True).count()
    print(f"\n⚡ Medidas de Urgência: {urgentes} ({(urgentes/total)*100:.1f}%)")
    
    # Por comarca
    com_comarca = FormularioMedidaProtetiva.objects.exclude(comarca_competente=None).count()
    print(f"\n🏛️  Com Comarca Definida: {com_comarca} ({(com_comarca/total)*100:.1f}%)")
    
    # Formulários mais recentes
    print(f"\n📅 Formulários Mais Recentes:")
    recentes = FormularioMedidaProtetiva.objects.order_by('-data_solicitacao')[:5]
    for form in recentes:
        data_str = form.data_solicitacao.strftime('%d/%m/%Y %H:%M')
        tipos_str = ", ".join([tipo.nome for tipo in form.tipo_de_violencia.all()])
        print(f"   • {data_str} - {form.vitima.nome} vs {form.agressor.nome}")
        print(f"     Tipos: {tipos_str if tipos_str else 'Nenhum'}")


if __name__ == "__main__":
    # Adicionar import necessário para anotações
    
    
    # Executa a função principal quando o script é chamado diretamente
    criar_formularios_mp_aleatorios()