# -*- coding: utf-8 -*-
"""
Script para criar os tipos de violência no banco de dados.

Baseado na Lei Maria da Penha (Lei 11.340/2006).

@autor: ogliari
@comando:
  python manage.py shell
  from automacoes.cria_tipos_violencia import criar_tipos_violencia
  >>> criar_tipos_violencia()
"""

from sistema_justica.models import TipoDeViolencia


def criar_tipos_violencia():
    """
    Cria os tipos de violência conforme Lei Maria da Penha.
    """
    tipos_violencia = [
        (
            "Física",
            "Entendida como qualquer conduta que ofenda a integridade ou saúde corporal da mulher."
        ),
        (
            "Moral",
            "É considerada qualquer conduta que configure calúnia, difamação ou injúria."
        ),
        (
            "Patrimonial",
            "Entendida como qualquer conduta que configure retenção, subtração, destruição parcial ou total de seus objetos, instrumentos de trabalho, documentos pessoais, bens, valores e direitos ou recursos econômicos, incluindo os destinados a satisfazer suas necessidades."
        ),
        (
            "Psicológica",
            "É considerada qualquer conduta que: cause dano emocional e diminuição da autoestima; prejudique e perturbe o pleno desenvolvimento da mulher; ou vise degradar ou controlar suas ações, comportamentos, crenças e decisões."
        ),
        (
            "Sexual",
            "Trata-se de qualquer conduta que constranja a presenciar, a manter ou a participar de relação sexual não desejada mediante intimidação, ameaça, coação ou uso da força."
        ),
        (
            "Vicária",
            "Na violência vicária, o agressor atinge filhos ou pessoas próximas da mulher com o objetivo de causar sofrimento, punição ou controle sobre ela."
        )
    ]

    for nome, descricao in tipos_violencia:
        tipo, created = TipoDeViolencia.objects.get_or_create(
            nome=nome,
            defaults={'descricao': descricao, 'ativo': True}
        )
        if created:
            print(f"Tipo de Violência Criado: {nome}")
        else:
            print(f"Tipo de Violência Já Existente: {nome}")