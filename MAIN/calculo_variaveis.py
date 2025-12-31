# -*- coding: utf-8 -*-
"""
Módulo para cálculos de variáveis e estatísticas do PIEVDCS
Path: MAIN/calculo_variaveis.py

Funcionalidades:
- Estatísticas de tipos de violência
- Análise de medidas protetivas
- Ranking de municípios violentos
- Cálculo de reincidência
- Incidências mensais e anuais

Autor: OgliariNatan
Data: 2025
"""

from datetime import date, timedelta
from collections import Counter
from django.db.models import Q, Count
from django.core.cache import cache

from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from sistema_justica.models.base import TipoDeViolencia
from seguranca_publica.models.militar import OcorrenciaMilitar
from seguranca_publica.models.civil import OcorrenciaCivil
from seguranca_publica.models.base import grau_parentesco_agressor_choices

""" Configuraçao de decoradores para debug """
import os
from dotenv import load_dotenv

var_debug = os.getenv('DEBUG', False) #Carrega apenas a variavel de debug

if var_debug == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo, calcula_tempo_fun
    checked_debug_decorador = calcula_tempo
    checked_debug_decorador_fun = calcula_tempo_fun
    
else:
    checked_debug_decorador = None
    checked_debug_decorador_fun = None

""" Fim da configuraçao de decoradores para debug """



# ========================================================================
# FUNÇÕES AUXILIARES PARA TIPOS DE VIOLÊNCIA
# ✅ Lazy loading: só executa quando chamada, não no import
# ========================================================================

@checked_debug_decorador_fun
def obter_tipos_violencia_ativos():
    """
    Obtém lista de tipos de violência ativos do banco de dados.
    Usa cache Django para melhorar performance.
    
    Adaptado para modelo simplificado (apenas id, nome, descricao, ativo)
    
    Returns:
        list: Lista de dicionários com 'id' e 'nome'
        
    Exemplo:
        [
            {'id': 1, 'nome': 'Violência Física'},
            {'id': 2, 'nome': 'Violência Psicológica'},
            ...
        ]
    """
    cache_key = 'pievdcs_tipos_violencia_ativos'
    tipos = cache.get(cache_key)
    
    if tipos is None:
        try:
            tipos = list(
                TipoDeViolencia.objects
                .filter(ativo=True)
                .values('id', 'nome')
                .order_by('nome')
            )
            cache.set(cache_key, tipos, 3600)  # Cache por 1 hora
        except Exception:
            # ✅ Fallback: retorna lista vazia se tabela não existe
            tipos = []
    
    return tipos


def obter_ids_tipos_violencia():
    """
    Retorna apenas os IDs dos tipos de violência ativos.
    
    Returns:
        list: Lista de IDs
    """
    return [tipo['id'] for tipo in obter_tipos_violencia_ativos()]


def obter_mapeamento_tipos_violencia():
    """
    Cria dicionário mapeando ID → Nome dos tipos de violência.
    
    Returns:
        dict: {id: nome}
        
    Exemplo:
        {1: 'Violência Física', 2: 'Violência Psicológica', ...}
    """
    return {tipo['id']: tipo['nome'] for tipo in obter_tipos_violencia_ativos()}



LABELS_TIPO_PARENTESCO = dict(grau_parentesco_agressor_choices)


# ========================================================================
# CLASSE: COMARCAS COM MEDIDAS PROTETIVAS
# ========================================================================

class PegarComarcasComMP:
    """
    Classe responsável por classificar comarcas que possuem 
    Medidas Protetivas e seus respectivos números de ocorrências.
    """
    
    def pegar_comarcas_com_mp(self):
        """
        Obtém comarcas com medidas protetivas ordenadas por quantidade.
        
        Returns:
            QuerySet: Comarcas com total de formulários MP
        """
        queryset = (
            FormularioMedidaProtetiva.objects
            .values('comarca_competente__nome')
            .annotate(total=Count('ID'))
            .order_by('-total')
        )
        return queryset


# ========================================================================
# CLASSE: ESTATÍSTICAS DE TIPOS DE VIOLÊNCIA
# ========================================================================

class TipoViolenciaStats:
    """
    Classe para cálculo de estatísticas relacionadas a tipos de violência.
    
    Suporta ManyToManyField: uma ocorrência pode ter múltiplos tipos.
    """
    
    @property
    def tipos_violencia_ids(self):
        """✅ Lazy property: carrega IDs apenas quando necessário"""
        return obter_ids_tipos_violencia()
    
    @property
    def labels_tipo_violencia(self):
        """✅ Lazy property: carrega labels apenas quando necessário"""
        return obter_mapeamento_tipos_violencia()
    
    def conta_violencias_por_mes(self, mes, ano):
        """
        Conta ocorrências de cada tipo de violência em um mês específico.
        
        ⚠️ Como tipos_de_violencia é ManyToMany, um formulário pode ter 
        múltiplos tipos. Cada relacionamento é contado individualmente.
        
        Args:
            mes (int): Número do mês (1-12)
            ano (int): Ano (ex: 2025)
            
        Returns:
            Counter: {tipo_id: quantidade}
        """
        contagem = Counter()
        
        filtro_data = Q(data__month=mes, data__year=ano)
        filtro_data_formulario = Q(data_solicitacao__month=mes, data_solicitacao__year=ano)
        
        # ✅ Usa property ao invés de variável global
        for tipo_id in self.tipos_violencia_ids:
            # Polícia Militar
            total_pm = (
                OcorrenciaMilitar.objects
                .filter(filtro_data, tipos_de_violencia__id=tipo_id)
                .distinct()
                .count()
            )
            
            # Polícia Civil
            total_pc = (
                OcorrenciaCivil.objects
                .filter(filtro_data, tipos_de_violencia__id=tipo_id)
                .distinct()
                .count()
            )
            
            # Formulário de Medida Protetiva
            total_mp = (
                FormularioMedidaProtetiva.objects
                .filter(filtro_data_formulario, tipos_de_violencia__id=tipo_id)
                .distinct()
                .count()
            )
            
            contagem[tipo_id] = total_pm + total_pc + total_mp
        
        return contagem
    
    def verifica_maior_violencia_por_mes(self):
        """
        Identifica tipo de violência mais frequente no mês atual
        e compara com o mês anterior.
        
        Returns:
            dict: Estatísticas comparativas entre meses
        """
        hoje = date.today()
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        # Calcular mês anterior
        primeiro_dia_mes_atual = hoje.replace(day=1)
        data_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)
        mes_anterior = data_mes_anterior.month
        ano_anterior = data_mes_anterior.year
        
        # Contagens
        atual = self.conta_violencias_por_mes(mes_atual, ano_atual)
        anterior = self.conta_violencias_por_mes(mes_anterior, ano_anterior)
        
        # ✅ Usa property ao invés de variável global
        labels = self.labels_tipo_violencia
        
        # Tipo mais comum no mês atual
        if atual:
            tipo_id_atual, total_atual = atual.most_common(1)[0]
            tipo_atual = labels.get(tipo_id_atual, f"ID {tipo_id_atual}")
        else:
            tipo_atual = "Nenhum registro"
            total_atual = 0
        
        # Tipo mais comum no mês anterior
        if anterior:
            tipo_id_anterior, total_anterior = anterior.most_common(1)[0]
            tipo_anterior = labels.get(tipo_id_anterior, f"ID {tipo_id_anterior}")
        else:
            tipo_anterior = "Nenhum registro"
            total_anterior = 0
        
        # Porcentagem do tipo mais comum no mês anterior
        total_violencias_mes_anterior = sum(anterior.values())
        porcentagem_anterior = (
            round((total_anterior / total_violencias_mes_anterior) * 100, 2)
            if total_violencias_mes_anterior > 0 else 0
        )
        
        # Variação percentual
        if total_anterior > 0:
            variacao = round(((total_atual - total_anterior) / total_anterior) * 100, 2)
        else:
            variacao = 100.0 if total_atual > 0 else 0.0
        
        return {
            "mes_atual": {
                "tipo": tipo_atual,
                "total": total_atual
            },
            "mes_anterior": {
                "tipo": tipo_anterior,
                "total": total_anterior,
                "porcentagem": porcentagem_anterior
            },
            "variacao_percentual": variacao
        }


# ========================================================================
# CLASSE: ESTATÍSTICAS DE MEDIDAS PROTETIVAS
# ========================================================================

class MedidasProtetivas:
    """Classe para cálculo de estatísticas de Medidas Protetivas"""
    
    def porcentagem_mes_anterior(self):
        """
        Calcula porcentagem de medidas protetivas solicitadas no mês anterior.
        
        Returns:
            dict: Porcentagem e total de medidas solicitadas
        """
        hoje = date.today()
        primeiro_dia_mes_atual = hoje.replace(day=1)
        data_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)
        mes_anterior = data_mes_anterior.month
        ano_anterior = data_mes_anterior.year
        
        # Filtros por data
        filtro_ocorrencias = Q(data__month=mes_anterior, data__year=ano_anterior)
        filtro_formulario = Q(data_solicitacao__month=mes_anterior, data_solicitacao__year=ano_anterior)
        
        # Medidas protetivas solicitadas
        solicitadas = (
            OcorrenciaMilitar.objects.filter(filtro_ocorrencias, status_MP='SO').count() +
            OcorrenciaCivil.objects.filter(filtro_ocorrencias, status_MP='SO').count() +
            FormularioMedidaProtetiva.objects.filter(filtro_formulario, solicitada_mpu=True).count()
        )
        
        # Total de ocorrências
        total_ocorrencias = (
            OcorrenciaMilitar.objects.filter(filtro_ocorrencias).count() +
            OcorrenciaCivil.objects.filter(filtro_ocorrencias).count() +
            FormularioMedidaProtetiva.objects.filter(filtro_formulario).count()
        )
        
        # Porcentagem
        porcentagem = (
            round((solicitadas / total_ocorrencias) * 100, 2) 
            if total_ocorrencias > 0 else 0
        )
        
        return {
            "porcentagem": porcentagem,
            "total": solicitadas,
            "total_ocorrencias": total_ocorrencias
        }


# ========================================================================
# CLASSE: MUNICÍPIOS MAIS VIOLENTOS
# ========================================================================

class MunicipiosViolentos:
    """Classe para calcular ranking de municípios mais violentos"""
    
    def municipios_mais_violentos(self, top=5):
        """
        Identifica municípios com mais ocorrências de violência.
        
        Args:
            top (int): Quantidade de municípios a retornar. Padrão: 5
            
        Returns:
            list: Lista de tuplas (município, total) ordenada por total
        """
        # Ocorrências militares
        militares = (
            OcorrenciaMilitar.objects
            .values('municipio_ocorrencia__nome')
            .annotate(total=Count('id'))
        )
        
        # Ocorrências civis
        civis = (
            OcorrenciaCivil.objects
            .values('municipio_ocorrencia__nome')
            .annotate(total=Count('id'))
        )
        
        # Formulários de medida protetiva
        formularios = (
            FormularioMedidaProtetiva.objects
            .values('municipio_mp__nome')
            .annotate(total=Count('ID'))
        )
        
        # Agregar totais por município
        contagem = {}
        
        for qs in [militares, civis]:
            for item in qs:
                nome = item.get('municipio_ocorrencia__nome')
                if nome:
                    contagem[nome] = contagem.get(nome, 0) + item['total']
        
        for item in formularios:
            nome = item.get('municipio_mp__nome')
            if nome:
                contagem[nome] = contagem.get(nome, 0) + item['total']
        
        # Ordenar e retornar top N
        ranking = sorted(contagem.items(), key=lambda x: x[1], reverse=True)
        return ranking[:top]


# ========================================================================
# CLASSE: GRAU DE PARENTESCO
# ========================================================================

class GrauParentesco:
    """Classe para análise de grau de parentesco entre vítima e agressor"""
    
    def parentesco_mais_comum(self):
        """
        Identifica o grau de parentesco mais comum.
        
        Returns:
            dict: Tipo de parentesco e total de ocorrências
        """
        parentescos = (
            FormularioMedidaProtetiva.objects
            .values('grau_parentesco_agressor')
            .annotate(total=Count('ID'))
            .order_by('-total')
        )
        
        if parentescos:
            tipo_mais_comum = parentescos[0]['grau_parentesco_agressor']
            tipo_mais_comum_label = LABELS_TIPO_PARENTESCO.get(
                tipo_mais_comum, 
                tipo_mais_comum
            )
            return {
                "grau_parentesco": tipo_mais_comum_label,
                "total": parentescos[0]['total']
            }
        
        return None


# ========================================================================
# CLASSE: REINCIDÊNCIA
# ========================================================================

class BuscaReincidencia:
    """Classe para cálculo de reincidência de agressores e vítimas"""
    
    def ocorrencias_reincidentes(self):
        """
        Calcula estatísticas de reincidência de agressores.
        
        Returns:
            dict: Lista de reincidentes e porcentagens
        """
        # Agressores com mais de uma ocorrência
        reincidentes = (
            FormularioMedidaProtetiva.objects
            .values('agressor__id', 'agressor__nome', 'agressor__cpf')
            .annotate(total_mp=Count('ID'))
            .filter(total_mp__gt=1)
            .order_by('-total_mp')
        )
        
        # Total de formulários
        total_formularios = FormularioMedidaProtetiva.objects.count()
        
        # Quantidade de agressores reincidentes
        qtd_reincidentes_agressor = reincidentes.count()
        
        # Porcentagem de reincidência
        porcentagem_agressor_reincidente = (
            round((qtd_reincidentes_agressor / total_formularios) * 100, 2) 
            if total_formularios > 0 else 0
        )
        
        # ⚠️ TODO: Implementar cálculo de reincidência de vítimas
        # Por enquanto, valor fixo
        porcentagem_vitima_reincidente = 6
        
        return {
            "lista": list(reincidentes),
            "reincidencia_agressor": porcentagem_agressor_reincidente,
            "reincidencia_vitima": porcentagem_vitima_reincidente,
            "total_formularios": total_formularios,
            "total_reincidentes": qtd_reincidentes_agressor
        }


# ========================================================================
# CLASSE: INCIDÊNCIAS POR MÊS
# ========================================================================

class IncidenciasPorMes:
    """
    Classe para cálculo de incidências de violência doméstica por período.
    Agrega dados de todas as fontes (PM, PC, MP).
    """
    
    # Mapeamento de meses em português brasileiro
    MESES_MAP = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    
    def calcular_incidencias_ano_atual(self):
        """
        Calcula incidências por mês do ano atual.
        
        Returns:
            dict: {mes: total} para cada mês do ano
        """
        hoje = date.today()
        ano_atual = hoje.year
        
        return self.calcular_incidencias_por_periodo(
            ano=ano_atual, 
            mes_inicio=1, 
            mes_fim=12
        )
    
    def calcular_incidencias_por_periodo(self, ano=None, mes_inicio=1, mes_fim=12):
        """
        Calcula incidências para um período específico.
        
        Args:
            ano (int, optional): Ano para cálculo. Se None, usa ano atual
            mes_inicio (int): Mês inicial (1-12). Padrão: 1
            mes_fim (int): Mês final (1-12). Padrão: 12
            
        Returns:
            dict: {mes: total} para o período especificado
        """
        if ano is None:
            ano = date.today().year
        
        incidencias = {}
        
        for mes_num in range(mes_inicio, mes_fim + 1):
            filtro_ocorrencias = Q(data__month=mes_num, data__year=ano)
            filtro_formulario = Q(data_solicitacao__month=mes_num, data_solicitacao__year=ano)
            
            # Contar cada fonte
            total_militar = OcorrenciaMilitar.objects.filter(filtro_ocorrencias).count()
            total_civil = OcorrenciaCivil.objects.filter(filtro_ocorrencias).count()
            total_mp = FormularioMedidaProtetiva.objects.filter(filtro_formulario).count()
            
            # Somar total
            total_mes = total_militar + total_civil + total_mp
            
            # Mapear para nome do mês em português brasileiro
            mes_nome = self.MESES_MAP[mes_num]
            incidencias[mes_nome] = total_mes
        
        return incidencias
    
    def comparar_com_ano_anterior(self):
        """
        Compara incidências do ano atual com o ano anterior.
        
        Returns:
            dict: Dados comparativos completos com variação percentual
        """
        hoje = date.today()
        ano_atual = hoje.year
        ano_anterior = ano_atual - 1
        
        # Calcular incidências
        atual = self.calcular_incidencias_por_periodo(ano=ano_atual)
        anterior = self.calcular_incidencias_por_periodo(ano=ano_anterior)
        
        # Calcular variação percentual por mês
        variacao = {}
        for mes in atual.keys():
            total_atual = atual[mes]
            total_anterior = anterior.get(mes, 0)
            
            if total_anterior > 0:
                var_perc = round(((total_atual - total_anterior) / total_anterior) * 100, 2)
            else:
                var_perc = 100.0 if total_atual > 0 else 0.0
            
            variacao[mes] = var_perc
        
        return {
            'ano_atual': {
                'ano': ano_atual,
                'dados': atual,
                'total': sum(atual.values())
            },
            'ano_anterior': {
                'ano': ano_anterior,
                'dados': anterior,
                'total': sum(anterior.values())
            },
            'variacao_percentual': variacao
        }


# ========================================================================
# INSTÂNCIAS GLOBAIS DAS CLASSES
# Conforme padrão PIEVDCS para uso em templates e views
# ========================================================================

if var_debug == 'True':
    print("\nInicializando instâncias globais de cálculo de variáveis...\n")

tipoviolencia = TipoViolenciaStats()
medidasprotetivas = MedidasProtetivas()
municipiosviolentos = MunicipiosViolentos()
grauparentesco = GrauParentesco()
reincidencia = BuscaReincidencia()
pegarcomarcascommp = PegarComarcasComMP()
incidenciaspormes = IncidenciasPorMes()