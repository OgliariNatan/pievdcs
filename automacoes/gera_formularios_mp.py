"""
Script para gerar dados fictícios de FormularioMedidaProtetiva (Defensoria Pública)
Gera 500 registros de solicitações de medida protetiva com dados realistas brasileiros.

Para executar:
1. Abra o Django shell: python manage.py shell
2. Execute: from automacoes.gera_formularios_mp import criar_formularios_mp_aleatorios
3. Execute: criar_formularios_mp_aleatorios()
"""

import random
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Configuração do Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MAIN.settings')
    django.setup()

from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from sistema_justica.models.base import Vitima_dados, Agressor_dados
from sistema_justica.models.poder_judiciario import ComarcasPoderJudiciario
from seguranca_publica.models.base import tipo_de_violencia_choices, grau_parentesco_agressor_choices


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
    
    if total_vitimas < 50:
        print(f"⚠️  AVISO: Apenas {total_vitimas} vítimas cadastradas. Recomenda-se ter pelo menos 50.")
        print("   Execute primeiro o script gera_vitimas.py para criar mais dados.")
    
    if total_agressores < 50:
        print(f"⚠️  AVISO: Apenas {total_agressores} agressores cadastrados. Recomenda-se ter pelo menos 50.")
        print("   Execute primeiro o script gera_agressores.py para criar mais dados.")
        
    if total_comarcas < 5:
        print(f"⚠️  AVISO: Apenas {total_comarcas} comarcas cadastradas. Alguns formulários não terão comarca.")
    
    print(f"📊 Dados disponíveis: {total_vitimas} vítimas, {total_agressores} agressores, {total_comarcas} comarcas")
    
    # Listas para seleção aleatória
    vitimas_disponiveis = list(Vitima_dados.objects.all())
    agressores_disponiveis = list(Agressor_dados.objects.all())
    comarcas_disponiveis = list(ComarcasPoderJudiciario.objects.all())
    
    # Choices para seleção aleatória
    tipos_violencia = [choice[0] for choice in tipo_de_violencia_choices]
    graus_parentesco = [choice[0] for choice in grau_parentesco_agressor_choices]

    # Lista de ruas fictícias comuns (reutilizando)
    RUAS = [
        "Rua das Flores", "Rua São João", "Rua Santa Maria", "Rua XV de Novembro",
        "Rua Tiradentes", "Rua Dom Pedro II", "Rua Getúlio Vargas", "Rua Presidente Vargas",
        "Rua José de Alencar", "Rua Santos Dumont", "Rua Castro Alves", "Rua Rui Barbosa",
        "Rua Marechal Deodoro", "Rua Benjamin Constant", "Rua Sete de Setembro",
        "Rua Coronel Oliveira", "Rua Major Silva", "Rua Capitão Santos", "Rua Doutor Lima",
        "Rua Professor Almeida", "Avenida Brasil", "Avenida Independência", "Avenida Liberdade",
        "Travessa das Palmeiras", "Travessa São José", "Alameda dos Ipês"
    ]
    
    # Distribuição de períodos de medida protetiva (em dias)
    periodos_mp_dias = [120, 180, 240, 300, 360]  # Mais comum: 120 dias
    pesos_periodos = [40, 20, 15, 10, 8]  # 120 dias é mais provável
    
    # Distribuição de tipos de violência (baseada em estatísticas reais)
    pesos_violencia = {
        'Fisica': 35,
        'Psicologica': 25,
        'Sexual': 15,
        'Patrimonial': 12,
        'Moral': 13
    }
    
    # Distribuição de graus de parentesco (baseada em estatísticas reais)
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
            
            # Verificar se já existe um formulário com essa combinação vítima-agressor (Poderia pular esta verificação)
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
            
            # Período da medida protetiva (120 dias é o padrão, mas pode variar)
            dias_mp = random.choices(periodos_mp_dias, weights=pesos_periodos, k=1)[0]
            periodo_mp = data_aleatoria.date() + timedelta(days=dias_mp)
            
            # Medida Protetiva de Urgência (90% são de urgência)
            solicitada_mpu = random.choices([True, False], weights=[90, 10], k=1)[0]
            
            # Tipo de violência com distribuição realista
            tipo_violencia = random.choices(
                list(pesos_violencia.keys()), 
                weights=list(pesos_violencia.values()), 
                k=1
            )[0]
            
            # Grau de parentesco com distribuição realista
            grau_parentesco = random.choices(
                list(pesos_parentesco.keys()),
                weights=list(pesos_parentesco.values()),
                k=1
            )[0]
            
            # Comarca (100% dos casos têm comarca definida)
            comarca = random.choice(comarcas_disponiveis)
            
            
            # Seleciona município entre os municípios da comarca
            municipios_comarca = comarca.municipios_abrangentes.all()
            municipio_mp = random.choice(municipios_comarca) if municipios_comarca else None
            
            # Criar o formulário
            formulario = FormularioMedidaProtetiva.objects.create(
                data_solicitacao=data_aleatoria,
                vitima=vitima_selecionada,
                agressor=agressor_selecionado,
                periodo_mp=periodo_mp,
                solicitada_mpu=solicitada_mpu,
                tipo_de_violencia=tipo_violencia,
                comarca_competente=comarca,
                grau_parentesco_agressor=grau_parentesco,
                bairro_mp=random.choice(RUAS),
                municipio_mp=municipio_mp
            )
            
            formularios_criados += 1
            
                
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
    print(f"📈 Taxa de sucesso: {(formularios_criados/(formularios_criados+len(erros))*100):.1f}%")
    
    if formularios_criados > 0:
        print("\n📋 ESTATÍSTICAS DOS FORMULÁRIOS CRIADOS:")
        
        # Estatísticas por tipo de violência
        print("\n🔍 Distribuição por Tipo de Violência:")
        for tipo_violencia in tipos_violencia:
            count = FormularioMedidaProtetiva.objects.filter(tipo_de_violencia=tipo_violencia).count()
            print(f"   • {dict(tipo_de_violencia_choices)[tipo_violencia]}: {count} casos")
        
        # Estatísticas por grau de parentesco
        print("\n👥 Distribuição por Grau de Parentesco:")
        for grau in graus_parentesco:
            count = FormularioMedidaProtetiva.objects.filter(grau_parentesco_agressor=grau).count()
            print(f"   • {dict(grau_parentesco_agressor_choices)[grau]}: {count} casos")
        
        # Estatísticas por urgência
        urgentes = FormularioMedidaProtetiva.objects.filter(solicitada_mpu=True).count()
        nao_urgentes = FormularioMedidaProtetiva.objects.filter(solicitada_mpu=False).count()
        print(f"\n⚡ Medidas de Urgência:")
        print(f"   • Urgentes: {urgentes} ({(urgentes/(urgentes+nao_urgentes)*100):.1f}%)")
        print(f"   • Não urgentes: {nao_urgentes} ({(nao_urgentes/(urgentes+nao_urgentes)*100):.1f}%)")
        
        # Período médio de validade
        formularios_recentes = FormularioMedidaProtetiva.objects.all()[:100]  # Amostra de 100
        if formularios_recentes:
            periodos = []
            for form in formularios_recentes:
                if form.data_solicitacao and form.periodo_mp:
                    dias_validade = (form.periodo_mp - form.data_solicitacao.date()).days
                    periodos.append(dias_validade)
            
            if periodos:
                periodo_medio = sum(periodos) / len(periodos)
                print(f"\n📅 Período Médio de Validade: {periodo_medio:.0f} dias")
    
    if erros:
        print(f"\n❌ DETALHES DOS ERROS ({len(erros)} total):")
        for i, erro in enumerate(erros[:10]):  # Mostra apenas os 10 primeiros erros
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
    
    # Por tipo de violência
    print("\n🔍 Por Tipo de Violência:")
    for codigo, nome in tipo_de_violencia_choices:
        count = FormularioMedidaProtetiva.objects.filter(tipo_de_violencia=codigo).count()
        if count > 0:
            percentual = (count / total) * 100
            print(f"   • {nome}: {count} ({percentual:.1f}%)")
    
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
        print(f"   • {data_str} - {form.vitima.nome} vs {form.agressor.nome}")


if __name__ == "__main__":
    # Executa a função principal quando o script é chamado diretamente
    criar_formularios_mp_aleatorios()
