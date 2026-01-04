# -*- coding: utf-8 -*-
"""
Script para buscar municípios por estado via API do IBGE e cadastrá-los no banco.

Uso sugerido no shell Django:
    python manage.py shell
    from automacoes.atribui_municipios import *
    >>> cadastrar_municipios_por_estado_ibge()           # cadastra todos os estados já existentes na base
    >>> cadastrar_municipios_por_estado_ibge(['SP','RJ']) # cadastra apenas estados específicos
"""

import time
import requests
from django.db import transaction
from sistema_justica.models import Estado, Municipio

IBGE_MUNICIPIOS_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/{sigla}/municipios"
REQUEST_TIMEOUT = 15  # segundos
MAX_RETRIES = 3
SLEEP_BETWEEN_RETRIES = 1.5  # segundos


def _buscar_municipios_ibge(sigla_estado: str):
    """
    Consulta a API do IBGE e retorna a lista de municípios para a sigla informada.
    """
    url = IBGE_MUNICIPIOS_URL.format(sigla=sigla_estado)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"Falha ao consultar IBGE para {sigla_estado}: {exc}") from exc
            time.sleep(SLEEP_BETWEEN_RETRIES)


def cadastrar_municipios_por_estado_ibge(siglas=None):
    """
    Para cada estado cadastrado na tabela Estado, busca os municípios na API do IBGE
    e cadastra aqueles que ainda não existem. Também preenche o código IBGE quando faltante.

    Parâmetros:
        siglas (list[str] | None): lista opcional de siglas a processar. Se None, processa todos os estados.
    """
    qs_estados = Estado.objects.all().order_by("sigla")
    if siglas:
        qs_estados = qs_estados.filter(sigla__in=siglas)

    if not qs_estados.exists():
        print("❌ Nenhum estado encontrado para processar.")
        return

    print("Iniciando cadastro de municípios via IBGE...")
    total_cadastrados = 0
    total_atualizados = 0
    total_existentes = 0

    for estado in qs_estados:
        print(f"\nProcessando estado: {estado.nome} ({estado.sigla})")
        try:
            dados_municipios = _buscar_municipios_ibge(estado.sigla)
        except Exception as exc:
            print(f"❌ Erro ao buscar municípios de {estado.sigla}: {exc}")
            continue

        with transaction.atomic():
            for dado in dados_municipios:
                nome = dado.get("nome")
                codigo_ibge = dado.get("id")

                if not nome or not codigo_ibge:
                    print(f"  ⚠️ Registro inválido retornado pelo IBGE: {dado}")
                    continue

                obj, created = Municipio.objects.get_or_create(
                    nome=nome,
                    estado=estado,
                    defaults={"codigo_ibge": codigo_ibge},
                )

                if created:
                    total_cadastrados += 1
                    print(f"  ✓ Cadastrado: {nome} (IBGE {codigo_ibge})")
                else:
                    if obj.codigo_ibge != codigo_ibge:
                        obj.codigo_ibge = codigo_ibge
                        obj.save(update_fields=["codigo_ibge"])
                        total_atualizados += 1
                        print(f"  ↻ Atualizado código IBGE: {nome} -> {codigo_ibge}")
                    else:
                        total_existentes += 1
                        print(f"  - Já existente: {nome}")

    print("\n📊 Resumo:")
    print(f"   Municípios cadastrados: {total_cadastrados}")
    print(f"   Municípios com IBGE atualizado: {total_atualizados}")
    print(f"   Municípios já existentes (sem mudança): {total_existentes}")
    print(f"   Total processado: {total_cadastrados + total_atualizados + total_existentes}")
    print("✅ Processo finalizado!")


def verificar_estados_cadastrados():
    """
    Verifica quais estados estão cadastrados no banco de dados.
    """
    print("Estados cadastrados no banco de dados:")
    estados = Estado.objects.all().order_by("sigla")

    if not estados:
        print("❌ Nenhum estado encontrado no banco de dados!")
        return

    for estado in estados:
        count_municipios = Municipio.objects.filter(estado=estado).count()
        print(f"  {estado.sigla} - {estado.nome} ({count_municipios} municípios)")

    print(f"\nTotal de estados cadastrados: {estados.count()}")


if __name__ == "__main__":
    print("Script para cadastro de municípios por estado via IBGE")
    print("=" * 60)
