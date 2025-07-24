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
        # Consulta para obter as ocorrências com mais de uma ocorrência do mesmo agressor
        reincidentes = (
            OcorrenciaMilitar.objects.values('agressor__nome')
            .annotate(total=Count('id'))
            .filter(total__gt=1)
        )
        return reincidentes




tipoviolencia = TipoViolencia()
medidasprotetivas = MedidasProtetivas()
municipiosviolentos = MunicipiosViolentos()
grauparentesco = GrauPrarentesco()
reincidencia = BuscaReincidencia()
