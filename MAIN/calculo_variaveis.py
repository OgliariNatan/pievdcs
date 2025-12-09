from datetime import date, timedelta
from collections import Counter
from django.db.models import Q, Count
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from seguranca_publica.models.militar import OcorrenciaMilitar
from seguranca_publica.models.civil import OcorrenciaCivil
from seguranca_publica.models.base import tipo_de_violencia_choices, grau_parentesco_agressor_choices

TIPOS_VIOLENCIA = [tipo[0] for tipo in tipo_de_violencia_choices]
LABELS_TIPO_VIOLENCIA = dict(tipo_de_violencia_choices)
LABELS_TIPO_PARENTESCO = dict(grau_parentesco_agressor_choices)


class PegarComarcasComMP:
    """
    Classe responsavel por classificar todas as comarcas que possuem Medidas Protetivas e seus respectivos numeros de ocorrências. 
    """
    def pegar_comarcas_com_mp(self):
        # Consulta para obter as comarcas com medidas protetivas
        queryset = (
            FormularioMedidaProtetiva.objects
            .values('comarca_competente__nome')
            .annotate(total=Count('ID'))
            .order_by('-total')
        )
        #print(f"Comarcas com Medidas Protetivas: {queryset}")
        return queryset


class TipoViolencia:
    def conta_violencias_por_mes(self, mes, ano):
        contagem = Counter()
        for tipo in TIPOS_VIOLENCIA:
            filtro_data = Q(data__month=mes, data__year=ano)
            filtro_data_formulario = Q(data_solicitacao__month=mes, data_solicitacao__year=ano)

            total = (
                OcorrenciaMilitar.objects.filter(filtro_data, tipo_de_violencia=tipo).count()
                + OcorrenciaCivil.objects.filter(filtro_data, tipo_de_violencia=tipo).count()
                + FormularioMedidaProtetiva.objects.filter(filtro_data_formulario, tipo_de_violencia=tipo).count()

            )
            contagem[tipo] = total
        return contagem

    def verifica_maior_violencia_por_mes(self):
        hoje = date.today()
        mes_atual = hoje.month
        ano_atual = hoje.year
        mes_anterior = (hoje.replace(day=1) - timedelta(days=1)).month
        ano_anterior = (hoje.replace(day=1) - timedelta(days=1)).year

        atual = tipoviolencia.conta_violencias_por_mes(mes_atual, ano_atual)
        anterior = tipoviolencia.conta_violencias_por_mes(mes_anterior, ano_anterior)

        tipo_atual, total_atual = atual.most_common(1)[0]
        tipo_anterior, total_anterior = anterior.most_common(1)[0]

        total_violencias_mes_anterior = sum(anterior.values())
        porcentagem_anterior = (
            round((total_anterior / total_violencias_mes_anterior) * 100, 2)
            if total_violencias_mes_anterior > 0 else 0
        )

        # Cálculo da variação percentual
        variacao = (
            round(((total_atual - total_anterior) / total_anterior) * 100, 2)
            if total_anterior > 0 else 0
        )
        tipo_atual = LABELS_TIPO_VIOLENCIA.get(tipo_atual, tipo_atual)
        tipo_anterior = LABELS_TIPO_VIOLENCIA.get(tipo_anterior, tipo_anterior)
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
            "variacao_percentual": variacao  # Positiva se aumentou, negativa se diminuiu
        }
    

class MedidasProtetivas:
    
    def porcentagem_mes_anterior(self):
        hoje = date.today()
        primeiro_dia_mes_atual = hoje.replace(day=1)
        data_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)
        mes_anterior = data_mes_anterior.month
        ano_anterior = data_mes_anterior.year

        # Filtros por data
        filtro_ocorrencias = Q(data__month=mes_anterior, data__year=ano_anterior)
        filtro_formulario = Q(data_solicitacao__month=mes_anterior, data_solicitacao__year=ano_anterior)

        # Medidas protetivas solicitadas no mês anterior
        solicitadas = (
            OcorrenciaMilitar.objects.filter(filtro_ocorrencias, status_MP='SO').count() +
            OcorrenciaCivil.objects.filter(filtro_ocorrencias, status_MP='SO').count() +
            FormularioMedidaProtetiva.objects.filter(filtro_formulario, solicitada_mpu=True).count()
        )

        # Total de ocorrências no mês anterior (independente de medida protetiva)
        total_ocorrencias = (
            OcorrenciaMilitar.objects.filter(filtro_ocorrencias).count() +
            OcorrenciaCivil.objects.filter(filtro_ocorrencias).count() +
            FormularioMedidaProtetiva.objects.filter(filtro_formulario).count()
        )

        # Cálculo da porcentagem
        porcentagem = round((solicitadas / total_ocorrencias) * 100, 2) if total_ocorrencias > 0 else 0
        

        return {
            "porcentagem": porcentagem,
            "total": solicitadas,
        }

class MunicipiosViolentos:
    """
    Classe para calcular os municípios mais violentos
    """
    def municipios_mais_violentos(self, top=2):
        # Ocorrências militares
        militares = (
            OcorrenciaMilitar.objects.values('municipio_ocorrencia__nome').annotate(total=Count('id'))
        )
        # Ocorrências civis
        civis = (
            OcorrenciaCivil.objects.values('municipio_ocorrencia__nome').annotate(total=Count('id'))
        )
        # Formulários de medida protetiva
        formularios = (
            FormularioMedidaProtetiva.objects.values('municipio_mp__nome').annotate(total=Count('ID'))
        )

        # Junta todos em um dicionário somando os totais
        contagem = {}
        for qs in [militares, civis]:
            for item in qs:
                nome = item['municipio_ocorrencia__nome']
                if nome:
                    contagem[nome] = contagem.get(nome, 0) + item['total']
        for item in formularios:
            nome = item['municipio_mp__nome']
            if nome:
                contagem[nome] = contagem.get(nome, 0) + item['total']

        # Ordena do maior para o menor
        ranking = sorted(contagem.items(), key=lambda x: x[1], reverse=True)
        return ranking[:top]

class GrauPrarentesco:
    """
    Classe para calcular o grau de parentesco mais comum entre vítimas e agressores
    """
    def parentesco_mais_comum(self):
        # Consulta para obter o grau de parentesco mais comum
        parentescos = (
            FormularioMedidaProtetiva.objects.values('grau_parentesco_agressor')
            .annotate(total=Count('ID'))
            .order_by('-total')
        )
        if parentescos:
            tipo_mais_comum = parentescos[0]['grau_parentesco_agressor']
            tipo_mais_comum_label = LABELS_TIPO_PARENTESCO.get(tipo_mais_comum, tipo_mais_comum)
            return {
            "grau_parentesco": tipo_mais_comum_label,
            "total": parentescos[0]['total']
            }
        return None
    
class BuscaReincidencia:
    """
    Classe para calcular a reincidência de ocorrências
    """
    def ocorrencias_reincidentes(self):
        # Lista dos agressores reincidentes com dados pessoais
        reincidentes = (
            FormularioMedidaProtetiva.objects
            .values('agressor__id', 'agressor__nome', 'agressor__cpf')
            .annotate(total_mp=Count('ID'))
            .filter(total_mp__gt=1)
            .order_by('-total_mp')
        )
        reincidentes_1 = (
            FormularioMedidaProtetiva.objects.all().count()
        )
        # Total de agressores únicos
        total_agressores = (
            FormularioMedidaProtetiva.objects
            .values('agressor__id')
            .distinct()
            .count()
        )

        # Total de agressores únicos com mais de uma ocorrência
        qtd_reincidentes_agressor = (
            FormularioMedidaProtetiva.objects
            .values('agressor__id')
            .annotate(total_mp=Count('ID'))
            .filter(total_mp__gt=1)
            .count()
        )
        

        porcentagem_agressor_reincidente = round((qtd_reincidentes_agressor / reincidentes_1) * 100, 2) if reincidentes_1 > 0 else 0
        
        return {
            "lista": list(reincidentes),
            "reincidencia_agressor": porcentagem_agressor_reincidente,
            "reincidencia_vitima": 6  # Esse número está fixo — podemos revisar se quiser
        }

class IncidenciasPorMes:
    """
    Classe responsável por calcular a quantidade de incidências de violência doméstica por mês.
    Agrega dados de OcorrenciaMilitar, OcorrenciaCivil e FormularioMedidaProtetiva.
    """
    
    def calcular_incidencias_ano_atual(self):
        """
        Calcula a quantidade de incidências por mês do ano atual.
        
        Returns:
            dict: Dicionário com meses em português (lowercase) como chaves e totais como valores.
                 Exemplo: {'janeiro': 15, 'fevereiro': 20, ...}
        """
        hoje = date.today()
        ano_atual = hoje.year
        
        # Mapeamento de número do mês para nome em português
        meses_map = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        
        # Inicializar todos os meses com zero
        incidencias = {mes: 0 for mes in meses_map.values()}
        
        # Iterar pelos 12 meses
        for mes_num in range(1, 13):
            filtro_ocorrencias = Q(data__month=mes_num, data__year=ano_atual)
            filtro_formulario = Q(data_solicitacao__month=mes_num, data_solicitacao__year=ano_atual)
            
            # Contar ocorrências de cada fonte
            total_militar = OcorrenciaMilitar.objects.filter(filtro_ocorrencias).count()
            total_civil = OcorrenciaCivil.objects.filter(filtro_ocorrencias).count()
            total_mp = FormularioMedidaProtetiva.objects.filter(filtro_formulario).count()
            
            # Somar total do mês
            total_mes = total_militar + total_civil + total_mp
            
            # Atribuir ao mês correspondente
            mes_nome = meses_map[mes_num]
            incidencias[mes_nome] = total_mes
        
        return incidencias
    
    def calcular_incidencias_por_periodo(self, ano=None, mes_inicio=1, mes_fim=12):
        """
        Calcula incidências para um período específico.
        
        Args:
            ano (int, optional): Ano para cálculo. Se None, usa ano atual.
            mes_inicio (int): Mês inicial (1-12). Padrão: 1 (janeiro)
            mes_fim (int): Mês final (1-12). Padrão: 12 (dezembro)
            
        Returns:
            dict: Dicionário com meses e totais do período especificado.
        """
        if ano is None:
            ano = date.today().year
        
        meses_map = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        
        incidencias = {}
        
        for mes_num in range(mes_inicio, mes_fim + 1):
            filtro_ocorrencias = Q(data__month=mes_num, data__year=ano)
            filtro_formulario = Q(data_solicitacao__month=mes_num, data_solicitacao__year=ano)
            
            total_mes = (
                OcorrenciaMilitar.objects.filter(filtro_ocorrencias).count() +
                OcorrenciaCivil.objects.filter(filtro_ocorrencias).count() +
                FormularioMedidaProtetiva.objects.filter(filtro_formulario).count()
            )
            
            mes_nome = meses_map[mes_num]
            incidencias[mes_nome] = total_mes
        
        return incidencias
    
    def comparar_com_ano_anterior(self):
        """
        Compara incidências do ano atual com o ano anterior.
        
        Returns:
            dict: Contém dados do ano atual, ano anterior e variação percentual.
        """
        hoje = date.today()
        ano_atual = hoje.year
        ano_anterior = ano_atual - 1
        
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
                var_perc = 100 if total_atual > 0 else 0
            
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



tipoviolencia = TipoViolencia()
medidasprotetivas = MedidasProtetivas()
municipiosviolentos = MunicipiosViolentos()
grauparentesco = GrauPrarentesco()
reincidencia = BuscaReincidencia()
pegarcomarcascommp = PegarComarcasComMP()
incidenciaspormes = IncidenciasPorMes()

